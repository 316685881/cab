$(document).ready(function() {
    // 检查用户的登录状态
    $.get("/hello", function (resp) {
        if ("0" == resp.errno) {
            $("#div").html(resp.errmsg);
        }
    }, "json");
})
