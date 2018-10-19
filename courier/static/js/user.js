//#############################################################################
//################# user-home.html ############################################
//#############################################################################





//#############################################################################
//################# user-delivery.html ########################################
//#############################################################################
var delivery = {};
var package_counter = 0;
var get_package_size = false;
/*
    Wizard
*/
$(document).ready(function () {
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
        if(validateSourceFields()){
            delivery.source_address.state = $("#src-state").val();
            delivery.source_address.city = $("#src-city").val();
            delivery.source_address.address1 = $("#src-address1").val();
            delivery.source_address.address2 = $("#src-address2").val();
            delivery.source_address.zip = $("#src-zip").val();
            delivery.source_address.phone = $("#src-phone").val();
            delivery.source_address.fax = $("#src-fax").val();

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
    addrID = $("#addressbook-for-src").val();
        $.ajax({
            url: '/user/ajax/get-address/',
                type : 'GET',
                data : {
                'id' : addrID,
            },
            success: function (data) {
                $("#src-state").val(data.state);
                $("#src-city").val(data.city);
                $("#src-address1").val(data.address1);
                $("#src-address2").val(data.address2);
                $("#src-zip").val(data.zip);
                $("#src-phone").val(data.phone);
                $("#src-fax").val(data.fax);
                validateSourceFields();

            },
            error : function(){

            }
        });
})

$("#get-destn-address").click(function(){
    addrID = $("#addressbook-for-destn").val();
        $.ajax({
            url: '/user/ajax/get-address',
            type : 'GET',
            data : {
            'id' : addrID,
            },
            success: function (data) {
                $("#destn-state").val(data.state);
                $("#destn-city").val(data.city);
                $("#destn-address1").val(data.address1);
                $("#destn-address2").val(data.address2);
                $("#destn-zip").val(data.zip);
                $("#destn-phone").val(data.phone);
                $("#destn-fax").val(data.fax);
                validateDestinationAddressFields();
            },
            error : function(){

            }
        });
});
/*
    Package Destination
*/
// Generating dynamic section to hold  chosen package template and the address
$("#add-package").click(function(){
    if(validateDestinationAddressFields()){
        if(typeof delivery.packages == 'undefined')
            delivery.packages = {}
        delivery.packages[package_counter] = {}

        state = $("#destn-state").val();
        city = $("#destn-city").val();
        address1 = $("#destn-address1").val();
        address2 = $("#destn-address2").val();
        zip = $("#destn-zip").val();
        phone = $("#destn-phone").val();
        fax = $("#destn-fax").val();
        signature = $("#signature").is(':checked');
        if (signature){
            signature = "YES";
        } else{
            signature = "NO";
        }
        delivery.packages[package_counter].template_id = delivery.report.packageTemplate.id;
        delivery.packages[package_counter].package_title = delivery.report.packageTemplate.title;
        delivery.packages[package_counter].state = state;
        delivery.packages[package_counter].city = city;
        delivery.packages[package_counter].address1 = address1;
        delivery.packages[package_counter].address2 = address2;
        delivery.packages[package_counter].zip = zip;
        delivery.packages[package_counter].phone = phone;
        delivery.packages[package_counter].fax = fax;
        delivery.packages[package_counter].signature = $("#signature").is(':checked');

        if(get_package_size){
            delivery.packages[package_counter].size_weight = $("#custom-size-weight").val();
            delivery.packages[package_counter].size_width = $("#custom-size-width").val();
            delivery.packages[package_counter].size_height = $("#custom-size-height").val();
            delivery.packages[package_counter].size_length = $("#custom-size-length").val();
            get_package_size = false;
        }

         package =` <div class="chosen-package">
                    <input type="hidden" value="${package_counter}" class="package-id">
                    <button type="button" class="close del-package" aria-label="Close">
                        <span aria-hidden="true">&times;</span>
                    </button>
                    <div class="row">
                      <div class="col-md-6" >
                          <span class="package-details-title">PACKAGE TYPE:&nbsp;</span>
                          <span>${ delivery.report.packageTemplate.title }</span>
                      </div>
                      <div class="col-md-6">
                           <span class="package-details-title">SIGNATURE REQUIRED:&nbsp;</span>
                           <span>${signature}</span>
                      </div>
                    </div>
                    <hr/>
                    <div class="row">
                        <div class="col-md-12">
                            <span class="package-details-title">TO ADDRESS:&nbsp;</span>
                            <span>Zip:${zip}, ${address1}, ${city}, ${state}</span><br/>
                            <span>${address2}  Phone: ${phone}, Fax:${fax}</span>
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
    $(".delivery-type").text(delivery.report.service_type_name);

    src = get_source_address();
    if(! src.address2){src.address2="none";}
    $(".source-address").text("Address2: "+ src.address2 + " | Address1: " + src.address1 + " | City: " + src.city + " | State: " + src.state + " | Zip: " + src.zip + " | Phone: " + src.phone + " | Fax: " + src.fax );
    $(".tab-pane>dl>.packages").empty();
    package = "";

//console.log(delivery.packages.length());
//console.log(delivery.packages.length);
//    for (i = 0; i < delivery.packages.length; i++)  {
    for (var i in delivery.packages) {
        //console.log(delivery.packages[i]);
        if(delivery.packages[i].signature){
            signature = "YES";
        }else {
            signature = "NO";
        }
        package +=` <div class="chosen-package">
                   <div class="row">
                     <div class="col-md-6" >
                         <span class="package-details-title">PACKAGE TYPE:&nbsp;</span>
                         <span>${ delivery.packages[i].package_title }</span>
                     </div>
                     <div class="col-md-6">
                          <span class="package-details-title">SIGNATURE REQUIRED:&nbsp;</span>
                          <span>${signature}</span>
                     </div>
                   </div>
                   <hr/>
                   <div class="row">
                       <div class="col-md-12">
                           <span class="package-details-title">TO ADDRESS:&nbsp;</span>
                           <span>Zip:${delivery.packages[i].zip}, ${delivery.packages[i].address1}, ${delivery.packages[i].city}, ${delivery.packages[i].state}</span><br/>
                           <span>${delivery.packages[i].address2}  Phone: ${delivery.packages[i].phone},Fax: ${delivery.packages[i].fax}</span>
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
        delivery_data = JSON.stringify(delivery);
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
                        alert("Error in submiting the delivery request!")
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

/*
    Validation of source address fields
*/
function validateSourceFields() {
    var has_no_error = true;
    $(".field-error").removeClass("field-error");
    state = $.trim($('#src-state').val());
    city = $.trim($('#src-city').val());
    address1 = $.trim($('#src-address1').val());
    zip = $.trim($('#src-zip').val());

    if (state.length < 1) {
        has_no_error = false;
        $('#src-state').addClass("field-error");
    }
    if (city.length < 1) {
        has_no_error = false;
      $('#src-city').addClass("field-error");
    }
    if (address1.length < 1) {
        has_no_error = false;
      $('#src-address1').addClass("field-error");
    }
    if (zip.length < 1) {
        has_no_error = false;
        $('#src-zip').addClass("field-error");
    }
    return has_no_error;
}

/*
    Validation of destination address fields
*/
function validateDestinationAddressFields() {
    var has_no_error = true;
    $(".field-error").removeClass("field-error");
    state = $.trim($('#destn-state').val());
    city = $.trim($('#destn-city').val());
    address1 = $.trim($('#destn-address1').val());
    zip = $.trim($('#destn-zip').val());

    if (state.length < 1) {
        has_no_error = false;
        $('#destn-state').addClass("field-error");
    }
    if (city.length < 1) {
        has_no_error = false;
      $('#destn-city').addClass("field-error");
    }
    if (address1.length < 1) {
        has_no_error = false;
      $('#destn-address1').addClass("field-error");
    }
    if (zip.length < 1) {
        has_no_error = false;
        $('#destn-zip').addClass("field-error");
    }
    return has_no_error;
}

$(".round-tab").on("click",function(e){
    valid = validateSourceFields();
    if(!valid){
        $(this).parent().removeClass("active");
    }

})

$("#clear-src-address").click(function(e){
    e.preventDefault();
    $("#src-address1, #src-address2, #src-zip, #src-phone, #src-fax").val("");
})

$("#clear-destn-address").click(function(e){
    e.preventDefault();
    $("#destn-address1, #destn-address2, #destn-zip, #destn-phone, #destn-fax").val("");
    $("#signature").prop("checked", false);
})

//#############################################################################
//################# user-delivery-report.html #################################
//#############################################################################


//#############################################################################
//################# user-tracking.html ########################################
//#############################################################################

$(document).ready(function () {
    $('#tracking-table').DataTable();
});




//#############################################################################
//################# user-address-book.html ####################################
//#############################################################################

$('.confirm-delete').on('click', function(){
    return confirm('Are you sure you want to delete this address?');
})

//#############################################################################
//################# user-add-address.html #####################################
//#############################################################################


//#############################################################################
//################# user-edit-address.html ####################################
//#############################################################################



//#############################################################################
//################# Helper function ###########################################
//#############################################################################

function showMessage(msg_title, msg_body, delay_time=60*1000){
    $("#show-message-modal").find(".modal-title").text(msg_title);
    $("#show-message-modal").find(".modal-body").text(msg_body);
    $("#show-message-modal").modal('show');
    setTimeout(function(){
        $("#show-message-modal").modal('hide');
    },delay_time)

}
