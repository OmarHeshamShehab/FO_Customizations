(function () {
    'use strict';

    $dyn.ui.defaults.SalesIntelligenceControl = {};

    $dyn.controls.SalesIntelligenceControl = function (data, element) {
        var self = this;

        $dyn.ui.Control.apply(self, arguments);
        $dyn.ui.applyDefaults(self, data, $dyn.ui.defaults.SalesIntelligenceControl);

        if (!self.HtmlContent) {
            return;
        }

        $dyn.observe(self.HtmlContent, function (htmlValue) {
            if (!htmlValue) return;

            var container = $(element).find('#SalesIntelligenceDashboardContainer');
            if (!container.length) return;

            try {
                var parser = new DOMParser();
                var doc = parser.parseFromString(htmlValue, 'text/html');
                container.empty();
                var nodes = doc.body.childNodes;
                for (var i = 0; i < nodes.length; i++) {
                    container[0].appendChild(document.importNode(nodes[i], true));
                }
            } catch (e) {
                return;
            }

            var scripts = [];
            container.find('script').each(function () {
                var src = $(this).attr('src');
                if (!src) {
                    scripts.push($(this).text());
                }
                $(this).remove();
            });

            function runScripts() {
                setTimeout(function () {
                    for (var i = 0; i < scripts.length; i++) {
                        try {
                            var fn = new Function(scripts[i]);
                            fn();
                        } catch (e) {
                            // skip
                        }
                    }
                }, 300);
            }

            if (typeof Chart !== 'undefined') {
                runScripts();
            } else {
                var script = document.createElement('script');
                script.type = 'text/javascript';
                script.src = '/resources/scripts/SalesIntelligenceChartJS.js';
                script.onload = runScripts;
                script.onerror = function () {
                    runScripts();
                };
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