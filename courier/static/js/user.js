//#############################################################################
//################# user-home.html ############################################
//#############################################################################





//#############################################################################
//################# user-delivery.html ########################################
//#############################################################################
var delivery = {};
var package_counter = 0;
var get_package_size = false;
var zone_division_name = "";
/*
    Wizard
*/
$(document).ready(function () {
    zone_division_name = $("#zone-division").html();
    //Initialize tooltips
    $('.nav-tabs > li a[title]').tooltip();

    //Wizard
    $('a[data-toggle="tab"]').on('show.bs.tab', function (e) {
        var $target = $(e.target);
        if ($target.parent().hasClass('disabled')) {
            return false;
        }
    });
});

/*
    Delivery Type Chooser
*/

$(function(){
	$('div.service-type').on('click', function(){
        delivery.service_type = $(this).find('.selective-option-radio').val();
        if(typeof delivery.report == 'undefined')
            delivery.report = {}
        delivery.report.service_type_name = $(this).find('.title').text();
        delivery.report.service_type_description = $(this).find('.description').text();
        // Wizard
        var $first = $( ".wizard .nav-tabs .nav-item:nth-child(1)" );
        var $second = $( ".wizard .nav-tabs .nav-item:nth-child(2)" );
        $first.removeClass('active')
        $first.removeClass('active-wizard');
        $second.removeClass('disabled');
        $second.children('a[data-toggle="tab"]').removeClass('disabled');
        $second.children('a[data-toggle="tab"]').addClass('active-wizard');
        $second.children('a[data-toggle="tab"]').click();
	});

	$('.step-two-btn').on('click', function(e){

        delivery.source_address = {}
        if(validateAddressFields("src")){
            set_delivery_source_address();
            // Wizard
            var $second = $( ".wizard .nav-tabs .nav-item:nth-child(2)" );
            var $third = $( ".wizard .nav-tabs .nav-item:nth-child(3)" );
            $second.removeClass('active')
            $second.removeClass('active-wizard');
            $third.removeClass('disabled');
            $third.children('a[data-toggle="tab"]').removeClass('disabled');
            $third.children('a[data-toggle="tab"]').addClass('active-wizard');
            $third.children('a[data-toggle="tab"]').click();
        }
        else{
            showMessage("field error","Please make sure all required fields are filled out!",5000);
        }
	});
	$('.step-three-btn').on('click', function(){
        // Wizard
        var $third = $( ".wizard .nav-tabs .nav-item:nth-child(3)" );
        var $forth = $( ".wizard .nav-tabs .nav-item:nth-child(4)" );
        $third.removeClass('active')
        $third.removeClass('active-wizard');
        $forth.removeClass('disabled');
        $forth.children('a[data-toggle="tab"]').removeClass('disabled');
        $forth.children('a[data-toggle="tab"]').addClass('active-wizard');
        $forth.children('a[data-toggle="tab"]').click();
        update_report();
	});
});

$(function(){
	$('div.selective-option').not('.disabled').find('div.selective-option-item').on('click', function(){
		$(this).parent().parent().find('div.selective-option-item').removeClass('selected');
		$(this).addClass('selected');
		$(this).find('.selective-option-radio').prop("checked", true);
	});
});

/*
    Sets and updates global delivery's pickup address object
*/
function set_delivery_source_address(){
    if(delivery.source_address == undefined){delivery.source_address = {}}
    delivery.source_address.city = $("#src-city").val();
    delivery.source_address.city_name = $("#src-city option:selected").text();
    delivery.source_address.province_name = $("#src-province option:selected").text();
    delivery.source_address.country_name = $("#src-country option:selected").text();
    delivery.source_address.address1 = $("#src-address1").val();
    delivery.source_address.address2 = $("#src-address2").val();
    delivery.source_address.zip = $("#src-zip").val();
    delivery.source_address.phone = $("#src-phone").val();
    delivery.source_address.fax = $("#src-fax").val();
    delivery.source_address.email = $("#src-email").val();
}

/*
    Package number and type chooser
*/
$('.package-fields-wrapper').each(function() {
    var $wrapper = $('.multi-fields', this);
    $(".add-field", $(this)).click(function(e) {
        $('.multi-field:first-child', $wrapper).clone(true).appendTo($wrapper).find('input').val('').focus();
    });
    $('.multi-field .remove-field', $wrapper).click(function() {
        if ($('.multi-field', $wrapper).length > 1)
            $(this).parent('.multi-field').remove();
    });
});

