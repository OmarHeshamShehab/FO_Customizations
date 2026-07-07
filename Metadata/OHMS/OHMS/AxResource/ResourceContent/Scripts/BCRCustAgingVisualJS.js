//==============================================================================
// FILE: BCRCustAgingVisual.js
//------------------------------------------------------------------------------
// HANDOVER SUMMARY (read before changing anything)
//
// PURPOSE
//   Client-side F&O visual control for the "Customer Aging with Bank" form.
//   It receives one JSON string (self.AgingData) built by the X++ engine
//   (BCRCustAgingVisualEngine.getDataJson) and renders four sections:
//     1. Run-info banner (as-of date + customer selection)   -> renderRunInfo
//     2. Bank section (table, bars, currency pills, donut)   -> renderBank
//     3. Customer aging tree table (collapsible)             -> render
//     4. Management overview (KPIs, bars, watchlist)         -> renderMgmt
//
// DATA CONTRACT (must match the engine's JSON exactly)
//   d.customers[]      : {classification,country,channel,invoiceAccount,custAccount,
//                         custName,custGroup,terms,dso,total,balanceDue,
//                         notDue,d30,d60,d90,d180}
//   d.banks[]          : {bank,accountId,balance,valueSar,currency,rate}
//   d.currencyTotals[] : {currency,total}
//   d.grandTotalSar, d.asOfDate, d.customerSelection
//
// TREE HIERARCHY (4 collapsible levels, then customer leaf rows)
//   Classification -> Country -> Channel -> Invoice Account -> customer rows.
//   Open/closed state per level is held in openClass/openCountry/openChannel/
//   openInvoiceAcct and reset on every data reload (renderAll).
//
// NUMBER FORMATTING
//   fmt2 -> 2 decimals for all money/amount values.
//   fmt7 -> 7 decimals, used ONLY for the DSO value. DSO is a small fraction
//           under the current formula, so 2 dp would round it to 0. The X++ side
//           (r2s7) must emit the same 7 decimals or the value is truncated before
//           it ever reaches here.
//
// STYLING NOTE
//   F&O namespaces external CSS class names at runtime, so ALL styling here is
//   inline. Do not rely on an external .css file.
//==============================================================================
(function () {
    'use strict';

    // Aging bucket coloring (severity ramp) used to tint the customer table columns.
    var BUCKETS = [
        { key: 'notDue', label: 'Balance Not Due', head: '#1F8A70', cell: '#E6F2EC' },
        { key: 'd30', label: '30 D', head: '#E6B325', cell: '#FBF3D6' },
        { key: 'd60', label: '60 D', head: '#E0871E', cell: '#FBEBD6' },
        { key: 'd90', label: '61-90', head: '#CB5C2E', cell: '#F7E0D6' },
        { key: 'd180', label: '180 DAnd Over', head: '#A62B2B', cell: '#F4DADA' }
    ];

    // Management-section bucket palette. Spread across distinct hues so adjacent
    // buckets are easy to tell apart (teal / amber / orange / purple / red).
    var MBUCKETS = [
        { key: 'notDue', label: 'Not due', color: '#1F8A70' },   // teal-green
        { key: 'd30', label: '30 days', color: '#F2C014' },   // amber
        { key: 'd60', label: '60 days', color: '#E87722' },   // orange
        { key: 'd90', label: '90 days', color: '#8E44AD' },   // purple
        { key: 'd180', label: '180+ days', color: '#C0392B' }    // red
    ];

    $dyn.ui.defaults.BCRCustAgingVisual = {};

    $dyn.controls.BCRCustAgingVisual = function (data, element) {
        var self = this;
        $dyn.ui.Control.apply(self, arguments);
        $dyn.ui.applyDefaults(self, data, $dyn.ui.defaults.BCRCustAgingVisual);

        var $root = $(element);
        var treeEl = $root.find('.bcrcav-tree')[0];
        var emptyEl = $root.find('.bcrcav-empty')[0];
        var bankTableEl = $root.find('.bcrcav-bank-table')[0];
        var bankChartEl = $root.find('.bcrcav-bank-chart')[0];
        var curEl = $root.find('.bcrcav-curtotals')[0];
        var curChartEl = $root.find('.bcrcav-cur-chart')[0];
        var grandEl = $root.find('.bcrcav-grand')[0];
        var runInfoEl = $root.find('.bcrcav-runinfo')[0];

        $root[0].style.cssText = 'display:block;width:100%';

        // Money/amount formatter: 2 decimals.
        var fmt2 = function (n) { return (n || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }); };
        // DSO formatter: 7 decimals. DSO is a small fraction under the current formula,
        // so fewer decimals would round it to 0. MUST match the engine's r2s7 precision.
        var fmt7 = function (n) { return (n || 0).toLocaleString(undefined, { minimumFractionDigits: 7, maximumFractionDigits: 7 }); };

        // ---------- Run-info (top-right): as-of date + customer selection ----------
        function renderRunInfo(d) {
            if (!runInfoEl) { return; }
            var dateLine = 'This report is run as of date ' + (d.asOfDate || '');
            var custLine = d.customerSelection || 'All customers selected';
            runInfoEl.innerHTML =
                '<div style="background:#FFF9C4;border:1px solid #E6D77A;border-radius:4px;padding:6px 10px;' +
                'font:600 12px Segoe UI;color:#5B4E00;text-align:right;max-width:520px;">' +
                '<div>' + dateLine + '</div>' +
                '<div style="font-weight:400;margin-top:2px;">' + custLine + '</div>' +
                '</div>';
        }

        // ---------- SVG donut helpers ----------
        function polar(cx, cy, r, angleDeg) {
            var a = (angleDeg - 90) * Math.PI / 180;
            return { x: cx + r * Math.cos(a), y: cy + r * Math.sin(a) };
        }
        function donutSlice(cx, cy, rO, rI, a0, a1, color) {
            var large = (a1 - a0) > 180 ? 1 : 0;
            var oS = polar(cx, cy, rO, a0);
            var oE = polar(cx, cy, rO, a1);
            var iE = polar(cx, cy, rI, a1);
            var iS = polar(cx, cy, rI, a0);
            var d = 'M ' + oS.x + ' ' + oS.y +
                ' A ' + rO + ' ' + rO + ' 0 ' + large + ' 1 ' + oE.x + ' ' + oE.y +
                ' L ' + iE.x + ' ' + iE.y +
                ' A ' + rI + ' ' + rI + ' 0 ' + large + ' 0 ' + iS.x + ' ' + iS.y +
                ' Z';
            return '<path d="' + d + '" fill="' + color + '" stroke="#fff" stroke-width="1.5"></path>';
        }
        // Generic donut renderer. items: [{label, value, color}].
        function renderDonut(el, items, title, unit) {
            if (!el) { return; }
            var total = 0;
            items.forEach(function (it) { total += (+it.value || 0); });
            if (!items.length || total <= 0) { el.innerHTML = ''; return; }

            var cx = 85, cy = 85, rO = 78, rI = 48, slices = '';
            if (items.length === 1) {
                slices = '<circle cx="' + cx + '" cy="' + cy + '" r="' + rO + '" fill="' + items[0].color + '"></circle>' +
                    '<circle cx="' + cx + '" cy="' + cy + '" r="' + rI + '" fill="#fff"></circle>';
            } else {
                var a = 0;
                items.forEach(function (it) {
                    var a1 = a + ((+it.value || 0) / total) * 360;
                    slices += donutSlice(cx, cy, rO, rI, a, a1, it.color);
                    a = a1;
                });
            }

            var legend = '';
            items.forEach(function (it) {
                var pct = ((+it.value || 0) / total) * 100;
                legend += '<div style="display:flex;align-items:center;gap:8px;margin:3px 0;font:12px Segoe UI;">' +
                    '<span style="width:12px;height:12px;border-radius:2px;background:' + it.color + ';display:inline-block;flex:0 0 auto;"></span>' +
                    '<b style="min-width:60px;">' + it.label + '</b>' +
                    '<span style="font-variant-numeric:tabular-nums;">' + fmt2(it.value) + ' ' + unit + '</span>' +
                    '<span style="color:#667;">(' + pct.toFixed(2) + '%)</span>' +
                    '</div>';
            });

            el.style.cssText = 'display:flex;align-items:center;gap:28px;flex-wrap:wrap;margin-top:16px;';
            el.innerHTML =
                '<svg width="170" height="170" viewBox="0 0 170 170" role="img" aria-label="' + title + '">' + slices +
                '<text x="' + cx + '" y="' + (cy - 4) + '" text-anchor="middle" style="font:600 11px Segoe UI;fill:#5a6b7b;">Total ' + unit + '</text>' +
                '<text x="' + cx + '" y="' + (cy + 13) + '" text-anchor="middle" style="font:700 12px Segoe UI;fill:#1B1B1B;">' + fmt2(total) + '</text>' +
                '</svg>' +
                '<div><div style="font:600 13px Segoe UI;color:#1B1B1B;margin-bottom:6px;">' + title + '</div>' + legend + '</div>';
        }

        // ---------- Horizontal bar chart. items: [{label, value, color, labelBg}], pre-sorted ----------
        function renderBars(el, items, title, unit) {
            if (!el) { return; }
            if (!items.length) { el.innerHTML = ''; return; }
            var max = 0, total = 0;
            items.forEach(function (it) { var v = +it.value || 0; if (v > max) { max = v; } total += v; });
            if (max <= 0) { el.innerHTML = ''; return; }

            var TRACK = 280; // fixed px width of the bar track so it never collapses
            var bars = items.map(function (it) {
                var v = +it.value || 0;
                var w = Math.max(Math.round((v / max) * TRACK), 2);
                var pct = total > 0 ? (v / total) * 100 : 0;
                return '<div style="display:flex;align-items:center;gap:10px;margin:4px 0;font:12px Segoe UI;">' +
                    '<div style="flex:0 0 200px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;background:' + (it.labelBg || 'transparent') + ';padding:2px 6px;border-radius:3px;" title="' + it.label + '">' + it.label + '</div>' +
                    '<div style="flex:0 0 ' + TRACK + 'px;background:#EEF2F6;border-radius:3px;height:16px;">' +
                    '<div style="width:' + w + 'px;height:100%;background:' + it.color + ';border-radius:3px;"></div>' +
                    '</div>' +
                    '<div style="flex:0 0 auto;text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap;">' +
                    fmt2(v) + ' ' + unit + ' <span style="color:#667;">(' + pct.toFixed(2) + '%)</span>' +
                    '</div>' +
                    '</div>';
            }).join('');

            el.style.cssText = 'margin-top:16px;';
            el.innerHTML =
                '<div style="font:600 13px Segoe UI;color:#1B1B1B;margin-bottom:8px;">' + title + '</div>' +
                '<div style="font:600 11px Segoe UI;color:#5a6b7b;margin-bottom:6px;">Total ' + unit + ': ' + fmt2(total) + '</div>' +
                bars;
        }

        // ---------- Bank section ----------
        function renderBank(d) {
            var banks = d.banks || [];

            // Shared currency hue map (banks + currency totals) for consistent coloring.
            var curHues = {};
            var curList = [];
            function regCur(code) {
                if (code && curHues[code] === undefined) { curHues[code] = null; curList.push(code); }
            }
            banks.forEach(function (b) { regCur(b.currency); });
            (d.currencyTotals || []).forEach(function (c) { regCur(c.currency); });
            curList.sort();
            curList.forEach(function (k, i) { curHues[k] = Math.round((360 / curList.length) * i); });

            var curBg = function (code) { var h = curHues[code]; return (h == null) ? '#FFFFFF' : 'hsl(' + h + ',45%,93%)'; };
            var curPill = function (code) { var h = curHues[code]; return (h == null) ? { bg: '#F3F5F7', fg: '#1B1B1B' } : { bg: 'hsl(' + h + ',55%,92%)', fg: 'hsl(' + h + ',60%,28%)' }; };
            var curSolid = function (code) { var h = curHues[code]; return (h == null) ? '#9AA6B2' : 'hsl(' + h + ',55%,55%)'; };

            // ----- Bank table -----
            if (bankTableEl) {
                if (!banks.length) {
                    bankTableEl.innerHTML = '';
                } else {
                    var head = ['Bank Account Id', 'Bank Name', 'Currency Code', 'Value In Currency', 'Value In SAR', 'Todays EX Rate'];
                    var ths = head.map(function (h, i) {
                        var align = i >= 3 ? 'right' : 'left';
                        return '<th style="padding:5px 8px;text-align:' + align + ';white-space:nowrap;font:600 12px Segoe UI;' +
                            'background:#DCE7F2;color:#1B1B1B;border-bottom:1px solid #cfd6dd;">' + h + '</th>';
                    }).join('');

                    var rows = banks.map(function (b) {
                        var bg = curBg(b.currency);
                        var txt = 'padding:4px 8px;font:12px Segoe UI;border-bottom:1px solid #eef0f2;background:' + bg + ';';
                        var num = 'padding:4px 8px;text-align:right;font:12px Segoe UI;font-variant-numeric:tabular-nums;border-bottom:1px solid #eef0f2;background:' + bg + ';';
                        return '<tr>' +
                            '<td style="' + txt + '">' + (b.accountId || '') + '</td>' +
                            '<td style="' + txt + '">' + (b.bank || '') + '</td>' +
                            '<td style="' + txt + '">' + (b.currency || '') + '</td>' +
                            '<td style="' + num + '">' + fmt2(b.balance) + '</td>' +
                            '<td style="' + num + '">' + fmt2(b.valueSar) + '</td>' +
                            '<td style="' + num + '">' + fmt2(b.rate) + '</td>' +
                            '</tr>';
                    }).join('');

                    bankTableEl.innerHTML =
                        '<table style="border-collapse:collapse;width:100%;min-width:0;margin-top:8px;">' +
                        '<thead><tr>' + ths + '</tr></thead><tbody>' + rows + '</tbody></table>';
                    bankTableEl.style.cssText = 'overflow-x:auto;';
                }
            }

            // ----- Bank horizontal bars (sorted by Value In SAR, colored & labeled by currency) -----
            var bankItems = banks
                .filter(function (b) { return (+b.valueSar || 0) > 0; })
                .map(function (b) {
                    return { label: b.bank, value: +b.valueSar || 0, color: curSolid(b.currency), labelBg: curBg(b.currency) };
                })
                .sort(function (a, b) { return b.value - a.value; });
            renderBars(bankChartEl, bankItems, 'Cash by bank (Value In SAR)', 'SAR');

            // ----- Currency pills (colored by currency) -----
            if (curEl) {
                curEl.style.cssText = 'display:flex;flex-wrap:wrap;gap:10px;margin-top:12px;';
                curEl.innerHTML = (d.currencyTotals || []).map(function (c) {
                    var col = curPill(c.currency);
                    return '<span style="font:12px Segoe UI;background:' + col.bg + ';color:' + col.fg + ';' +
                        'border:1px solid ' + col.fg + ';border-radius:12px;padding:4px 12px;">' +
                        '<b>' + c.currency + '</b> ' + fmt2(c.total) + '</span>';
                }).join('');
            }

            // ----- Currency donut (SAR equivalent, from bank rows) -----
            var curMap = {}, curOrder = [];
            banks.forEach(function (b) {
                var k = b.currency || '(blank)';
                if (curMap[k] === undefined) { curMap[k] = 0; curOrder.push(k); }
                curMap[k] += (+b.valueSar || 0);
            });
            var curItems = curOrder.map(function (k) {
                return { label: k, value: curMap[k], color: curSolid(k) };
            });
            renderDonut(curChartEl, curItems, 'Cash distribution by currency (SAR equivalent)', 'SAR');

            // ----- Grand total -----
            if (grandEl) {
                grandEl.textContent = 'Total Cash as of today in SAR: ' + fmt2(d.grandTotalSar);
                grandEl.style.cssText = 'margin-top:12px;padding:6px 10px;display:inline-block;border-radius:4px;' +
                    'background:#1F8A70;color:#fff;font:600 13px Segoe UI;font-variant-numeric:tabular-nums;';
            }
        }

        // ---------- Customer aging tree table ----------
        // 4 collapsible levels + leaf rows. Open/closed state per level below;
        // all four are reset in renderAll() whenever new data arrives.
        var customers = [];
        var openClass = {};     // classification -> bool
        var openCountry = {};   // classification|country -> bool
        var openChannel = {};   // classification|country|channel -> bool
        var openInvoiceAcct = {}; // classification|country|channel|invoiceAccount -> bool

        var COLS = ['Classification', 'Country', 'Channel', 'Invoice Account', 'Cust Account', 'Cust Name', 'Cust Group', 'DSO', 'Terms of payment',
            'Total', 'Balance Due', 'Balance Not Due', '30 D', '60 D', '90 D', '180 DAnd Over'];

        function uniqueOrdered(arr, keyFn) {
            var seen = {}, out = [];
            arr.forEach(function (x) { var k = keyFn(x); if (!(k in seen)) { seen[k] = 1; out.push(k); } });
            return out;
        }

        function headerRow() {
            var th = COLS.map(function (c) {
                var b2 = ({ 'Balance Not Due': 0, '30 D': 1, '60 D': 2, '90 D': 3, '180 DAnd Over': 4 })[c];
                var style = 'padding:5px 8px;text-align:' + (['Total', 'Balance Due', 'Balance Not Due', '30 D', '60 D', '90 D', '180 DAnd Over'].indexOf(c) >= 0 ? 'right' : 'left') + ';white-space:nowrap;font:600 12px Segoe UI;border-bottom:1px solid #cfd6dd;';
                if (b2 !== undefined) { style += 'background:' + BUCKETS[b2].head + ';color:#fff;'; }
                else { style += 'background:#EEF2F6;color:#1B1B1B;'; }
                return '<th style="' + style + '">' + c + '</th>';
            }).join('');
            return '<tr>' + th + '</tr>';
        }

        function tintCell(bucketIdx, val) {
            return '<td style="padding:4px 8px;text-align:right;font:12px Segoe UI;font-variant-numeric:tabular-nums;' +
                'background:' + BUCKETS[bucketIdx].cell + ';border-bottom:1px solid #eef0f2">' + fmt2(val) + '</td>';
        }
        function numCell(val) {
            return '<td style="padding:4px 8px;text-align:right;font:12px Segoe UI;font-variant-numeric:tabular-nums;border-bottom:1px solid #eef0f2">' + fmt2(val) + '</td>';
        }
        // DSO cell: same styling as numCell, but 7 decimals (uses fmt7).
        function dsoCell(val) {
            return '<td style="padding:4px 8px;text-align:right;font:12px Segoe UI;font-variant-numeric:tabular-nums;border-bottom:1px solid #eef0f2">' + fmt7(val) + '</td>';
        }
        function txtCell(val, extra) {
            return '<td style="padding:4px 8px;font:12px Segoe UI;border-bottom:1px solid #eef0f2;' + (extra || '') + '">' + (val || '') + '</td>';
        }
        function toggleCell(open, label, pad) {
            var sign = open ? '\u2212' : '+';
            return '<td style="padding:4px 8px;font:600 12px Segoe UI;border-bottom:1px solid #eef0f2;padding-left:' + pad + 'px">' +
                '<span class="tg" style="display:inline-block;width:16px;cursor:pointer;color:#3A6EA5">' + sign + '</span>' + label + '</td>';
        }
        function blankCells(n) {
            var s = ''; for (var i = 0; i < n; i++) { s += '<td style="border-bottom:1px solid #eef0f2"></td>'; }
            return s;
        }

        // ---------- Group subtotals (Total .. 180 DAnd Over) ----------
        function sumGroup(rows) {
            var s = { total: 0, balanceDue: 0, notDue: 0, d30: 0, d60: 0, d90: 0, d180: 0 };
            rows.forEach(function (r) {
                s.total += (+r.total || 0);
                s.balanceDue += (+r.balanceDue || 0);
                s.notDue += (+r.notDue || 0);
                s.d30 += (+r.d30 || 0);
                s.d60 += (+r.d60 || 0);
                s.d90 += (+r.d90 || 0);
                s.d180 += (+r.d180 || 0);
            });
            return s;
        }
        function sumCell(val) {
            return '<td style="padding:4px 8px;text-align:right;font:600 12px Segoe UI;font-variant-numeric:tabular-nums;border-bottom:1px solid #eef0f2">' + fmt2(val) + '</td>';
        }
        function sumCells(s) {
            return sumCell(s.total) + sumCell(s.balanceDue) + sumCell(s.notDue) +
                sumCell(s.d30) + sumCell(s.d60) + sumCell(s.d90) + sumCell(s.d180);
        }
        // Returns true if every total column in the group is zero.
        function isZeroGroup(s) {
            return !s.total && !s.balanceDue && !s.notDue && !s.d30 && !s.d60 && !s.d90 && !s.d180;
        }

        // render: draws the collapsible aging tree. Groups are hidden when every
        // amount column is zero; customer leaf rows with zero Total are hidden too.
        function render() {
            var has = customers.length > 0;
            if (emptyEl) emptyEl.hidden = has;
            if (!has) { treeEl.innerHTML = ''; return; }

            var html = '<table style="border-collapse:collapse;width:100%;min-width:1180px">' +
                '<thead>' + headerRow() + '</thead><tbody>';

            var classes = uniqueOrdered(customers, function (r) { return r.classification || '(blank)'; });
            classes.forEach(function (classification) {
                var clOpen = !!openClass[classification];
                var inClass = customers.filter(function (r) { return (r.classification || '(blank)') === classification; });

                // Skip the whole group if every total column is zero
                var gs = sumGroup(inClass);
                if (isZeroGroup(gs)) { return; }

                html += '<tr data-class="' + classification + '" style="background:#C9D9EC">' +
                    toggleCell(clOpen, '<b>' + classification + '</b>', 4) +
                    blankCells(8) + sumCells(gs) + '</tr>';
                if (!clOpen) { return; }

                var countries = uniqueOrdered(inClass, function (r) { return r.country || '(blank)'; });
                countries.forEach(function (country) {
                    var coKey = classification + '|' + country;
                    var coOpen = !!openCountry[coKey];
                    var inCountry = inClass.filter(function (r) { return (r.country || '(blank)') === country; });
                    html += '<tr data-country="' + coKey + '" style="background:#DCE7F2">' +
                        '<td style="border-bottom:1px solid #eef0f2"></td>' +
                        toggleCell(coOpen, '<b>' + country + '</b>', 16) +
                        blankCells(7) + sumCells(sumGroup(inCountry)) + '</tr>';
                    if (!coOpen) { return; }

                    var channels = uniqueOrdered(inCountry, function (r) { return r.channel || '(blank)'; });
                    channels.forEach(function (channel) {
                        var chKey = classification + '|' + country + '|' + channel;
                        var chOpen = !!openChannel[chKey];
                        var rows = inCountry.filter(function (r) { return (r.channel || '(blank)') === channel; });
                        // Hide the channel entirely if all amount columns are zero
                        if (isZeroGroup(sumGroup(rows))) { return; }
                        html += '<tr data-channel="' + chKey + '" style="background:#EAF0F6">' +
                            '<td style="border-bottom:1px solid #eef0f2"></td>' +
                            '<td style="border-bottom:1px solid #eef0f2"></td>' +
                            toggleCell(chOpen, channel, 28) +
                            blankCells(6) + sumCells(sumGroup(rows)) + '</tr>';
                        if (!chOpen) { return; }

                        // Invoice Account level (4th collapsible level), bg #F2F5F9, 40px indent.
                        var invoiceAccts = uniqueOrdered(rows, function (r) { return r.invoiceAccount || '(blank)'; });
                        invoiceAccts.forEach(function (invAcct) {
                            var invKey = classification + '|' + country + '|' + channel + '|' + invAcct;
                            var invOpen = !!openInvoiceAcct[invKey];
                            var invRows = rows.filter(function (r) { return (r.invoiceAccount || '(blank)') === invAcct; });
                            // Hide the invoice account entirely if all amount columns are zero
                            if (isZeroGroup(sumGroup(invRows))) { return; }
                            html += '<tr data-invoice="' + invKey + '" style="background:#F2F5F9">' +
                                '<td style="border-bottom:1px solid #eef0f2"></td>' +
                                '<td style="border-bottom:1px solid #eef0f2"></td>' +
                                '<td style="border-bottom:1px solid #eef0f2"></td>' +
                                toggleCell(invOpen, invAcct, 40) +
                                blankCells(5) + sumCells(sumGroup(invRows)) + '</tr>';
                            if (!invOpen) { return; }

                            // Customer leaf rows. DSO uses dsoCell (7 dp); money uses numCell (2 dp).
                            invRows.forEach(function (r) {
                                if ((+r.total || 0) === 0) { return; }   // hide customers with zero Total; group header stays
                                html += '<tr>' +
                                    '<td style="border-bottom:1px solid #eef0f2"></td>' +
                                    '<td style="border-bottom:1px solid #eef0f2"></td>' +
                                    '<td style="border-bottom:1px solid #eef0f2"></td>' +
                                    '<td style="border-bottom:1px solid #eef0f2"></td>' +
                                    txtCell(r.custAccount) +
                                    txtCell(r.custName) +
                                    txtCell(r.custGroup) +
                                    dsoCell(r.dso) +              /* DSO value (7 dp) */
                                    txtCell(r.terms) +
                                    numCell(r.total) +
                                    numCell(r.balanceDue) +
                                    tintCell(0, r.notDue) +
                                    tintCell(1, r.d30) +
                                    tintCell(2, r.d60) +
                                    tintCell(3, r.d90) +
                                    tintCell(4, r.d180) +
                                    '</tr>';
                            });
                        });
                    });
                });
            });

            html += '</tbody></table>';
            treeEl.innerHTML = html;
            treeEl.style.cssText = 'overflow-x:auto;margin-top:8px';

            // One delegated toggle handler per level. stopPropagation on the deeper
            // levels so a click doesn't also toggle the parent row.
            Array.prototype.forEach.call(treeEl.querySelectorAll('tr[data-class]'), function (tr) {
                tr.addEventListener('click', function () {
                    var k = tr.getAttribute('data-class');
                    openClass[k] = !openClass[k];
                    render();
                });
            });
            Array.prototype.forEach.call(treeEl.querySelectorAll('tr[data-country]'), function (tr) {
                tr.addEventListener('click', function (ev) {
                    ev.stopPropagation();
                    var k = tr.getAttribute('data-country');
                    openCountry[k] = !openCountry[k];
                    render();
                });
            });
            Array.prototype.forEach.call(treeEl.querySelectorAll('tr[data-channel]'), function (tr) {
                tr.addEventListener('click', function (ev) {
                    ev.stopPropagation();
                    var k = tr.getAttribute('data-channel');
                    openChannel[k] = !openChannel[k];
                    render();
                });
            });
            Array.prototype.forEach.call(treeEl.querySelectorAll('tr[data-invoice]'), function (tr) {
                tr.addEventListener('click', function (ev) {
                    ev.stopPropagation();
                    var k = tr.getAttribute('data-invoice');
                    openInvoiceAcct[k] = !openInvoiceAcct[k];
                    render();
                });
            });
        }
        // ---------- Management overview: charts/bars below the table ----------
        // F&O namespaces external CSS class names at runtime, so all styling here is
        // INLINE (same approach as the table/bank). No dependency on the .css file.
        // All values come from d.customers (already retrieved). No new formulas.
        var mgmtOpenClass = {};                 // classification -> expanded?
        var mgmtOpenCountry = {};               // classification|country -> expanded?
        var mgmtWatchSort = { key: 'd180', dir: 'desc' };  // watchlist sort state

        function renderMgmt(d) {
            var el = $root.find('.bcrcav-mgmt')[0];
            if (!el) {
                el = document.createElement('div');
                el.className = 'bcrcav-mgmt';
                if (emptyEl && emptyEl.parentNode) {
                    emptyEl.parentNode.insertBefore(el, emptyEl.nextSibling);
                } else if (treeEl && treeEl.parentNode) {
                    treeEl.parentNode.insertBefore(el, treeEl.nextSibling);
                } else {
                    $root[0].appendChild(el);
                }
            }

            var rows = d.customers || [];
            if (!rows.length) { el.innerHTML = ''; return; }

            function clamp0(v) { v = +v || 0; return v > 0 ? v : 0; }
            function escAttr(s) { return ('' + (s == null ? '' : s)).replace(/"/g, '&quot;'); }

            // Traffic-light color for a DSO value (green<=30, amber<=60, red>60 or invalid).
            function dsoColor(v) {
                var dv = +v;
                if (!isFinite(dv) || dv < 0 || dv > 1000) { return '#A62B2B'; } // abnormal -> red
                if (dv <= 30) { return '#1F8A70'; }
                if (dv <= 60) { return '#E0871E'; }
                return '#A62B2B';
            }

            // Inline style constants
            var S_BLOCK = 'background:#FFFFFF;border:1px solid #E6E9ED;border-radius:8px;padding:16px 18px;';
            var S_BTITLE = 'font:600 14px Segoe UI;color:#1B1B1B;margin:0 0 4px;';
            var S_BSUB = 'font:400 12px Segoe UI;color:#6A737D;margin:0 0 14px;line-height:1.5;';

            // KPI card with an optional left accent color (used for aging buckets).
            function kpiCard(label, value, accent) {
                var bar = accent ? 'border-left:4px solid ' + accent + ';' : 'border-left:4px solid transparent;';
                var valColor = accent ? accent : '#1B1B1B';
                return '<div style="background:#F7F9FB;border:1px solid #ECEFF2;border-radius:8px;padding:12px 14px;' + bar + '">' +
                    '<div style="font:400 12px Segoe UI;color:#6A737D;margin-bottom:6px;">' + label + '</div>' +
                    '<div style="font:600 20px Segoe UI;color:' + valColor + ';font-variant-numeric:tabular-nums;">' + value + '</div>' +
                    '</div>';
            }
            function seg(color, widthPct, label, value, pct) {
                return '<span class="bcrcav-seg" style="display:block;height:100%;width:' + widthPct + '%;background:' + color + ';" ' +
                    'data-label="' + escAttr(label) + '" data-value="' + fmt2(value) + '" data-pct="' + pct.toFixed(1) + '"></span>';
            }

            // ----- Portfolio totals (all from existing fields) -----
            var g = sumGroup(rows);
            var overdue = g.d30 + g.d60 + g.d90 + g.d180;
            var pctOverdue = g.total ? (overdue / g.total) * 100 : 0;
            var pct180 = g.total ? (g.d180 / g.total) * 100 : 0;

            var html = '';
            html += '<div style="font:600 16px Segoe UI;color:#1B1B1B;margin:0 0 4px;">Management overview</div>';

            // ----- Headline takeaway (uses only g.d180, g.total) -----
            html += '<div style="background:#FBF6E9;border:1px solid #E6D77A;border-left:4px solid #A62B2B;' +
                'border-radius:6px;padding:10px 14px;font:600 13px Segoe UI;color:#5B4E00;">' +
                fmt2(g.d180) + ' SAR (' + pct180.toFixed(1) + '% of total receivables) is past 180 days. ' +
                'Overdue overall: ' + pctOverdue.toFixed(1) + '%.' +
                '</div>';

            // ----- KPI strip: total + each aging bucket (colours match the bars below) -----
            html += '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:12px;">' +
                kpiCard('Total receivables', fmt2(g.total) + ' SAR', '#2E5A88') +
                kpiCard('Not due', fmt2(g.notDue) + ' SAR', MBUCKETS[0].color) +
                kpiCard('30 days', fmt2(g.d30) + ' SAR', MBUCKETS[1].color) +
                kpiCard('60 days', fmt2(g.d60) + ' SAR', MBUCKETS[2].color) +
                kpiCard('90 days', fmt2(g.d90) + ' SAR', MBUCKETS[3].color) +
                kpiCard('180+ days', fmt2(g.d180) + ' SAR', MBUCKETS[4].color) +
                '</div>';

            // ----- Receivables by aging bucket (separate horizontal bars, one per bucket) -----
            // Each bar's length is scaled to the largest POSITIVE bucket so big buckets don't
            // crush the small ones. Negative buckets (credits) show a small red marker on the
            // left and a "(credit)" note so they read as intentional, not missing.
            var bucketMaxPos = MBUCKETS.reduce(function (m, b) { var v = clamp0(g[b.key]); return v > m ? v : m; }, 0);
            var bucketBars = MBUCKETS.map(function (b) {
                var val = g[b.key];
                var isNeg = (+val || 0) < 0;
                var w = bucketMaxPos > 0 ? (clamp0(val) / bucketMaxPos * 100) : 0;
                var pct = g.total ? (val / g.total * 100) : 0;
                var fill = isNeg
                    ? '<div style="width:8px;height:100%;background:#C0392B;border-radius:4px 0 0 4px;"></div>'
                    : '<div style="width:' + w + '%;height:100%;background:' + b.color + ';border-radius:4px;min-width:2px;"></div>';
                var amtColor = isNeg ? '#C0392B' : '#1B1B1B';
                var note = isNeg ? ' <span style="color:#C0392B;font-weight:600;">(credit)</span>' : '';
                return '<div style="display:flex;align-items:center;gap:10px;margin:7px 0;font:12px Segoe UI;">' +
                    '<div style="flex:0 0 96px;display:flex;align-items:center;gap:7px;color:#4A4A4A;">' +
                    '<i style="width:11px;height:11px;border-radius:2px;display:inline-block;flex:0 0 auto;background:' + b.color + ';"></i>' +
                    '<span style="white-space:nowrap;">' + b.label + '</span></div>' +
                    '<div style="flex:1 1 auto;min-width:60px;background:#EEF2F6;border-radius:4px;height:18px;position:relative;overflow:hidden;">' +
                    fill +
                    '</div>' +
                    '<div style="flex:0 0 210px;text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums;">' +
                    '<b style="color:' + amtColor + ';">' + fmt2(val) + '</b> ' +
                    '<span style="color:#667;">(' + pct.toFixed(1) + '%)</span>' + note + '</div>' +
                    '</div>';
            }).join('');
            html += '<div style="' + S_BLOCK + '">' +
                '<div style="' + S_BTITLE + '">Receivables by aging bucket</div>' +
                '<div style="' + S_BSUB + '">How much sits in each age band \u2014 each bar is one bucket, with its amount and share of total receivables.</div>' +
                bucketBars +
                '</div>';

            // ----- By classification (expandable -> country -> channel) -----
            var classes = uniqueOrdered(rows, function (r) { return r.classification || '(blank)'; });
            var classData = [];
            classes.forEach(function (c) {
                var inClass = rows.filter(function (r) { return (r.classification || '(blank)') === c; });
                var cs = sumGroup(inClass);
                if (isZeroGroup(cs)) { return; }
                classData.push({ name: c, sum: cs, pos: clamp0(cs.total), rows: inClass });
            });
            classData.sort(function (a, b) { return b.pos - a.pos; });
            var maxPos = classData.reduce(function (m, x) { return x.pos > m ? x.pos : m; }, 0);

            var classRows = classData.map(function (cd) {
                var cs = cd.sum;
                var barW = maxPos > 0 ? (cd.pos / maxPos * 100) : 0;
                var isOpen = !!mgmtOpenClass[cd.name];
                var sign = isOpen ? '\u2212' : '+';

                var headRow = '<div class="bcrcav-classtoggle" data-class="' + escAttr(cd.name) + '" ' +
                    'style="cursor:pointer;padding:6px 4px;border-radius:4px;">' +
                    '<div style="display:flex;justify-content:space-between;align-items:baseline;font:13px Segoe UI;margin-bottom:5px;">' +
                    '<span><span style="display:inline-block;width:14px;color:#3A6EA5;font-weight:600;">' + sign + '</span>' +
                    '<b style="font-weight:600;">' + cd.name + '</b></span>' +
                    '<span style="color:#4A4A4A;font-variant-numeric:tabular-nums;">' + fmt2(cs.total) + ' SAR</span></div>' +
                    '<div style="width:100%;padding-left:14px;box-sizing:border-box;">' +
                    '<div style="display:flex;height:15px;border-radius:3px;overflow:hidden;width:' + barW + '%;min-width:46px;background:#EEF2F6;">' +
                    MBUCKETS.map(function (b) {
                        var val = cs[b.key];
                        var segTotal = clamp0(cs.notDue) + clamp0(cs.d30) + clamp0(cs.d60) + clamp0(cs.d90) + clamp0(cs.d180);
                        var w = segTotal > 0 ? (clamp0(val) / segTotal * 100) : 0;
                        var pct = cs.total ? (val / cs.total * 100) : 0;
                        return seg(b.color, w, b.label + ' \u00B7 ' + cd.name, val, pct);
                    }).join('') +
                    '</div></div></div>';

                var detail = '';
                if (isOpen) {
                    // Drill: country (collapsible) -> channel. Re-grouping the same rows.
                    var countries = uniqueOrdered(cd.rows, function (r) { return r.country || '(blank)'; });
                    var cMax = 0;
                    var cAgg = countries.map(function (co) {
                        var inCo = cd.rows.filter(function (r) { return (r.country || '(blank)') === co; });
                        var s = sumGroup(inCo);
                        var pos = clamp0(s.total);
                        if (pos > cMax) { cMax = pos; }
                        return { name: co, sum: s, pos: pos, rows: inCo };
                    }).filter(function (x) { return !isZeroGroup(x.sum); })
                        .sort(function (a, b) { return b.pos - a.pos; });

                    detail = cAgg.map(function (co) {
                        var coKey = cd.name + '|' + co.name;
                        var coOpen = !!mgmtOpenCountry[coKey];
                        var coSign = coOpen ? '\u2212' : '+';

                        // Country header row (clickable toggle)
                        var coHead = '<div class="bcrcav-countrytoggle" data-cokey="' + escAttr(coKey) + '" ' +
                            'style="cursor:pointer;display:flex;justify-content:space-between;align-items:baseline;' +
                            'font:600 12px Segoe UI;color:#2E4A66;margin-bottom:3px;">' +
                            '<span><span style="display:inline-block;width:13px;color:#3A6EA5;">' + coSign + '</span>' + co.name + '</span>' +
                            '<span style="font-variant-numeric:tabular-nums;">' + fmt2(co.sum.total) + ' SAR</span></div>';

                        var chHtml = '';
                        if (coOpen) {
                            var channels = uniqueOrdered(co.rows, function (r) { return r.channel || '(blank)'; });
                            var chMax = 0;
                            var chAgg = channels.map(function (ch) {
                                var inCh = co.rows.filter(function (r) { return (r.channel || '(blank)') === ch; });
                                var s = sumGroup(inCh);
                                var pos = clamp0(s.total);
                                if (pos > chMax) { chMax = pos; }
                                return { name: ch, sum: s, pos: pos };
                            }).filter(function (x) { return !isZeroGroup(x.sum); })
                                .sort(function (a, b) { return b.pos - a.pos; });

                            chHtml = chAgg.map(function (ch) {
                                var w = chMax > 0 ? (ch.pos / chMax * 100) : 0;
                                return '<div style="margin:3px 0 3px 18px;">' +
                                    '<div style="display:flex;justify-content:space-between;font:11px Segoe UI;color:#5a6b7b;margin-bottom:2px;">' +
                                    '<span>' + ch.name + '</span><span style="font-variant-numeric:tabular-nums;">' + fmt2(ch.sum.total) + '</span></div>' +
                                    '<div style="display:flex;height:11px;border-radius:2px;overflow:hidden;width:' + w + '%;min-width:32px;background:#EEF2F6;">' +
                                    MBUCKETS.map(function (b) {
                                        var val = ch.sum[b.key];
                                        var st = clamp0(ch.sum.notDue) + clamp0(ch.sum.d30) + clamp0(ch.sum.d60) + clamp0(ch.sum.d90) + clamp0(ch.sum.d180);
                                        var sw = st > 0 ? (clamp0(val) / st * 100) : 0;
                                        var pct = ch.sum.total ? (val / ch.sum.total * 100) : 0;
                                        return seg(b.color, sw, b.label + ' \u00B7 ' + ch.name, val, pct);
                                    }).join('') +
                                    '</div></div>';
                            }).join('');
                            chHtml = chHtml || '<div style="font:11px Segoe UI;color:#6A737D;margin-left:18px;">No channel breakdown.</div>';
                        }

                        return '<div style="margin:6px 0 6px 14px;padding-left:8px;border-left:2px solid #E6E9ED;">' +
                            coHead + chHtml +
                            '</div>';
                    }).join('');
                    detail = '<div style="margin:2px 0 8px 0;">' + (detail || '<div style="font:11px Segoe UI;color:#6A737D;margin-left:14px;">No breakdown.</div>') + '</div>';
                }

                return headRow + detail;
            }).join('');

            html += '<div style="' + S_BLOCK + '">' +
                '<div style="' + S_BTITLE + '">By classification</div>' +
                '<div style="' + S_BSUB + '">Which segments carry the most exposure \u2014 click a row to drill into country and channel. Bar length is total balance; colours show the aging split.</div>' +
                (classRows || '<div style="font:12px Segoe UI;color:#6A737D;">No classification data.</div>') +
                '</div>';

            // ----- Top risk watchlist (sortable; worst accounts by selected column) -----
            var watchAll = rows.filter(function (r) { return clamp0(r.d180) > 0; });
            var sk = mgmtWatchSort.key, sdir = mgmtWatchSort.dir === 'asc' ? 1 : -1;
            function sortVal(r) {
                if (sk === 'name') { return (r.custName || r.custAccount || '').toLowerCase(); }
                if (sk === 'country') { return (r.country || '').toLowerCase(); }
                return +r[sk] || 0;
            }
            watchAll.sort(function (a, b) {
                var va = sortVal(a), vb = sortVal(b);
                if (va < vb) { return -1 * sdir; }
                if (va > vb) { return 1 * sdir; }
                return 0;
            });
            var watch = watchAll.slice(0, 10);

            var watchHtml;
            if (watch.length) {
                function arrow(key) { return sk === key ? (mgmtWatchSort.dir === 'asc' ? ' \u25B2' : ' \u25BC') : ''; }
                // Max 180+ in view, for heat-shading the amount cell (darker = bigger exposure).
                var wMax180 = watch.reduce(function (m, r) { var v = clamp0(r.d180); return v > m ? v : m; }, 0);
                function heat180(v) {
                    var t = wMax180 > 0 ? clamp0(v) / wMax180 : 0;      // 0..1
                    var bg = 'hsl(2,72%,' + (96 - Math.round(t * 34)) + '%)'; // 96% -> 62% lightness
                    var fg = t > 0.5 ? '#FFFFFF' : '#8E1F1F';
                    return 'background:' + bg + ';color:' + fg + ';font-weight:600;';
                }
                var thBase = 'font-weight:600;color:#FFFFFF;padding:7px 8px;cursor:pointer;white-space:nowrap;background:#3A4A5A;';
                var thL = 'text-align:left;' + thBase;
                var thN = 'text-align:right;' + thBase;
                var wHead = '<tr>' +
                    '<th style="' + thL + 'border-top-left-radius:6px;">#</th>' +
                    '<th data-sort="name" style="' + thL + '">Customer' + arrow('name') + '</th>' +
                    '<th data-sort="custAccount" style="' + thL + '">Cust Acct' + arrow('custAccount') + '</th>' +
                    '<th data-sort="invoiceAccount" style="' + thL + '">Invoice Acct' + arrow('invoiceAccount') + '</th>' +
                    '<th data-sort="country" style="' + thL + '">Country' + arrow('country') + '</th>' +
                    '<th data-sort="d180" style="' + thN + '">180+' + arrow('d180') + '</th>' +
                    '<th data-sort="balanceDue" style="' + thN + '">Balance Due' + arrow('balanceDue') + '</th>' +
                    '<th data-sort="dso" style="' + thN + 'border-top-right-radius:6px;">DSO' + arrow('dso') + '</th>' +
                    '</tr>';
                var tdL = 'padding:7px 8px;border-bottom:1px solid #EEF0F2;';
                var tdLN = tdL + 'font-variant-numeric:tabular-nums;';
                var tdN = tdLN + 'text-align:right;';
                var wBody = watch.map(function (r, i) {
                    var name = r.custName || r.custAccount || '(blank)';
                    var dCol = dsoColor(r.dso);
                    var zebra = (i % 2 === 1) ? 'background:#F7F9FB;' : '';
                    // DSO shown as a colored pill (7 dp, uses fmt7).
                    var dsoPill = '<span style="display:inline-block;min-width:46px;text-align:right;padding:2px 8px;border-radius:10px;' +
                        'background:' + dCol + '1A;color:' + dCol + ';font-weight:600;font-variant-numeric:tabular-nums;">' + fmt7(r.dso) + '</span>';
                    var rankBg = i < 3 ? '#A62B2B' : (i < 6 ? '#E0871E' : '#9AA6B2');
                    var rank = '<span style="display:inline-block;width:20px;height:20px;line-height:20px;text-align:center;border-radius:50%;' +
                        'background:' + rankBg + ';color:#fff;font:600 11px Segoe UI;">' + (i + 1) + '</span>';
                    return '<tr class="bcrcav-wrow" style="' + zebra + '">' +
                        '<td style="' + tdL + '">' + rank + '</td>' +
                        '<td style="' + tdL + 'font-weight:600;color:#1B1B1B;">' + name + '</td>' +
                        '<td style="' + tdL + 'color:#4A4A4A;">' + (r.custAccount || '') + '</td>' +
                        '<td style="' + tdL + 'color:#4A4A4A;">' + (r.invoiceAccount || '') + '</td>' +
                        '<td style="' + tdL + '">' + (r.country || '') + '</td>' +
                        '<td style="' + tdN + heat180(r.d180) + 'border-radius:4px;">' + fmt2(r.d180) + '</td>' +
                        '<td style="' + tdN + '">' + fmt2(r.balanceDue) + '</td>' +
                        '<td style="' + tdN + '">' + dsoPill + '</td>' +
                        '</tr>';
                }).join('');
                watchHtml = '<div style="overflow-x:auto;"><table class="bcrcav-watchtbl" style="width:100%;border-collapse:separate;border-spacing:0;font:12px Segoe UI;min-width:760px;"><thead>' + wHead + '</thead><tbody>' + wBody + '</tbody></table></div>';
            } else {
                watchHtml = '<div style="font:12px Segoe UI;color:#6A737D;">No balances past 180 days.</div>';
            }
            html += '<div style="' + S_BLOCK + '">' +
                '<div style="' + S_BTITLE + '">Top risk \u2014 customers by 180+ balance</div>' +
                '<div style="' + S_BSUB + '">The accounts to chase first \u2014 click a column to re-sort. DSO is colour-coded: green \u2264 30, amber \u2264 60, red over 60 or abnormal.</div>' +
                watchHtml +
                '</div>';

            // ----- Commit to DOM -----
            el.style.cssText = 'position:relative;margin-top:22px;padding-top:18px;border-top:1px solid #E6E9ED;display:flex;flex-direction:column;gap:18px;';
            el.innerHTML = html;

            // Tooltip (shown on hovering a segment bar)
            var tip = document.createElement('div');
            tip.style.cssText = 'position:absolute;z-index:50;pointer-events:none;background:#1B1B1B;color:#fff;' +
                'font:12px Segoe UI;padding:6px 9px;border-radius:4px;white-space:nowrap;' +
                'box-shadow:0 2px 6px rgba(0,0,0,0.25);opacity:0;transition:opacity 0.1s ease;';
            el.appendChild(tip);
            function moveTip(ev) {
                var rect = el.getBoundingClientRect();
                var x = ev.clientX - rect.left + 14;
                var y = ev.clientY - rect.top + 14;
                var maxX = el.clientWidth - tip.offsetWidth - 8;
                if (x > maxX) { x = maxX; }
                if (x < 0) { x = 0; }
                tip.style.left = x + 'px';
                tip.style.top = y + 'px';
            }
            function showTip(ev, content) { tip.innerHTML = content; tip.style.opacity = '1'; moveTip(ev); }
            function hideTip() { tip.style.opacity = '0'; }
            Array.prototype.forEach.call(el.querySelectorAll('.bcrcav-seg'), function (s) {
                s.addEventListener('mouseenter', function (ev) {
                    var content = '<b style="font-weight:600;">' + s.getAttribute('data-label') + '</b><br>' +
                        s.getAttribute('data-value') + ' SAR (' + s.getAttribute('data-pct') + '%)';
                    showTip(ev, content);
                });
                s.addEventListener('mousemove', moveTip);
                s.addEventListener('mouseleave', hideTip);
            });

            // Classification expand/collapse
            Array.prototype.forEach.call(el.querySelectorAll('.bcrcav-classtoggle'), function (row) {
                row.addEventListener('click', function () {
                    var k = row.getAttribute('data-class');
                    mgmtOpenClass[k] = !mgmtOpenClass[k];
                    renderMgmt(d);   // re-render with same data
                });
            });

            // Country expand/collapse (stopPropagation so it doesn't toggle the classification)
            Array.prototype.forEach.call(el.querySelectorAll('.bcrcav-countrytoggle'), function (row) {
                row.addEventListener('click', function (ev) {
                    ev.stopPropagation();
                    var k = row.getAttribute('data-cokey');
                    mgmtOpenCountry[k] = !mgmtOpenCountry[k];
                    renderMgmt(d);   // re-render with same data
                });
            });

            // Watchlist row hover highlight
            Array.prototype.forEach.call(el.querySelectorAll('.bcrcav-wrow'), function (tr) {
                var orig = tr.getAttribute('style') || '';
                tr.addEventListener('mouseenter', function () { tr.setAttribute('style', orig + 'background:#EAF2FB;'); });
                tr.addEventListener('mouseleave', function () { tr.setAttribute('style', orig); });
            });

            // Watchlist sort
            Array.prototype.forEach.call(el.querySelectorAll('.bcrcav-watchtbl th[data-sort]'), function (th) {
                th.addEventListener('click', function () {
                    var k = th.getAttribute('data-sort');
                    if (mgmtWatchSort.key === k) {
                        mgmtWatchSort.dir = (mgmtWatchSort.dir === 'asc') ? 'desc' : 'asc';
                    } else {
                        mgmtWatchSort.key = k;
                        mgmtWatchSort.dir = (k === 'name' || k === 'country') ? 'asc' : 'desc';
                    }
                    renderMgmt(d);   // re-render with same data
                });
            });
        }

        // renderAll: entry point per data load. Resets all expand/collapse state and
        // redraws every section. Called from the AgingData observer below.
        function renderAll(d) {
            customers = d.customers || [];
            openClass = {};
            openCountry = {};
            openChannel = {};
            openInvoiceAcct = {};
            mgmtOpenClass = {};
            mgmtOpenCountry = {};
            mgmtWatchSort = { key: 'd180', dir: 'desc' };
            renderRunInfo(d);
            renderBank(d);
            render();
            renderMgmt(d);
        }
        // AgingData is the bound JSON string from the X++ engine. Parse and render on change.
        $dyn.observe(self.AgingData, function (json) {
            if (!json) { return; }
            try { renderAll(JSON.parse(json)); }
            catch (e) { console.error('BCRCustAgingVisual parse error', e); }
        });
    };

    Object.defineProperty($dyn.controls.BCRCustAgingVisual, 'prototype',
        { value: Object.create($dyn.ui.Control.prototype) });
}());