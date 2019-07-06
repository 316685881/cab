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

function decodeQuery(){
    var search = decodeURI(document.location.search);
    return search.replace(/(^\?)/, '').split('&').reduce(function(result, item){
        values = item.split('=');
        result[values[0]] = values[1];
        return result;
    }, {});
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function(){
    // 检查用户的登录状态
    $.get("/api/v1.0/session", function (resp) {
        if ("4101" == resp.errno) {
            location.href = '/login.html'
        }
    });

    $('.modal').on('show.bs.modal', centerModals);      //当模态框出现的时候
    $(window).on('resize', centerModals);

    var result = decodeQuery();
    var role = result['role'];
    $.get('/api/v1.0/user/orders?role='+role, function (resp) {
        if (resp.errno == '0') {
            $('.orders-list').html(template('orders-list-tmpl', {orders: resp.data.orders}));
            $(".order-accept").on("click", function(){
                var order_id = $(this).parents("li").attr("order-id");
                $(".modal-accept").attr("order-id", order_id);
            });
            $(".modal-accept").on("click", function(){
                var order_id = $(this).attr("order-id");
                var data = {
                    action:'accept',
                    order_id: order_id
                };
                $.ajax({
                    url: '/api/v1.0/order/status',
                    type: 'put',
                    data: JSON.stringify(data),
                    contentType: 'application/json',
                    dataType: 'json',
                    headers: {"X-CSRFToken":getCookie("csrf_token")},
                    success: function (resp) {
                        if (resp.errno == '0') {
                            // alert(resp.errmsg);

                            $('#accept-modal').modal('hide');
                            location.href = '/lorders.html?role=role'
                            // $(".order-list>li[order_id="+ order_id +"]>div.order-content>div.order-text>ul li:eq(4)>span").html('等待支付');
                            // $('.order-list>li[order_id='+ order_id +']>div.order-title>div#operate-div>').hide();
                            // $('.order-list>li[order_id='+ order_id +']>div.order-title>div#accept-div>h3').html('已接单').show();
                        }
                    }
                });
            });
            //        拒单
            $(".order-reject").on("click", function(){
                var order_id = $(this).parents("li").attr("order-id");
                $(".modal-reject").attr("order-id", order_id);
            });
            $(".modal-reject").on("click", function(){
                var order_id = $(this).attr("order-id");
                var reason = $('#reject-reason').val();
                var data = {
                    action:'reject',
                    order_id: order_id,
                    reject_reason: reason
                };
                $.ajax({
                    url: '/api/v1.0/order/status',
                    type: 'put',
                    data: JSON.stringify(data),
                    contentType: 'application/json',
                    dataType: 'json',
                    headers: {"X-CSRFToken":getCookie("csrf_token")},
                    success: function (resp) {
                        if (resp.errno == '0') {
                            // alert(resp.errmsg);
                            $('#reject-modal').modal('hide');
                            location.href = '/lorders.html?role=role'
                            // $(".order-list>li[order_id="+ order_id +"]>div.order-content>div.order-text>ul li:eq(4)>span").html('已拒单');
                            // $('.order-list>li[order_id='+ order_id +']>div.order-title>div#operate-div>').hide();
                            // $('.order-list>li[order_id='+ order_id +']>div.order-title>div#reject-div>h3').html('已拒单');

                        } else if (resp.errno == '4101') {
                            location.href = '/login.html'
                        }else {
                            alert(resp.errmsg)
                        }
                    }
                });
            });


                }
                else if (resp.errno == '4101') {
                    location.href = '/login.html'
                }else {
                    alert(resp.errmsg)
                }
            });





});