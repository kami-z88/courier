$(document).ready(function(){
     /*
        Automatically check delivery table in the database every x millisecond
        to reload page if any new row
    */
    setInterval(function(){
        $.ajax({
            url : '/courier/ajax/check-db-for-courier/',
            type : 'GET',
            success : function(data){ console.log("location1: " + data.hasCourierNewTask);
                if(typeof(Storage) !== "undefined") {
                    console.log("location2: " + data.hasCourierNewTask)
                    if(window.location.pathname == '/courier/tasks/should-pickup' && data.hasCourierNewTask){
                        console.log("location3: " + data.hasCourierNewTask)
                        sessionStorage.makeSoundAlert = 'yes';
                        unset_new_task_for_courier(true);
                    } else if(data.hasCourierNewTask) {
                        console.log("location4: " + data.hasCourierNewTask)
                         unset_new_task_for_courier();
                        audio = document.getElementById("alertAudio");
                        audio.play();
                        sessionStorage.makeSoundAlert = 'no';
                    }

                }
            }
        });
    }, 20000)

     /*
        Make a sound alert if new delivery request recieved
    */
    if(sessionStorage.makeSoundAlert == 'yes'){
        audio = document.getElementById("alertAudio");
        audio.play();
        sessionStorage.makeSoundAlert = 'no';
    }

    /*
        In courier-tasks.html page keeps the selected tab selected after page reloaded
    */
    switch(window.location.pathname) {
        case '/courier/tasks/smart-sort':
            $(".radio-inline.so").addClass("selected");
            break;
        case '/courier/tasks/custom-sort':
            $(".radio-inline.co").addClass("selected");
            break;
        case '/courier/tasks/pickedup':
            $(".radio-inline.pu").addClass("selected");
            break;
          case '/courier/tasks/rejected-pickup':
            $(".radio-inline.rp").addClass("selected");
            break;
          case '/courier/tasks/failures':
            $(".radio-inline.ft").addClass("selected");
            break;
        case '/courier/tasks/target-task':
            $(".radio-inline.tt").addClass("selected");
            break;
        default:
            $(".radio-inline.sp").addClass("selected");
    }

    // It makes  "Map" tab appear just for target-task page
    if(window.location.pathname == '/courier/tasks/target-task'){
        $(".expand-collapse.hidden").removeClass("hidden");
    }
})

function unset_new_task_for_courier(reload=false){
    $.ajax({
        url:'/courier/ajax/unset-new-task-for-courier/',
        type: 'Get',
        success: function(data){
            if(data.result == 'success' && reload){
                location.reload(true);
            }
        },
    });
}

// In courier-tasks.html page give "selected" class  to clicked tab
//      and keep a reference to selected element via session
$(".radio-inline").on('click', function(){
    $(".top-row").find(".selected").removeClass("selected");
    $(this).addClass('selected');
    sessionStorage.display_val = $(this).find('input').val();
})

// Drag and Drop for choosing ta`rget task
function allowDrop(ev) {
    ev.preventDefault();
}

function drag_task(){
    //this function reserved for future implementation
}

var task_goal = '';
var delivery_id_on_drag = '';
$(".delivery-wrapper").on('mousedown', function(){
    delivery_id_on_drag = $(this).attr('data-dlvry-id');
    task_goal = 'pickup';
})

var package_id_on_drag = '';
$(".package-wrapper").on('mousedown', function(){
    package_id_on_drag = $(this).attr('data-pckg-id');
    task_goal = 'handover';
})


$(".drop-target-task").on('dragenter', function(){
    $(this).addClass('drag-enter');
})

$(".drop-target-task").on('dragleave', function(){
    $(this).removeClass('drag-enter');
})

$(".add-to-target").click(function(){
    var value_str = $(this).val();
    var id = value_str.split(",")[0];
    var action = value_str.split(",")[1];
    var task_goal = "";
    if(action == 'pickup'){
        task_goal = 'pickup';
    }
    else if(action == 'handover'){
        task_goal = 'handover';
    }
    $.ajax({
        url:'/courier/ajax/put-task-on-target/',
        type:'GET',
        data:{
            'id':id,
            'task-goal':task_goal,
        },
        success : function(data){
            if(data.status == 'success'){
                location.reload(true);
            }else{

            }
        },
        error : function(){

        },

    });
})

// Hides and Shows map for target request on courier demand on "/courier/tasks/target-task" page
$(".expand-collapse.map").click(function(){
    $(this).find('i').toggleClass('fa-expand fa-compress');
    $(".map-wrapper.hideable").toggleClass('hidden');
})

// Hides and Shows packages of each delivery on "/courier/tasks/should-pickup" page
$(".expand-collapse.pkg").click(function(){
    $(this).find('i').toggleClass('fa-expand fa-compress');
    $(this).parents().eq(1).find('.hideable').toggleClass('hidden');
})

// Set modal button value with clicked delivery id
$(".withdraw").on('click', function(){
    delivery_id = $(this).val();
    $("#withdraw-target").val(delivery_id);
})

