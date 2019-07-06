//模态框居中的控制
function centerModals(){
    $('.modal').each(function(i){   //遍历每一个模态框
        var $clone = $(this).clone().css('display', 'block').appendTo('body');    
        var top = Math.round(($clone.height() - $clone.find('.modal-content').height()) / 2);
        top = top > 0 ? top : 0;
        $clone.remove();
        $(this).find('.modal-content').css("margin-top", top-30);  //修正原先已经有的30个像素
    });
}

function getFormatDate(){
    var nowDate = new Date();
    var year = nowDate.getFullYear();
    var month = nowDate.getMonth() + 1 < 10 ? "0" + (nowDate.getMonth() + 1) : nowDate.getMonth() + 1;
    var date = nowDate.getDate() < 10 ? "0" + nowDate.getDate() : nowDate.getDate();
    var hour = nowDate.getHours()< 10 ? "0" + nowDate.getHours() : nowDate.getHours();
    var minute = nowDate.getMinutes()< 10 ? "0" + nowDate.getMinutes() : nowDate.getMinutes();
    var second = nowDate.getSeconds()< 10 ? "0" + nowDate.getSeconds() : nowDate.getSeconds();
    return year + "-" + month + "-" + date+" "+hour+":"+minute;
}



function goToSearchPage(th) {
    var url = "/search.html?";
    url += ("aid=" + $(th).attr("area-id"));
    url += "&";
    var areaName = $(th).attr("area-name");
    if (undefined == areaName) areaName="";
    url += ("aname=" + areaName);
    url += "&";
    url += ("sd=" + $("#dateSelect").val());
    url += "&";
    url += ("sp=" + $('#startPoint').val());
    url += "&";
    url += ("ep=" + $('#endPoint').val());
    location.href = url;
}

/*content高度*/
    function initSize() {
        var height = $(window).height() - $("header").height() - $("#description").height() - $("#menu").height();
        $("#content").height(height + "px");
    }

$(document).ready(function() {
    // 检查用户的登录状态
    $.get("/api/v1.0/session", function (resp) {
        if ("0" == resp.errno) {
            $(".top-bar>.user-info>.user-name").html(resp.data.username);
            $(".top-bar>.user-info").show();
        } else {
            $(".top-bar>.register-login").show();
        }
    }, "json");


    //获取主页数据并展示在轮播图中
    $.get('/api/v1.0/index', function (resp) {
        if (resp.errno == '0') {
            $("#swiper-wrapper").html(template('swiper_temp', {cars: resp.data}));
            // alert('OK')
            var mySwiper = new Swiper('.swiper-container', {
                loop: true,
                autoplay: 2000,
                autoplayDisableOnInteraction: false,
                pagination: '.swiper-pagination',
                paginationClickable: true
            });
        } else {
            alert('error' + resp.errmsg)
        }
    });

    //加载区域
    $.get('/api/v1.0/car/area', function (resp) {
        if (resp.errno == '0') {
            var areas = resp.data;

            //    使用template.js的template(template, data)生成模板
            var html = template('area_temp', {areas: areas});
            $('#area-list').html(html);
            //点击效果
            $(".area-list a").click(function (e) {
                $("#area-btn").html($(this).html());
                $(".search-btn").attr("area-id", $(this).attr("area-id"));
                $(".search-btn").attr("area-name", $(this).html());
                $("#area-modal").modal("hide");
            });
        } else {
            alert(errmsg)
        }
    });


    $("#dateSelect").val(getFormatDate());
    $("#dateSelect").click(function () {
        var dtPicker = new mui.DtPicker({type: 'datetime', beginDate: getFormatDate()});

        /*参数：'datetime'-完整日期视图(年月日时分)
                'date'--年视图(年月日)
                'time' --时间视图(时分)
                'month'--月视图(年月)
                'hour'--时视图(年月日时)
        */
        dtPicker.show(function (selectItems) {
            var y = selectItems.y.text;  //获取选择的年
            var m = selectItems.m.text;  //获取选择的月
            var d = selectItems.d.text;  //获取选择的日
            var H = selectItems.h.text;  //获取选择的时
            var M = selectItems.i.text;  //获取选择的分

            var date = y + "-" + m + "-" + d + " " + H + ":" + M;
            $("#dateSelect").val(date);

        });


    });
    $('.modal').on('show.bs.modal', centerModals);      //当模态框出现的时候
    $(window).on('resize', centerModals);               //当窗口大小变化的时候



})