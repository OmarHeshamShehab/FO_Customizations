/**
 * VoxD365ControlScript.js - Extensible Control JavaScript for D365 F&O
 */
(function () {
    'use strict';

    $dyn.ui.defaults.VoxD365Control = {};

    $dyn.controls.VoxD365Control = function (data, element) {
        var self = this;
        $dyn.ui.Control.apply(self, arguments);
        $dyn.ui.applyDefaults(self, data, $dyn.ui.defaults.VoxD365Control);

        if (!self.HtmlContent) {
            console.warn('VoxD365: HtmlContent property not found');
            return;
        }

        $dyn.observe(self.HtmlContent, function (htmlValue) {
            if (!htmlValue) {
                console.log('VoxD365: Empty HTML content');
                return;
            }

            var container = $(element).find('#VoxD365Container');
            if (!container.length) {
                console.error('VoxD365: Container not found');
                return;
            }

            try {
                var parser = new DOMParser();
                var doc = parser.parseFromString(htmlValue, 'text/html');

                container.empty();

                // IMPORTANT: Also inject styles from head
                var styles = doc.head.getElementsByTagName('style');
                for (var i = 0; i < styles.length; i++) {
                    container[0].appendChild(document.importNode(styles[i], true));
                }

                // Inject body content
                var nodes = doc.body.childNodes;
                for (var i = 0; i < nodes.length; i++) {
                    container[0].appendChild(document.importNode(nodes[i], true));
                }

                console.log('VoxD365: HTML injected successfully');

            } catch (e) {
                console.error('VoxD365: Error parsing HTML', e);
                return;
            }

            // Extract and run scripts
            var scripts = [];
            container.find('script').each(function () {
                var src = $(this).attr('src');
                if (!src) {
                    scripts.push($(this).text());
                }
                $(this).remove();
            });

            setTimeout(function () {
                for (var i = 0; i < scripts.length; i++) {
                    try {
                        var fn = new Function(scripts[i]);
                        fn();
                        console.log('VoxD365: Script executed');
                    } catch (e) {
                        console.error('VoxD365: Script error', e);
                    }
                }
            }, 300);
        });
    };

    Object.defineProperty(
        $dyn.controls.VoxD365Control,
        'prototype',
        { value: Object.create($dyn.ui.Control.prototype) }
    );

    console.log('VoxD365: Control script loaded');
}());