function hrefBack() {
    history.go(-1);
}

function decodeQuery(){
    var search = decodeURI(document.location.search);
    return search.replace(/(^\?)/, '').split('&').reduce(function(result, item){
        values = item.split('=');
        result[values[0]] = values[1];
        return result;
    }, {});
}

$(document).ready(function(){


    //获取地址栏的车辆id

    var result = decodeQuery();
    var car_id = result['id'];
    $.get('/api/v1.0/car/detail/'+car_id, function (resp) {

        if (resp.errno == '0') {
            var car = resp.data.car;

            // alert('ok');
            if (resp.data.car.user_id != resp.data.user_id){
                $(".update-car").hide();
                $(".book-car").show();

                $(".book-car").attr("href", "/booking.html?cid="+car.car_id);
            }
            else {

                $(".book-car").hide();
                $(".update-car").show();
                $(".update-car").attr("href", "/updatecar.html?id="+car.car_id);
            }

            $('.swiper-container').html(template('swiper_temp', {image_urls: car.image_urls, price: car.price}));
            $('.detail-con').html(template('car_info_temp', {car:car}));
            var mySwiper = new Swiper ('.swiper-container', {
            loop: true,
            autoplay: 2000,
            autoplayDisableOnInteraction: false,
            pagination: '.swiper-pagination',
            paginationType: 'fraction'
            });

            //获取配置数据
            $.get('/api/v1.0/car/facilities', function (resp) {
                if (resp.errno == '0'){
                    var all_facilities = resp.data;
                    for (i = 0; i < all_facilities.length; i++) {
                        var flag = false;
                        for (j = 0; j<car.facilities.length; j++){
                           if (all_facilities[i].facility_id == car.facilities[j]) {
                               $('.car-facility-list').append('<li style="color: green"><span class="mui-icon mui-icon-checkmarkempty"></span>'+ all_facilities[i].facility_name +'</li>');
                               flag = true;
                                break;
                           }

                        }
                        if (!flag){
                            $('.car-facility-list').append('<li style="color: #bbbbbb;"><span class="mui-icon mui-icon-closeempty"></span>'+ all_facilities[i].facility_name +'</li>')
                        }


                    }



                }
                else {
                    alert(errmsg)
                }
            });


        }
        else {
            alert(resp.errmsg+'--error')
        }
    });


})