/*
    Map API for Source Address

var map,map2, infoWindow;
function initMap() {
  map = new google.maps.Map(document.getElementById("source-map"), {
    center: {lat: -34.397, lng: 150.644},
    zoom: 16,
    mapTypeId : google.maps.MapTypeId.ROADMAP
  });
  map2 = new google.maps.Map(document.getElementById("destination-map"), {
    center: {lat: -34.397, lng: 150.644},
    zoom: 16,
    mapTypeId : google.maps.MapTypeId.ROADMAP
  });

  infoWindow = new google.maps.InfoWindow;
  // Try HTML5 geolocation.
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(function(position) {
      var pos = {
        lat: position.coords.latitude,
        lng: position.coords.longitude
      };

      infoWindow.setPosition(pos);
      infoWindow.setContent('Location found.');
      infoWindow.open(map);
      infoWindow.open(map2);
      map.setCenter(pos);
      map2.setCenter(pos);
         var userMarker = new google.maps.Marker({
              position: pos,
              map: map,
              icon: 'http://www.robotwoods.com/dev/misc/bluecircle.png'
         });
           var userMarker2 = new google.maps.Marker({
              position: pos,
              map: map2,
              icon: 'http://www.robotwoods.com/dev/misc/bluecircle.png'
         });
    }, function() {
      handleLocationError(true, infoWindow, map.getCenter());
    });
  } else {
    // Browser doesn't support Geolocation
    handleLocationError(false, infoWindow, map.getCenter());
  }
}

function handleLocationError(browserHasGeolocation, infoWindow, pos) {
  infoWindow.setPosition(pos);
  infoWindow.setContent(browserHasGeolocation ?
                        'Error: The Geolocation service failed.' :
                        'Error: Your browser doesn\'t support geolocation.');
  infoWindow.open(map);
}
*/
      function initMap() {
        map = new google.maps.Map(document.getElementById('source-map'), {
          center: {lat: 37.5464634, lng: 45.038272},
          zoom: 18,
        });
        map2 = new google.maps.Map(document.getElementById('destination-map'), {
          center: {lat: -34.397, lng: 150.644},
          zoom: 8
        });
      }

/*


    Package with custom size
*/
$('#custom-size-submit-btn').click(function(){
    get_package_size = true;

    no_errors = true;
    weight = $('#custom-size-weight').val();
    if(!$.isNumeric(weight) | weight <= 0 ){
        $('#custom-size-weight').addClass("input-error")
        no_errors = false;
    }
    width = $('#custom-size-width').val();
    if(!$.isNumeric(width) | width <= 0 ){
        $('#custom-size-width').addClass("input-error")
        no_errors = false;
    }
    height = $('#custom-size-height').val();
    if(!$.isNumeric(height) | height <= 0 ){
        $('#custom-size-height').addClass("input-error")
        no_errors = false;
    }
    length = $('#custom-size-length').val();
    if(!$.isNumeric(length)  | length <= 0 ){
        $('#custom-size-length').addClass("input-error")
        no_errors = false;
    }
    if(no_errors){
        $('#custom-size-submit-btn').removeClass('disabled');
        $('#custom-size-submit-btn').attr("data-toggle","modal");
    }
    else {
        $('.show-error-msg').css("display","block");
        $('#custom-size-submit-btn').removeAttr("data-toggle");
    }

})
$('#custom-size-weight').focus(function(){
    $(this).removeClass("input-error");
    $('.show-error-msg').css("display","none");
})
$('#custom-size-width').focus(function(){
    $(this).removeClass("input-error");
    $('.show-error-msg').css("display","none");
})
$('#custom-size-height').focus(function(){
    $(this).removeClass("input-error");
    $('.show-error-msg').css("display","none");
})
$('#custom-size-length').focus(function(){
    $(this).removeClass("input-error");
    $('.show-error-msg').css("display","none");

})

/*
    Get the address from user address book
*/
$("#get-src-address").click(function(){
    var address_id = $("#address-for-src").val();
    $.ajax({
        url : '/user/ajax/get-user-address/',
        type : 'GET',
        data : {
            'address_id' : address_id,
        },
        success : function(data){
            if(data.result == "success"){
                set_address_fields(data, 'src');
            }

        }
    });
})

