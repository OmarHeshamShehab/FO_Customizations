(function () {
    'use strict';

    $dyn.ui.defaults.SalesIntelligenceControl = {};

    $dyn.controls.SalesIntelligenceControl = function (data, element) {
        var self = this;

        $dyn.ui.Control.apply(self, arguments);
        $dyn.ui.applyDefaults(self, data, $dyn.ui.defaults.SalesIntelligenceControl);

        // Guard: HtmlContent must exist before observing
        if (!self.HtmlContent) {
            return;
        }

        $dyn.observe(self.HtmlContent, function (htmlValue) {
            if (!htmlValue) return;

            var container = $(element).find('#SalesIntelligenceDashboardContainer');
            if (!container.length) return;

            container.html(htmlValue);

            // Execute any scripts embedded in the returned HTML
            var scripts = [];
            container.find('script').each(function () {
                scripts.push($(this).text());
                $(this).remove();
            });

            function runCharts() {
                setTimeout(function () {
                    for (var i = 0; i < scripts.length; i++) {
                        try {
                            var fn = new Function(scripts[i]);
                            fn();
                        } catch (e) {
                            // skip failed scripts silently
                        }
                    }
                }, 300);
            }

            if (typeof Chart !== 'undefined') {
                runCharts();
            } else {
                var chartUrl = $dyn.internal.getResourceUrl('ChartJS');
                var script = document.createElement('script');
                script.type = 'text/javascript';
                script.src = chartUrl;
                script.onload = runCharts;
                document.head.appendChild(script);
            }
        });
    };

    Object.defineProperty(
        $dyn.controls.SalesIntelligenceControl,
        'prototype',
        { value: Object.create($dyn.ui.Control.prototype) }
    );

}());