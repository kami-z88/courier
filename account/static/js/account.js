/*
    profile-sidebar.html page
*/
$(".upload-image-cover").click(function(){
    $(".upload-image").trigger("click");
})

$(".toggle-upload").click(function(){
    $("li.upload-container").toggle("hidden");
    $("#upload-input").val("");
})

$(".toggle-password").click(function(){
    $("li.password-container").toggle("hidden");
    $(".form-control.pass1").val("");
    $(".form-control.pass2").val("");
    $("li.password-container").find(".error-message").html("");
    $("li.password-container").find(".error-message").addClass("hidden");
    $("li.password-container").find(".success-message").html("");
    $("li.password-container").find(".success-message").addClass("hidden");
})

$(".btn-change-password").click(function(){
    $("li.password-container").find(".error-message").html("");
    $("li.password-container").find(".error-message").addClass("hidden");
    $("li.password-container").find(".success-message").html("");
    $("li.password-container").find(".success-message").addClass("hidden");
    var pass1 = $(".form-control.pass1").val().trim();
    var pass2 = $(".form-control.pass2").val().trim();
    var user_id = $(this).val();
    csrf_token = $("li.password-container").find("input[name=csrfmiddlewaretoken]").val();
    var error = null;
    if( pass1.length < 8 ){
        error = "Your password should be at least 8 characters";
    } else if ( pass1 != pass2 ){
        error = "Password and Confirm don't match!";
    }
    if( error ){
        $("li.password-container").find(".error-message").html(error);
        $("li.password-container").find(".error-message").removeClass("hidden");
    } else {
        $.ajax({
            url:'/account/ajax/change-password/',
            type:'Post',
            data: {
                "userId": user_id,
                "csrfmiddlewaretoken": csrf_token,
                "pass1": pass1,
                "pass2": pass2,
            },
            success: function(data){
                if(data.error){
                    alert(data.error);
                } else {
                    if(data.result == "success"){
                        var message = 'Password changed <i class="fas fa-check"></i>';

                        $("li.password-container").find(".success-message").html(message);
                        $("li.password-container").find(".success-message").removeClass("hidden");
                    }else{
                        alert(data.result);
                    }
                }
            },
            error: function(){
                alert("ERROR!");
            }
        });
    }
})

$(".upload-image").change(function(){
    profile_image_file = this.files[0];
    var image_file_name = $(this).val();
    var file_name = image_file_name.replace(/^.*[\\\/]/, '');
    $("#upload-input").val(file_name);
    file_size = this.files[0].size;
})

$(".btn-upload").click(function(){
    var form_data = new FormData();
    csrfmiddlewaretoken = $("#upload-image-csrf").val();
    form_data.append("image", profile_image_file);
    form_data.append("csrfmiddlewaretoken", csrfmiddlewaretoken);
    $.ajax({
        url: '/account/ajax/upload-profile-photo/',
        type: 'Post',
        data: form_data,
        processData: false,
        contentType: false,
        success: function(data){
            alert(data.filename)
        }
    });
})

$("#open-delete-image-modal").click(function(){
    var profile_id = $(this).val();
    $("#do-delete-image").val(profile_id);
    $("#deleteImageModal").modal('show');
})

$("#do-delete-image").click(function(){
    var profile_id = $(this).val();
    $.ajax({
        url: '/account/ajax/delete-user-photo/',
        type: 'Get',
        data: {
            "profileId": profile_id,
        },
        success: function(data){
            location.reload(true);
        }
    });
})