$("#get-destn-address").click(function(){
    var address_id = $("#addressbook-for-destn").val();
    $.ajax({
        url : '/user/ajax/get-user-address/',
        type : 'GET',
        data : {
            'address_id' : address_id,
        },
        success : function(data){
            if(data.result == "success"){
                set_address_fields(data, 'destn');
            }
        }
    });
});
/*
    Package Destination
*/
// Generating dynamic section to hold  chosen package template and the address
$("#add-package").click(function(){
        var valid_fields = validateAddressFields("destn")
        var share_tracking_sms = $("#share-tracking-sms").is(':checked');
        if(share_tracking_sms){
            phone = $("#destn-phone").val().trim();
            if(phone.length < 1){
                valid_fields = false;
                $("#destn-phone").addClass("input-error");
            }
        }
        var share_tracking_email = $("#share-tracking-email").is(':checked');
        if(share_tracking_email){
            email = $("#destn-email").val().trim();
            if(email.length < 1){
                valid_fields = false;
                $("#destn-email").addClass("input-error");
            }
        }
        var tracking_sharing_method = "";
        if(share_tracking_sms && share_tracking_email){
            tracking_sharing_method = "SMS and E-Mail";
        } else if(share_tracking_sms) {
            tracking_sharing_method = "SMS";
        } else if(share_tracking_email) {
             tracking_sharing_method = "E-mail";
        } else {
            tracking_sharing_method = "No sharing method!";
        }
    if(valid_fields){
        if(typeof delivery.packages == 'undefined')
            delivery.packages = {}
        delivery.packages[package_counter] = {}

        city = $("#destn-city").val();
        city_name = $("#destn-city option:selected").text();
        province_name = $("#destn-province option:selected").text();
        country_name = $("#destn-country option:selected").text();
        address1 = $("#destn-address1").val().trim();
        address2 = $("#destn-address2").val().trim();
        zip = $("#destn-zip").val().trim();
        phone = $("#destn-phone").val().trim();
        fax = $("#destn-fax").val().trim();
        email = $("#destn-email").val().trim();
        signature = $("#signature").is(':checked');
        if (signature){
            signature = "Yes";
        } else{
            signature = "No";
        }
        description = $("#package-description").val().trim();
        delivery.packages[package_counter].template_id = delivery.report.packageTemplate.id;
        delivery.packages[package_counter].package_title = delivery.report.packageTemplate.title;
        delivery.packages[package_counter].city = city;
        delivery.packages[package_counter].country_name = country_name;
        delivery.packages[package_counter].province_name = province_name;
        delivery.packages[package_counter].city_name = city_name;
        delivery.packages[package_counter].address1 = address1;
        delivery.packages[package_counter].address2 = address2;
        delivery.packages[package_counter].zip = zip;
        delivery.packages[package_counter].phone = phone;
        delivery.packages[package_counter].fax = fax;
        delivery.packages[package_counter].email = email;
        delivery.packages[package_counter].signature = $("#signature").is(':checked');
        delivery.packages[package_counter].description = description;
        delivery.packages[package_counter].share_tracking_sms = $("#share-tracking-sms").is(':checked') ;
        delivery.packages[package_counter].share_tracking_email = $("#share-tracking-email").is(':checked') ;

        if(get_package_size){
            delivery.packages[package_counter].size_weight = $("#custom-size-weight").val();
            delivery.packages[package_counter].size_width = $("#custom-size-width").val();
            delivery.packages[package_counter].size_height = $("#custom-size-height").val();
            delivery.packages[package_counter].size_length = $("#custom-size-length").val();
            get_package_size = false;
        }

        zone_division_name = $("#zone-division").html();
        if (address2.length > 0){address2 = address2 + ", "}
        if (phone.length > 0){phone = "<b>Phone: </b>" + phone + ", "}
        if (fax.length > 0){fax ="<b>Fax: </b>" + fax + ", "}
        if (email.length > 0){email ="<b>Email: </b>" + email}
        if (description.length < 1){ description = "No description"}
         package =` <div class="chosen-package">
                    <input type="hidden" value="${package_counter}" class="package-id">
                    <button type="button" class="close del-package" aria-label="Close">
                        <span aria-hidden="true">&times;</span>
                    </button>
                    <div class="row">
                      <div class="col-md-6" >
                          <span class="package-details-title">Package Type:&nbsp;</span>
                          <span>${ delivery.report.packageTemplate.title }</span>
                      </div>
                      <div class="col-md-6">
                           <span class="package-details-title">Signature required:&nbsp;</span>
                           <span>${signature}</span>
                      </div>
                    </div>
                    <hr/>
                    <div class="row">
                        <div class="col-md-12">
                            <span class="package-details-title">To Address:&nbsp;</span>
                            <span>${address2} ${address1}, ${city_name}, ${province_name}, ${country_name}, <b>${zone_division_name}:&nbsp;</b>${zip}</span><br/>
                            <span>${phone} ${fax} ${email}</span>
                        </div>
                    </div>
                    <hr/>
                    <div class="row">
                        <div class="col-md-12">
                            <span class="package-details-title">Description:&nbsp;</span>
                                ${description}
                            </span>
                        </div>
                        <div class="col-md-12">
                            <span class="package-details-title">Tracking code sharing method:&nbsp;</span>
                                ${tracking_sharing_method}
                            </span>
                        </div>
                    </div>
                </div>`;
        $("#package-container").append(package);
        package_counter++;
        $("#package-template-modal").modal("hide");
    } else {
        // TODO:show error message
    }
});

