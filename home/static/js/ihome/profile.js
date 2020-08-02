function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function () {
        setTimeout(function () {
            $('.popup_con').fadeOut('fast', function () {
            });
        }, 1000)
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(document).ready(function () {
    $("#form-avatar").submit(function (e) {
        // 组织默认行为
        e.preventDefault();
        // 利用query.form.min.js提供akaxSubmit对表单进行异步提交
        $(this).ajaxSubmit({
            url: "/api/v1.0/users/avatar",
            type: "post",
            dataType: "json",
            handlers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            success: function (resp) {
                if (resp.error == "0") {
                    // 上传成功
                    var avatarUrl = resp.data.avatar_url;
                    $("#user-avatar").attr("src", avatarUrl);
                } else {
                    alert(resp.errmsg)
                }

            }
        })
    })
});
