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
    $.get('/api/v1.0/user/auth', function (resp) {
        if (resp.errno == '0') {
            $('#real-name').val(resp.data.real_name).prop('disabled', true);
            $('#id-card').val(resp.data.id_card).prop('disabled', true);
            $('#auth_btn').hide()
        }else if (resp.errno == '4101') {
            location.href = '/login.html'
        }else {
            alert(resp.errmsg)
        }
    });

    $('#form-auth').submit(function (e) {
        e.preventDefault();
        var realName = $('#real-name').val();
        var idCard = $('#id-card').val();
        if (!realName){
            $('.error-msg').show();
            return
        }
        if (!idCard) {
            $('.error-msg').show();
            return
        }
        var req_data = {
            real_name: realName,
            id_card: idCard
        };
        var req_json = JSON.stringify(req_data);

        $.ajax({
            url: 'api/v1.0/user/auth',
            type:"post",
            data: req_json,
            contentType: 'application/json',
            dataType: 'json',
            headers:{
                "X-CSRFToken":getCookie("csrf_token")
            },
            success: function (resp) {
                if (resp.errno == '0'){
                    $('#real-name').val(resp.data.real_name).prop('disabled', true);
                    $('#id-card').val(resp.data.id_card).prop('disabled', true);
                    $('#auth_btn').hide();
                    $('.error-msg').css("color","green").html(resp.errmsg).show();
                    // alert(resp.errmsg)
                }
                else {
                    $('.error-msg').html(resp.errmsg).show();
                }
            }

        })

    })
})