// If email checkbox for sharing tracking is checked make email field appearance required by adding *
$("#share-tracking-email").click(function(){
    var checked = $(this).is(':checked');
    if(checked){
        $('label[for=destn-email').append('<span class="star">*</span>');
    } else {
        $('label[for=destn-email').find(".star").remove();
    }
})

// If sms checkbox for sharing tracking is checked make phone field appearance required by adding *
$("#share-tracking-sms").click(function(){
    var checked = $(this).is(':checked');
    if(checked){
        $('label[for=destn-phone').append('<span class="star">*</span>');
    } else {
        $('label[for=destn-phone').find(".star").remove();
    }
})

$("#destn-phone").change(function(){
    $(this).removeClass("input-error");
})

$("#destn-email").change(function(){
    $(this).removeClass("input-error");
})

$('#package-template-modal').on('hidden.bs.modal', function () {
    get_package_size = false;
});

$(".package-template").click(function(){
    title = $(this).find(".title").text();
    id = $(this).find(".selective-option-radio").val();
    delivery.report.packageTemplate = {id:id, title:title};
});

// Remove
$("body").on("click",".del-package", function(){
    parentNod = $(this).parent();
    delete delivery.packages[parentNod.find(".package-id").val()];
    console.log(delivery);
    $(parentNod).remove();
})

/*
    Update last page of wizard
*/
$("body").on("click",".report-tab-link", function(){
    update_report();
})

function get_source_address(){
    src = {};
    src.state = $("#src-state").val();
    src.city = $("#src-city").val();
    src.address1 = $("#src-address1").val();
    src.address2 = $("#src-address2").val();
    src.zip = $("#src-zip").val();
    src.phone = $("#src-phone").val();
    src.fax = $("#src-fax").val();
    return src;

}

