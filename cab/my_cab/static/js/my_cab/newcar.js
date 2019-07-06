function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function(){



    // $('.popup_con').fadeIn('fast');
    // $('.popup_con').fadeOut('fast');

    //获取区域数据
    //填充数据第一种方式
    // $.get('/api/v1.0/car/area', function (resp) {
    //     if (resp.errno == '0'){
    //         for (i=0;i<resp.data.length;i++){
    //             var area = resp.data[i];
    //             $('#area-id').append('<option value="' +area.area_id+'">'+area.area_name+'</option>')
    //         }
    //     }
    //     else {
    //         alert(errmsg)
    //     }
    // })

   // 填充数据第二种方式，使用art-template ，引入template.js
        $.get('/api/v1.0/car/area', function (resp) {
            if (resp.errno == '0'){
                var areas = resp.data;

            //    使用template.js的template(template, data)生成模板
                var html = template('area_temp', {areas:areas});
                $('#area-id').html(html)
            }
            else {
                alert(errmsg)
            }
        });

        //获取配置数据
        $.get('/api/v1.0/car/facilities', function (resp) {
            if (resp.errno == '0'){
                var facilities = resp.data;

            //    使用template.js的template(template, data)生成模板
                var html = template('facility-temp', {facilities:facilities});
                $('.car-facility-list').html(html)


            }
            else {
                alert(errmsg)
            }
        });



    //发送信息参数
    $("#form-car-info").submit(function (e) {
        e.preventDefault();
        //获取车辆信息参数
        var raw_parm = $(this).serializeArray();
        var data = {};
        raw_parm.map(function (item) {
            data[item.name] = item.value
        });

        //获取车辆设施参数
        var facility = [];
        $(":checked[name=facility]").each(function (index, em) {
            facility[index] = $(em).val()
        });

        data["facility"] = facility;
        var req_json = JSON.stringify(data);
        alert(req_json);
        $.ajax({
            url:'api/v1.0/car',
            type:'post',
            data: req_json,
            contentType: 'application/json',
            dataType: 'json',
            headers:{
                // 请求头，将csrf_token值放到请求中，方便后端csrf进行验证
                "X-CSRFToken": getCookie("csrf_token")
            },
            success: function (resp) {
                if (resp.errno == '4101'){
                    alert(resp.errmsg);
                    location.href = '/login.html'
                }

                if (resp.errno == '0') {
                    $("#car-id").val(resp.data.car_id);
                    $("#form-car-info").hide();
                    $('#form-car-image').show();
                    alert(resp.errmsg)
                }
                else {
                    alert(resp.errmsg)
                }
            }

        })
    });

    $('#form-car-image').submit(function (e) {
        e.preventDefault();

        $(this).ajaxSubmit({
            url:'api/v1.0/car/image',
            type:'post',
            dataType: 'json',
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            }, // 请求头，将csrf_token值放到请求中，方便后端csrf进行验证
            success:function (resp) {
                if (resp.errno == '4101'){
                    alert(resp.errmsg);
                    location.href = '/login.html'
                }

                if (resp.errno == '0') {
                    alert(resp.errmsg);
                    var data = resp.data;

                    $('#car-image-cons').append('<img src="'+ data.image_url+ '">')
                }
                else {
                    alert(resp.errmsg)
                }
            }
        })
    });



})