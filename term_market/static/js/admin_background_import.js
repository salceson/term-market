/**
 * Author: Michał Ciołczyk
 *
 * jQuery background import plugin
 *
 * Checks if background import task has finished.
 */

(function ($) {
    function safe_tags(str) {
        return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }

    $.checkImportTask = function (options) {
        options = $.extend({
            url: '/',
            timeout: 500,
            successContent: "Success!",
            successClass: "",
            failureContent: "Failure!",
            failureClass: "",
            failureShowMsg: true,
            linksContent: "",
            processingSelector: "#processing",
            linksSelector: "#actions"
        }, options);

        var checkTask = function () {
            $.ajax({
                url: options.url,
                method: 'get'
            }).done(function (data) {
                console.log(data);
                if (!data['finished']) {
                    setTimeout(checkTask, 500);
                } else {
                    var msg = safe_tags(data['message']);
                    if (!data['success']) {
                        var content = options.failureContent;
                        if (options.failureShowMsg) {
                            content += ' <pre>' + msg + '</pre>';
                        }
                        $(options.processingSelector).html(content).attr("class", options.failureClass);
                    } else {
                        $(options.processingSelector).html(options.successContent).attr("class", options.successClass);
                    }
                    $(options.linksSelector).html(options.linksContent);
                }
            });
        };

        checkTask();
    };
})(grp.jQuery);