function update_report(){
    if(validateAddressFields("src")){
        set_delivery_source_address();
    } else {
        return
    }
    $(".delivery-type").text(delivery.report.service_type_name);
    src = delivery.source_address;
    var country = src.country_name + ", ";
    var province = src.province_name + ", ";
    var city = src.city_name + ", ";
    var address1 = src.address1 + ", ";
    var address2 = src.address2;
    var zip = "<b>" + zone_division_name + ":&nbsp;</b>" + src.zip + "<br / >";
    var phone = src.phone;
    var fax = src.fax;
    var email = src.email;
    address2 ? address2 += ", " : address2 = "";
    phone ? phone = "<b>Phone:&nbsp;</b>" + phone + ", " : phone = "";
    fax ? fax = "<b>Fax:&nbsp;</b>" + fax + ", " : fax = "";
    email ? email = "<b>E-Mail:&nbsp;</b>" + email : email = "";
    $(".source-address").html(address2 + address1 + city + province + country + zip + phone + fax + email);
    $(".tab-pane>dl>.packages").empty();
    package = "";

//console.log(delivery.packages.length());
//console.log(delivery.packages.length);
//    for (i = 0; i < delivery.packages.length; i++)  {
    for (var i in delivery.packages) {
        var package_title = delivery.packages[i].package_title;
        var country_name = delivery.packages[i].country_name + ", ";
        var province_name = delivery.packages[i].province_name + ", ";
        var city_name = delivery.packages[i].city_name + ", ";
        var address1 = delivery.packages[i].address1 + ", ";
        var address2 = delivery.packages[i].address2;
        var zip = delivery.packages[i].zip;
        var phone = delivery.packages[i].phone;
        var fax = delivery.packages[i].fax;
        var email = delivery.packages[i].email;
        if(delivery.packages[i].signature){
            signature = "YES";
        }else {
            signature = "NO";
        }
        var description = delivery.packages[i].description;
        var share_tracking_sms = delivery.packages[i].share_tracking_sms;
        var share_tracking_email = delivery.packages[i].share_tracking_email;
        var tracking_sharing_method = "";
        if(share_tracking_sms && share_tracking_email){
            tracking_sharing_method = "SMS and E-mail";
        } else if(share_tracking_sms) {
            tracking_sharing_method = "SMS";
        } else if(share_tracking_email) {
             tracking_sharing_method = "E-mail";
        } else {
            tracking_sharing_method = "No sharing method!";
        }
        zip = "<b>" + zone_division_name + ":&nbsp;</b>" + zip;
        address2 ? address2 += ", " : address2 = "";
        phone ? phone = "<b>Phone:&nbsp;</b>" + phone + ", " : phone = "";
        fax ? fax = "<b>Fax:&nbsp;</b>" + fax + ", " : fax = "";
        email ? email = "<b>E-mail:&nbsp;</b>" + email : email = "";
        if(!description) { description = "No description";}
         package +=`<div class="chosen-package">
                        <input type="hidden" value="${package_counter}" class="package-id">
                        <div class="row">
                          <div class="col-md-6" >
                              <span class="package-details-title">Package Type:&nbsp;</span>
                              <span>${ package_title }</span>
                          </div>
                          <div class="col-md-6">
                               <span class="package-details-title">Signature required:&nbsp;</span>
                               <span>${signature}</span>
                          </div>
                        </div>
                        <hr/>
                        <div class="row">
                            <div class="col-md-12">
                                <span class="package-details-title">To Address:&nbsp;</span>
                                <span>${address2} ${address1} ${city_name} ${province_name} ${country_name} ${zip}</span><br/>
                                <span>${phone} ${fax} ${email}</span>
                            </div>
                        </div>
                        <hr/>
                        <div class="row">
                            <div class="col-md-12">
                                <span class="package-details-title">Description:&nbsp;</span>
                                    ${description}
                                </span>
                            </div>
                            <div class="col-md-12">
                                <span class="package-details-title">Tracking code sharing method:&nbsp;</span>
                                    ${tracking_sharing_method}
                                </span>
                            </div>
                        </div>
                </div>`;
    }
   $(".tab-pane>dl>.packages").append(package);
}

$(".submit-delivery").click(function(){
    items = $(".packages").children(".chosen-package").length;
    if( items > 0 ){
        delete delivery.report;
        delivery_data = JSON.stringify(delivery);console.log(delivery_data);
            $.ajax({
                url: '/user/ajax/user-delivery/',
                type : 'GET',
                data : {
                    'delivery' : delivery_data,
                },
                success: function (data) {
                    console.log(data);
                    if(data["status"]=="success"){
                        window.location.replace(data["redirect"]);
                    }else{
                        alert("Failed: " + data.message);
                    }
                },
                error : function(){
                    alert("Error in establishing connection to server.")
                }
            });
    } else {
        showMessage("no package!","Please go back and add at least one package",10000000);
    }
})

$(".round-tab").on("click",function(e){
    update_report();
    valid = validateAddressFields();
    if(!valid){
        $(this).parent().removeClass("active");
    }

})

$("#clear-src-address").click(function(e){
    e.preventDefault();
    $("#address-for-src").val(0);
    clear_address_fields("src");
})

$("#clear-destn-address").click(function(e){
    e.preventDefault();
    $("#addressbook-for-destn").val(0);
    clear_address_fields("destn");
})


//#############################################################################
//################# user-delivery-report.html #################################
//#############################################################################

// Hides and Shows details of a package
$(".expand-collapse").click(function(){
    $(this).find('i').toggleClass('fa-expand fa-compress');
    $(this).parents().eq(3).find('.hideable').toggleClass('hidden');
    var btn_text = $(this).find(".btn-text").html()
    btn_text == "More Details" ? btn_text = "Less Details" : btn_text = "More Details";
    $(this).find(".btn-text").html(btn_text);
})