$("#withdraw-target").click(function(){
    target_item = $(this).val();
    item = target_item.split(":");
    if(item){
        $.ajax({
            url:'/courier/ajax/withdraw-target-task/',
            type:'GET',
            data:{
                'item-type':item[0],
                'id':item[1],
            },
            success : function(data){
                if(data.status == 'success'){
                    location.reload(true);
                }else{

                }
            },
            error : function(){

            },

        });
    }
})

$(".check-pickup").click(function(){
    $(this).toggleClass("selected");
    $(this).find(".far").toggleClass("fa-square fa-check-square");
})

// Sets package ID to reject package pickup Modal's reject button value
$(".reject-pickup").click(function(){
    package_id = $(this).val();
    $("#do-reject-pickup").val(package_id);
})

$("#do-reject-pickup").click(function(){
    package_id = $(this).val();
    rejection_reason = $("#pickup-rejection-text").val();
    $.ajax({
        url:'/courier/ajax/reject-package-pickup/',
        type:'GET',
        data:{
            'packageId':package_id,
            'rejectionReason':rejection_reason,
        },
        success : function(data){
            if(data.result == 'success'){

                location.reload(true);
            }
        },
        error : function(){

        },
    });
})

$(".undo-reject-pickup").click(function(){
    comment_and_package_ids = $(this).val();
    obj = JSON.parse(comment_and_package_ids);
    $.ajax({
        url:'/courier/ajax/undo-reject-package-pickup/',
        type:'GET',
        data:{
            'commentId':obj.commentId,
            'packageId':obj.packageId,
        },
        success : function(data){
            if (data.result == 'success'){
                location.reload(true);
            } else{
                alert("Operation failed!")
            }
        },
        error : function(){

        },
    });
})

$(".do-undo-pickup").click(function(){
    var value_str = $(this).val();
    var package_id = value_str.split(',')[0];
    var action = value_str.split(',')[1];
    $.ajax({
        url:'/courier/ajax/do-undo-pickup/',
        type:'GET',
        data:{
            'packageId':package_id,
            'action':action,
        },
        success : function(data){
            if (data.result == 'success'){
                location.reload(true);
            } else{
                alert("Operation failed!")
            }
        },
        error : function(){

        },
    });
})

$(".pickup-done").click(function(){
    delivery_id = $(this).val();
    $.ajax({
        url:'/courier/ajax/done-width-pickup/',
        type:'GET',
        data:{
            'deliveryId':delivery_id,
        },
        success : function(data){
            if (data.result == 'success'){
                location.reload(true);
            } else{
                alert("Operation failed!")
            }
        },
        error : function(){

        },
    });
})

$(".handover").on("click", function(){
    sig = $(this).attr("data-sig");
    if(sig == "True"){
        $("#receiver-name").attr("placeholder", "Name (required)")
        $("#do-handover").attr("disabled", true);
    } else {
        $("#receiver-name").attr("placeholder", "Name (optional)")
        $("#do-handover").attr("disabled", false);
    }
})

$("#do-handover").click(function(){
    package_id = $(this).val();
    signer_name = $("#receiver-name").val();
    signer_phone = $("#receiver-phone").val();
    $.ajax({
        url:'/courier/ajax/handover-package/',
        type:'GET',
        data:{
            "packageId" : package_id,
            "signerName" : signer_name,
            "signerPhone" : signer_phone,
        },
        success: function(data){
            if (data.result == "success"){
                location.reload(true);
            } else {
                alert("Operation failed!");
            }
        }

    })

})

$(".open-pickup-rejection-modal").click(function(){
    var package_id = $(this).val();
    $("#do-pickup-rejected").val(package_id);
})

$("#do-pickup-rejected").click(function(){
     var package_id = $(this).val();
     $.ajax({
        url:'/courier/ajax/pickup-rejected/',
        type:'Get',
        data: {
            'packageId': package_id,
        },
        success: function(data){
            if(data.result == "success"){
                location.reload(true)
            }else if(data.result == "failure"){
                alert("Failure!")
            }
        },
     });
})

$(".report-failure").click(function(){
    delivery_id = $(this).val();
    $("#do-report-failure").val(delivery_id);
    $("#reportFailureMolal").modal('show');
})

$("#do-report-failure").click(function(){
    value_str = $(this).val();
    id = value_str.split(":")[0]
    action = value_str.split(":")[1]
    comment_text = $(".failure-comment").val();
    if(delivery_id && comment_text){
        $.ajax({
            url:'/courier/ajax/report-failure/',
            type:'GET',
            data:{
                "id" : id,
                "commentText" : comment_text,
                "action" :action,
            },
            success: function(data){
                if (data.result == "success"){
                    location.reload(true);
                } else {
                    alert("Operation failed!");
                }
            }

        })
    }
})

$(".btn-action").click(function(){
    value_str = $(this).val();
    item_id = value_str.split(":")[0];
    item_type = value_str.split(":")[1];
    $.ajax({
        url: '/courier/ajax/add-failure-task-to-target/',
        type: 'Get',
        data: {
            'item_id': item_id,
            'item_type': item_type,
        },
        success: function(data){
            if(data.result == 'success'){
                location.reload(true);
            } else {
                alert( "Operation failed!")
            }
        }
    });
})
