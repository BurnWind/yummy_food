$(function(){
    var allow = true
    $('#send_icode').click(function(e){
        e.preventDefault()
        if(allow){
            var phone = $('#phone').val()
            if (phone.length==11){
                allow = false
                $(this).css('background-color','#ccc')
                setTimeout(function(){
                    allow = true
                    $('#send_icode').css('background-color','white')
                },60000)
                $.ajax({
                    url:'/get_icon',
                    method:'post',
                    dataType:'json',
                    data:{"sphone":phone},
                    success:function(data){
                        alert(data)
                    },
                })
            }else{
                alert('手机号码必须为11位')
            }
        }
    })
    $('#subm').click(function(e){
        var yan = true
        e.preventDefault()
        var phone = $('#phone').val()
        if(phone.length != 11){
            alert('手机号码必须为11位')
            yan = false
        }else if(!$(".p2 input[name=sname]").val()){
            alert('用户名不能为空')
            yan = false
        }else if($(".p2 input[name=spwd]").val() != $(".p2 input[name=cpwd]").val()){
            alert('两次密码输入不一致')
            yan = false
        }else if($(".p2 input[name=spwd]").val().length<6){
            alert('密码长度必须大于等于6位')
            yan = false
        }else if(!$('#icode').val()){
            alert('验证码不能为空')
            yan = false
        }else{
            yan = true
        }
        if(yan){
            $.ajax({
                url:'/register',
                method:'post',
                dataType:'text',
                data:$('#form').serialize(),
                success:function(data){
                    alert(data)
                    location.href='/login'
                },
                error:function(data){
                    alert(data.responseText)
                }
            })
        }
    })
})