$(document).ready(function(){
    $('.auth-warn').show();

    $.get('/api/v1.0/user/auth', function (resp) {
        if (resp.errno == '4101') {
            location.href = '/login.html'


        }
        else if (resp.errno == '0') {
            if (!(resp.data.real_name && resp.data.id_card)){

                $('#cars-list').hide();
                return
            }

            $('.auth-warn').hide();
            $('#cars-list').show();
            //实名后获取我的房源信息
            $.get('/api/v1.0/user/cars', function (data_resp) {
                if (data_resp.errno == '0') {
                    var html = template('my-car_temp', {my_cars:data_resp.data.my_cars});
                    $("#cars-list").html(html)
                }
                else {
                    var html = template('my-car_temp', {my_cars:[]});
                    $("#cars-list").html(html)
                }
            })
        }
    });

});