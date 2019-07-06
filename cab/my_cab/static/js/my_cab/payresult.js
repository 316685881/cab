

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function(){
    var data = document.location.search.substr(1)
    $.ajax({
        url: '/api/v1.0/order/payment',
        type: 'put',
        data: data,
        dataType: 'json',
        headers: {"X-CSRFToken": getCookie("csrf_token")},
        success: function (resp) {
            if (resp.errno == 0) {
                $('#result_con>h2').html(resp.errmsg)
            }else if (resp.errno == '4101') {
                location.href = '/login.html'
            }else {
                alert(resp.errmsg)
            }
        }
    });
});
