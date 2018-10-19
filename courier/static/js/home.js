$("#do-track").click(function(){
     code = $("#track-code").val()
    $.ajax({
        url:'/home/ajax/visitor-tracking/',
        type:'GET',
        data:{
        "code" : code,
        },
        success: function(data){
            if(!data.error){
                $("#status").text(data.status)
                $("#sender").text(data.sender)
                $("#signer").text(data.signer)
                $("#deliver-time").text(data.deliver_time)
                $("#trackingModal").modal('show')
            }
            else{
                alert(data.error)
            }

        }

    })
})