//#############################################################################
//################# user-tracking.html ########################################
//#############################################################################

$(".cancel-request").click(function(){
    $("#do-cancel-request").val($(this).val());
    $("#cancelRequestModal").modal("show");
})

$("#do-cancel-request").click(function(){
    value = $(this).val();
    delivery_id = value.split(":")[0]
    action = value.split(":")[1]
    $.ajax({
        url: "/user/ajax/cancel-delivery-request/",
        type: "Get",
        data: {
            "delivery_id": delivery_id
        },
        success: function(data){
            if (data.result == "success"){
                location.reload(true);
            }
        }
    });

})

$(".cancel-action").click(function(){
    value = $(this).val();
    str_list = value.split('_');
    action = str_list[str_list.length - 1];
    if(action == "dispatch"){
        action = "pick up";
    }
    $("#do-cancel-pickupHandover").val($(this).val());
    $("#cancelPackageModal").find(".modal-title").html(capitalize(action) + " Cancellation");
    $("#cancelPackageModal").find(".confirm-message").html("Do you want to cancel this package " + action);
    $("#do-cancel-pickupHandover").html("Cancel " + capitalize(action));
    $("#cancelPackageModal").modal("show");
})

$("#do-cancel-pickupHandover").click(function(){
    value = $(this).val();
    value_list = value.split(":");
    package_id = value_list[0];
    action = value_list[1];
    $.ajax({
        url: "/user/ajax/cancel-pickup-or-handover/",
        type: "Get",
        data: {
            "package_id": package_id,
            "action": action
        },
        success: function(data){
            if(data.result == "success"){
                location.reload(true);
            } else{
                alert("Failure!!")
            }
        }
    });
})


//#############################################################################
//################# user-address-book.html ####################################
//#############################################################################

$('.confirm-delete').on('click', function(){
    var addressBook_id = $(this).data("addressid");
    var title = $("#title" + addressBook_id).text();
    $("#do-delete-address").val(addressBook_id);
    $("#address-to-delete-title").text(title);
    $("#addressDeleteModal").modal("show");
})

$("#do-delete-address").click(function(){
    var addressBook_id = $(this).val();
    $.ajax({
        url:'/user/ajax/delete-user-address/',
        type: 'GET',
        data : {
            'address_id': addressBook_id,
        },
        success : function(data){
            if(data.result == "success"){
                window.location.reload();
            }else {
                alert ("Operation failed!");
            }
        },
        error : function(){
             alert("Connection Error!");
        }
    });
})

$("#addressModal").on("hidden.bs.modal", function () {
    $(".address-form").find(".input-error").removeClass("input-error");
});


$("#open-address-modal").click(function(){
    $("ul.address").find(".highlighted").removeClass("highlighted");
    $("#do-add-update-address").html("Save");
    $("#do-add-update-address").val('add:0');
    clear_address_fields("address");
    $("#addressModal").modal({
        backdrop: 'static',
    });
})


$("#do-add-update-address").click(function(){
    var value = $(this).val();
    var action = value.split(":")[0];
    var id = value.split(":")[1];
    addUpdateAddress(action, id);
})

$(".edit-address").click(function(){
    $("ul.address").find(".highlighted").removeClass("highlighted");
    $("#do-add-update-address").html("Update");
    var address_id = $(this).data('addressid');
    $("#do-add-update-address").val('update:' + address_id );
    $.ajax({
        url : '/user/ajax/get-user-address/',
        type : 'GET',
        data : {
            'address_id' : address_id,
        },
        success : function(data){
            set_address_fields(data, 'address');
            $("#do-add-update-address").html("Update");
            $("#addressModal").modal('show');
        }
    });
})

$(get_address_field_ids()).change(function(){
    $(this).removeClass("input-error");
})

//#############################################################################
//################# Helper function ###########################################
//#############################################################################

function showMessage(msg_title, msg_body, delay_time=60*1000){
    $("#message-modal").find(".modal-title").text(msg_title);
    $("#message-modal").find(".modal-body").text(msg_body);
    $("#message-modal").modal('show');
    setTimeout(function(){
        $("#message-modal").modal('hide');
    },delay_time)

}


