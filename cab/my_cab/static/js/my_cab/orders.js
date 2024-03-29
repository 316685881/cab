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

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function(){
    $('.modal').on('show.bs.modal', centerModals);      //当模态框出现的时候
    $(window).on('resize', centerModals);

    $.get('/api/v1.0/user/orders', function (resp) {
        if (resp.errno == '0') {
            $('.orders-list').html(template('orders-list-tmpl', {orders: resp.data.orders}));

            $('.order-pay').on('click', function (e) {
                var order_id = $(this).parents('li').attr('order-id');

                var data = {
                    order_id:order_id
                };
                $.ajax({
                    url:'/api/v1.0/order/payment',
                    type:'post',
                    data: JSON.stringify(data),
                    contentType: 'application/json',
                    dataType: 'json',
                    headers: {"X-CSRFToken":getCookie("csrf_token")},
                    success: function (resp) {
                        if (resp.errno == '4101'){
                            location.href = '/login.html'
                        } else if (resp.errno == '0') {
                            location.href = resp.data.pay_url
                        } else {
                            alert(resp.errmsg)
                        }
                    }
                });
            });

            $(".order-comment").on("click", function() {
                var orderId = $(this).parents("li").attr("order-id");
                $(".modal-comment").attr("order-id", orderId);
            });
            $('.modal-comment').on('click', function () {
                var order_id = $(".modal-comment").attr("order-id");
                var comment = $('#comment').val();
                var data = {
                    order_id:order_id,
                    comment: comment
                }

                $.ajax({
                    url:'/api/v1.0/order/comment',
                    type:'put',
                    data:JSON.stringify(data),
                    contentType:'application/json',
                    dataType:'json',
                    headers:{"X-CSRFToken": getCookie("csrf_token")},
                    success: function (resp) {
                        if (resp.errno == '0') {
                            $('#comment-modal').modal('hide');
                            location.href = '/orders.html'
                        } else {
                            alert(resp.errmsg)
                        }
                    }

                })

            })
        }
        else if (resp.errno == '4101') {
            location.href = '/login.html'
        } else {
            alert(resp.errmsg)
        }
    })
});


