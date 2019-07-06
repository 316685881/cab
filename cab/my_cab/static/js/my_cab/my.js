function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

// 点击推出按钮时执行的函数
function logout() {
    $.ajax({
        url: "/api/v1.0/session",
        type: "delete",
        headers: {
            "X-CSRFToken": getCookie("csrf_token")
        },
        dataType: "json",
        success: function (resp) {
            if ("0" == resp.errno) {
                // alert(resp.errmsg);
                location.href = "/index.html";
            }
        }
    });
}

$(document).ready(function(){
    $.get('/api/v1.0/user/my', function (resp) {
        if (resp.errno == '0'){
            $('#user-name').html(resp.data.username);
            $('#user-mobile').html(resp.data.phone);
            $('#user-avatar').attr('src', resp.data.user_head);
        }else if (resp.errno == '4101') {
            location.href = '/login.html'
        }else {
            alert(resp.errmsg)
        }
    })

})