$('.address_item').change(function(){
    var id = $(this).attr('id');
    var id_first_part = "#"+id.split("-")[0]+"-";
    var id_second_part = id.split("-")[1]
    if(id_second_part == "country"){
        if (this.value == 0){
            $(id_first_part + "province").find('option').remove('option');
            $(id_first_part + "province").append('<option value="0">Select province ...<option>');
            $(id_first_part + "city").find('option').remove('option');
            $(id_first_part + "city").append('<option value="0">Select city ...<option>');
            return
        }
        $(id_first_part + "province").removeClass("input-error");
        country_id = this.value;
        $.ajax({
            url: '/user/ajax/get-provinces/',
            type : 'GET',
            data : {
                'country_id' : country_id,
            },
            success: function (data) {
                $(id_first_part + "city").find('option').remove('option');
                $(id_first_part + "city").append('<option value="0">Select city ...<option>');
                $(id_first_part + "province").find('option').remove('option');
                for (var key in data) {
                    // check if the property/key is defined in the object itself, not in parent
                    if (data.hasOwnProperty(key)) {
                        $(id_first_part + "province").append($('<option>', {
                        value: key,
                        text: data[key],
                        }));
                    }
                }
                if(Object.keys(data).length == 1) {
                    for (var key in data) break;
                    $.ajax({
                        url: '/user/ajax/get-cities/',
                        type : 'GET',
                        data : {
                            'province_id' : key,
                        },
                        success: function (data) {
                            $(id_first_part + "city").find('option').remove('option');
                            for (var key in data) {
                                // check if the property/key is defined in the object itself, not in parent
                                if (data.hasOwnProperty(key)) {
                                    $(id_first_part + "city").append($('<option>', {
                                    value: key,
                                    text: data[key],
                                    }));
                                }
                            }
                        },
                        error : function(){
                            alert("Error in establishing connection to server.")
                        }
                    });

                }
            },
            error : function(){
                alert("Error in establishing connection to server.")
            }
        });
    }
    else if(id_second_part == "province"){
        if (this.value == 0){
            $(id_first_part + "city").find('option').remove('option');
            $(id_first_part + "city").append('<option value="0">Select city ...<option>');
            return
        }
        province_id = this.value;
        $.ajax({
            url: '/user/ajax/get-cities/',
            type : 'GET',
            data : {
                'province_id' : province_id,
            },
            success: function (data) {
                $(id_first_part + "city").find('option').remove('option');
                for (var key in data) {
                    // check if the property/key is defined in the object itself, not in parent
                    if (data.hasOwnProperty(key)) {
                        $(id_first_part + "city").append($('<option>', {
                        value: key,
                        text: data[key],
                        }));
                    }
                }
            },
            error : function(){
                alert("Error in establishing connection to server.")
            }
        });
    }
})

function clear_address_fields(id_prefix){
    var id_prefix = "#" + id_prefix + "-";
    $(id_prefix + "title").val("");
    $(id_prefix + "country").val(0);
    $(id_prefix + "province").find('option').remove('option');
    $(id_prefix + "province").append('<option value="0">Select province ...</option>');
    $(id_prefix + "city").find('option').remove('option');
    $(id_prefix + "city").append('<option value="0">Select city ...</option>');
    $(id_prefix + "address1").val("");
    $(id_prefix + "address2").val("");
    $(id_prefix + "zip").val("");
    $(id_prefix + "phone").val("");
    $(id_prefix + "fax").val("");
    $(id_prefix + "email").val("");
}

function set_address_fields(data, id_prefix){
    var id_prefix = "#" + id_prefix + "-";
    $(id_prefix + "country").find('option').remove('option');
    for(var key in data.countries){
        $(id_prefix + "country").append($('<option>', {
        value: key,
        text: data.countries[key],
        }));
    }
    $(id_prefix + "country").val(data['selected-country-id']);

    $(id_prefix + "province").find('option').remove('option');
    for(var key in data.provinces){
        $(id_prefix + "province").append($('<option>', {
        value: key,
        text: data.provinces[key],
        }));
    }
    $(id_prefix + "province").val(data['selected-province-id']);

    $(id_prefix + "city").find('option').remove('option');
    for(var key in data.cities){
        $(id_prefix + "city").append($('<option>', {
        value: key,
        text: data.cities[key],
        }));
    }
    $(id_prefix + "city").val(data['selected-city-id']);

    $(id_prefix + "title").val(data.title);
    $(id_prefix + "address1").val(data.address1);
    $(id_prefix + "address2").val(data.address2);
    $(id_prefix + "zip").val(data.zip);
    $(id_prefix + "phone").val(data.phone);
    $(id_prefix + "fax").val(data.fax);
    $(id_prefix + "email").val(data.email);
}

