var cur_page = 1; // 当前页
var next_page = 1; // 下一页
var total_page = 1;  // 总页数
var car_data_querying = true;   // 是否正在向后台获取数据

// 解析url中的查询字符串
function decodeQuery(){
    var search = decodeURI(document.location.search);
    return search.replace(/(^\?)/, '').split('&').reduce(function(result, item){
        values = item.split('=');
        result[values[0]] = values[1];
        return result;
    }, {});
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

// 更新用户点选的筛选条件
function updateFilterDateDisplay() {
    var startDate = $("#start-date").val();
    var start_point = $("#start-point").val();
    var end_point = $("#end-point").val();
    var $filterDateTitle = $(".filter-title-bar>.filter-title").eq(0).children("ul").children('li').eq(0);
    var $filterPointTitle = $(".filter-title-bar>.filter-title").eq(0).children("ul").children('li').eq(1);
    if (startDate) {
        var text = startDate.substr(5);
        $filterDateTitle.html(text);
    } else {
        $filterDateTitle.html("用车时间");
    }
    if (start_point && end_point){
        $filterPointTitle .html(start_point+'->'+end_point)
    }else {
        $filterPointTitle .html('地点')
        
    }
}


// 更新房源列表信息
// action表示从后端请求的数据在前端的展示方式
// 默认采用追加方式
// action=renew 代表页面数据清空从新展示
function updateHouseData(action) {
    var areaId = $(".filter-area>li.active").attr("area-id");
    if (undefined == areaId) areaId = "";
    var startDate = $("#start-date").val();
    var start_point = $("#start-point").val();
    var end_point = $("#end-point").val();
    var sortKey = $(".filter-sort>li.active").attr("sort-key");
    var params = {
        aid:areaId,
        sd:startDate,
        sp:start_point,
        ep:end_point,
        sk:sortKey,
        p:next_page
    };
    $.get("/api/v1.0/cars", params, function(resp){
        car_data_querying = false;
        if ("0" == resp.errno) {
            if (0 == resp.data.total_pages) {
                $(".car-list").html("暂时没有符合您查询的车辆信息。");
            } else {
                total_page = resp.data.total_pages;
                if ("renew" == action) {
                    cur_page = 1;
                    $(".car-list").html(template("car-temp", {cars:resp.data.cars}));
                } else {
                    cur_page = next_page;
                    $(".car-list").append(template("car-temp", {cars: resp.data.cars}));
                }
            }
        }
    })
}

$(document).ready(function() {
    var queryData = decodeQuery();
    var startDate = queryData["sd"];
    var startPoint = queryData["sp"];
    var endPoint = queryData["ep"];
    $("#start-date").val(startDate);
    $("#start-point").val(startPoint);
    $('#end-point').val(endPoint);
    updateFilterDateDisplay();
    var areaName = queryData["aname"];
    if (!areaName) areaName = "位置区域";
    $(".filter-title-bar>.filter-title").eq(1).children("span").eq(0).html(areaName);


    // 获取筛选条件中的城市区域信息
    $.get("/api/v1.0/car/area", function (data) {
        if ("0" == data.errno) {
            // 用户从首页跳转到这个搜索页面时可能选择了城区，所以尝试从url的查询字符串参数中提取用户选择的城区
            var areaId = queryData["aid"];
            // 如果提取到了城区id的数据
            if (areaId) {
                // 遍历从后端获取到的城区信息，添加到页面中
                for (var i = 0; i < data.data.length; i++) {
                    // 对于从url查询字符串参数中拿到的城区，在页面中做高亮展示
                    // 后端获取到城区id是整型，从url参数中获取到的是字符串类型，所以将url参数中获取到的转换为整型，再进行对比
                    areaId = parseInt(areaId);
                    if (data.data[i].area_id == areaId) {
                        $(".filter-area").append('<li area-id="' + data.data[i].area_id + '" class="active">' + data.data[i].area_name + '</li>');
                    } else {
                        $(".filter-area").append('<li area-id="' + data.data[i].area_id + '">' + data.data[i].area_name + '</li>');
                    }
                }
            } else {
                // 如果url参数中没有城区信息，不需要做额外处理，直接遍历展示到页面中
                for (var i = 0; i < data.data.length; i++) {
                    $(".filter-area").append('<li area-id="' + data.data[i].area_id + '">' + data.data[i].area_name + '</li>');
                }
            }
            // 在页面添加好城区选项信息后，更新展示车辆列表信息
            updateHouseData("renew");

            //添加滚动事件，距离底部100时加载下一页
            $(document).scroll(function () {
                var scroH = $(document).scrollTop();  //滚动高度
                var viewH = $(window).height();  //可见高度
                var contentH = $(document).height();  //内容高度

                //         if(scroH >100){  //距离顶部大于100px时
                //
                //         }

                if (contentH - (scroH + viewH) <= 100) {  //距离底部高度小于100px
                    // alert(contentH - (scroH + viewH));
                    // 如果没有正在向后端发送查询车辆列表信息的请求
                    if (!car_data_querying) {
                        // 将正在向后端查询车辆列表信息的标志设置为真，
                        car_data_querying = true;
                        // 如果当前页面数还没到达总页数
                        if (cur_page < total_page) {
                            // 将要查询的页数设置为当前页数加1
                            next_page = cur_page + 1;
                            // 向后端发送请求，查询下一页车辆数据
                            updateHouseData();
                        } else {
                            car_data_querying = false;
                        }
                    }
                }

                // if (contentH = (scroH + viewH)){  //滚动条滑到底部啦
                //
                // }  

            });


        }
    });

    $("#start-date").click(function () {
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
            $("#start-date").val(date);

        });
    });

    // $(".input-daterange").datepicker({
    //     format: "yyyy-mm-dd hh:ii",
    //     startDate: "today",
    //     language: "zh-CN",
    //     autoclose: true
    // });
    var $filterItem = $(".filter-item-bar>.filter-item");
    $(".filter-title-bar").on("click", ".filter-title", function (e) {
        var index = $(this).index();
        if (!$filterItem.eq(index).hasClass("active")) {
            $(this).children("span").children("i").removeClass("fa-angle-down").addClass("fa-angle-up");
            $(this).siblings(".filter-title").children("span").children("i").removeClass("fa-angle-up").addClass("fa-angle-down");
            $filterItem.eq(index).addClass("active").siblings(".filter-item").removeClass("active");
            $(".display-mask").show();
        } else {
            $(this).children("span").children("i").removeClass("fa-angle-up").addClass("fa-angle-down");
            $filterItem.eq(index).removeClass('active');
            $(".display-mask").hide();
            updateFilterDateDisplay();
        }
    });
    $(".display-mask").on("click", function (e) {
        $(this).hide();
        $filterItem.removeClass('active');
        updateFilterDateDisplay();
        cur_page = 1;
        next_page = 1;
        total_page = 1;
        updateHouseData("renew");

    });
    $(".filter-item-bar>.filter-area").on("click", "li", function (e) {
        if (!$(this).hasClass("active")) {
            $(this).addClass("active");
            $(this).siblings("li").removeClass("active");
            $(".filter-title-bar>.filter-title").eq(1).children("span").eq(0).html($(this).html());
        } else {
            $(this).removeClass("active");
            $(".filter-title-bar>.filter-title").eq(1).children("span").eq(0).html("位置区域");
        }
    });
    $(".filter-item-bar>.filter-sort").on("click", "li", function (e) {
        if (!$(this).hasClass("active")) {
            $(this).addClass("active");
            $(this).siblings("li").removeClass("active");
            $(".filter-title-bar>.filter-title").eq(2).children("span").eq(0).html($(this).html());
        }
    })

})