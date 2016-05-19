/**
 * Created by caimiao on 15-6-28.
 */

define(function(require, exports, module) {
    exports.init_jq = function () {
        jQuery.extend({
            // alert弹出框
            phalert: function(content) {
                $("#g_alert_content").text(content);
                $("#global_alert_dlg").modal({show: true, keyboard: false, backdrop: 'static'})
            },
            // 弹出确认框
            phconfirm: function(content, callback) {
                $("#g_confirm_content").text(content);

                if (callback instanceof Function) {
                    $("#g_confirm_todo").bind('click', callback)
                }
                $("#global_confirm_dlg").modal({show: true, keyboard: false, backdrop: 'static'});
            },
            // 关闭确认框
            phconfirm_dismiss: function() {
                $("#g_confirm_todo").unbind("click");
                $("#global_confirm_dlg").modal("hide");
            }
        });
    };
})