function addUpdateAddress(action='add', address_id=0){
    var title = $("#address-title").val().trim();
    var country = $("#address-country").val();
    var province = $("#address-province").val();
    var city = $("#address-city").val();
    var address1 = $("#address-address1").val().trim();
    var address2 = $("#address-address2").val().trim();
    var zip = $("#address-zip").val().trim();
    var phone = $("#address-phone").val().trim();
    var fax = $("#address-fax").val().trim();
    var email = $("#address-email").val().trim();
    var valid_fields = true;
    if( title.length < 1 ){ valid_fields = false; $("#address-title").addClass("input-error"); }
    if( country < 1 ) { valid_fields = false; $("#address-country").addClass("input-error")}
    if( province < 1 ) { valid_fields = false; $("#address-province").addClass("input-error")}
    if( city < 1 ) { valid_fields = false; $("#address-city").addClass("input-error")}
    if( address1.length < 1 ) { valid_fields = false; $("#address-address1").addClass("input-error")}
    if( zip.length < 1 ) { valid_fields = false; $("#address-zip").addClass("input-error")}
    if(email.length > 1 ){
        if(!validateEmail(email)){ valid_fields = false; $("#address-email").addClass("input-error")}
    }
    if (valid_fields){
        $("#addressModal").modal('hide');
        $.ajax({
            url: '/user/ajax/add-update-address/',
            type: 'GET',
            data:{
                'address_data' : JSON.stringify({
                    'action': action,
                    'address-id': address_id,
                    'title': title,
                    'country': country,
                    'province': province,
                    'city': city,
                    'address1': address1,
                    'address2': address2,
                    'zip': zip,
                    'phone': phone,
                    'fax': fax,
                    'email': email
                })
            },
            success : function(data){
                if(data.error.length > 0 ){
                    alert(data.error);
                    $("#address-row-" + data.address_id).addClass("highlighted");
                    $([document.documentElement, document.body]).animate({
                        scrollTop: $("#address-row-" + data.address_id).offset().top
                    }, 1000);
                }
                else {
                    window.location.reload();
                }
            },
            error : function(){

            }
        });
    }
}

function get_address_field_ids(){
    var fields = ['title', 'country', 'province', 'city', 'address1', 'zip', 'email' ];
    var target_ids = "";
    fields.forEach(function(item, index){
       target_ids += "#address-" + item + ",#src-" + item + ",#destn-" + item;
       if( index != fields.length - 1){target_ids += ','}
    })
    return target_ids
}

/*
    Validation of destination address fields
*/
function validateAddressFields(id_prefix) {
    var has_no_error = true;
    id_prefix = "#" + id_prefix + "-";
    $(".input-error").removeClass("input-error");
    city = $(id_prefix + "city").val();
    address1 = $.trim($(id_prefix + "address1").val());
    zip = $.trim($(id_prefix + "zip").val());
    email = $.trim($(id_prefix + "email").val());

    if (id_prefix == "address") {
        title = $.trim($(id_prefix + "title").val());
        if (title.length < 1){
            has_no_error = false;
            $('#address-title').addClass("input-error");
        }
    }
    if (city < 1) {
        has_no_error = false;
      $(id_prefix + "city").addClass("input-error");
    }
    if (address1.length < 1) {
        has_no_error = false;
      $(id_prefix + "address1").addClass("input-error");
    }
    if (zip.length < 1) {
        has_no_error = false;
        $(id_prefix + "zip").addClass("input-error");
    }
    if (email.length > 0 ) {
        if (!validateEmail(email)){
            has_no_error = false;
            $(id_prefix + "email").addClass("input-error");
        }
    }
    return has_no_error;
}

function validateEmail(Email) {
    var filter = /^([\w-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([\w-]+\.)+))([a-zA-Z]{2,4}|[0-9]{1,3})(\]?)$/;
    if (filter.test(Email)) {
        return true;
    }
    else {
        return false;
    }
}

function capitalize(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}