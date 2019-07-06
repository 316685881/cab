function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function() {
        setTimeout(function(){
            $('.popup_con').fadeOut('fast',function(){}); 
        },1000) 
    });
}


function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(document).ready(function () {

    $.get('/api/v1.0/user/head', function (resp) {
        if (resp.errno == '0') {
            $("#user-avatar").attr("src", resp.data.image_url);
            $('#upload_btn').val('更换')
        }
        else if (resp.errno == '4101') {
            location.href = '/login.html'
        }else {
            alert(resp.errmsg)
        }

    });

    $.get('/api/v1.0/user/username', function (resp) {
        if (resp.errno == '0') {
            $('#user-name').val(resp.data.username);
            $('#alter_btn').val('更改')
        }
        else if (resp.errno == '4101') {
            location.href = '/login.html'
        }else {
            alert(resp.errmsg)
        }

    });

    $("#form-avatar").submit(function (e) {
        // 阻止表单的默认行为
        e.preventDefault();
        // 利用jquery.form.min.js提供的ajaxSubmit对表单进行异步提交
        $(this).ajaxSubmit({
            url: "/api/v1.0/user/head",
            type: "post",
            dataType: "json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            success: function (resp) {
                if (resp.errno == "0") {
                    // 上传成功
                    var imageUrl = resp.data.image_url;
                    $("#user-avatar").attr("src", imageUrl);
                    alert(resp.errmsg)
                    // showSuccessMsg()
                } else {
                    alert(resp.errmsg);
                }
            }
        })
    });

//    更改用户名
    $('#form-name').submit(function (e) {
        e.preventDefault();

        var username = $('#user-name').val();
        if (!username) {
            $('.error-msg').html('用户名不能为空').show();
            return

        }
        var req_data = {
            username: username
        };

        var req_json = JSON.stringify(req_data);

        $.ajax({
            url: '/api/v1.0/user/username',
            type: 'post',
            data: req_json,
            contentType: 'application/json',
            dataType: 'json',
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            }, // 请求头，将csrf_token值放到请求中，方便后端csrf进行验证
            success: function (resp) {
                if (resp.errno == '0'){
                    $('#user-name').value = username;
                    $('.error-msg').hide();
                    alert(resp.errmsg)
                }
                else if (resp.errno == '4003') {
                    $('.error-msg').show();
                }
                else {
                    alert(resp.errmsg)
                }
            }
        })
    })

})
