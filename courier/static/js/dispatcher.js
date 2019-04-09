$(document).ready(function (){
    /*
        Make a sound alert if new delivery request recieved
    */
    if(sessionStorage.makeSoundAlert == 'yes'){
        audio = document.getElementById("alertAudio");
        audio.play();
        sessionStorage.makeSoundAlert = 'no';
    }

    /*
        Status Chart
    */
	var options = {
		responsive: true,
		legend: {
			position: 'top',
		},
		title: {
			display: true,
		},
		animation: {
			animateScale: true,
			animateRotate: true
		}
	};
    var data = {
        datasets: [{
            data: [not_reviewed, waiting_for_courier, on_road_to_pick, on_road_to_deliver, delivered],
            backgroundColor: [
				"#FF0000", //window.chartColors.red,
				"#FFFF00", //window.chartColors.yellow,
				"#FFC300", //window.chartColors.orange,
				"#2E86C1", //window.chartColors.blue,
				"#2ECC71", //window.chartColors.green,
			],
        }],
        labels: [
            'Not Reviewed',
            'Waiting for courier',
            'Not Picked Yet',
            'Delivering',
            'Delivered',
        ]
    };
    var  dashboard_delivery_status = new Chart(document.getElementById('dashboard-delivery-status').getContext('2d'), {
        type: 'doughnut',
        data: data,
        options: options
    });
    /*
        Delivery Request Chart
    */
	var data = {
		labels: request_chart_lables,
		datasets: [{
			label: 'Number of delivery requests',
			backgroundColor: "#FF0000",
			borderColor: "#FF0000",
			fill: false,
			data: request_chart_variables,
			fill: false,
		},]
	};
	var options = {
		responsive: true,
		hover: {
			mode: 'nearest',
			intersect: true
		},
		tooltips: {
			mode: 'index',
			intersect: false,
		},
		scales: {
			xAxes: [{
				display: true,
				scaleLabel: {
					display: true,
					labelString: 'Time of day'
				}
			}],
			yAxes: [{
				display: true,
                ticks: {
                    beginAtZero:true,
                    stepSize: 1,
                },
				scaleLabel: {
					display: true,
					labelString: 'Number of request'
				}
			}]
		}
	};

    var  dashboard_delivery_requests = new Chart(document.getElementById('dashboard-delivery-requests').getContext('2d'), {
        type: 'line',
        data: data,
        options: options
    });
});


/*
    Auto dispatch auto-dispatch-select for selecting courier
*/

$(".auto-dispatch > input[type='checkbox']").on('click',function(){

    if($("input[type='checkbox']").is(":checked")){
        $("#auto-dispatch-select").prop("disabled",false);
    }
    else {
        $("#auto-dispatch-select > option[value='-1']").prop("selected",true);
        $("#auto-dispatch-select").prop("disabled",true);
    }

});

$("#auto-dispatch-select").change(function(){
    var courier_id = $(this).val();
    var auto_dispatch_on = $("#auto-dispatch-check").is(':checked');
    if(courier_id > 0 && auto_dispatch_on){
        $.ajax({
            url:'/dispatcher/ajax/set-auto-dispatch-on/',
            type:'Get',
            data: {
                'courier-id': courier_id
            },
            success: function(data){
                alert("Auto dispatch set to " + data.courier_name );
            }
        });
    }
})

$("#auto-dispatch-check").on('click', function(){
    if(!$(this).is(':checked')) {
        $.ajax({
            url:'/dispatcher/ajax/set-auto-dispatch-off/',
            type: 'Get',
            success: function(data){
                if (data.result == "success"){
                    console.log("Auto dispatch turned off")
                }
            }
        });
    }
})

$(".btn-select-courier").click(function(){
    delivery_id = $(this).val();
    $("#do-dispatch").attr("data-delivery-id",delivery_id);
    $("#do-dispatch").attr("data-courier-id","");
     $("#choose-courier-modal").find(".selected-courier").removeClass("selected-courier");
     $("#do-dispatch").prop("disabled",true);
})

$(".each-courier").on('click', function(){
    $("#choose-courier-modal").find(".selected-courier").removeClass("selected-courier");
    $(this).addClass("selected-courier");
    courier_id = $(this).find("span.courierid").data("cid");
    $("#do-dispatch").attr("data-courier-id",courier_id);
    $("#do-dispatch").prop("disabled",false);



});

$("#do-dispatch").click(function(){
    delivery_id = $(this).attr("data-delivery-id");
    courier_id = $(this).attr("data-courier-id");
    if(delivery_id && courier_id ){
        $.ajax({
            url: '/dispatcher/ajax/set-courier/',
                type : 'GET',
                data : {
                'delivery_id' : delivery_id,
                'courier_id'  : courier_id,
            },
            success: function (data) {
                //show success message
                location.reload(true);
            },
            error : function(){
                alert("error")
            }

        });
    }
});

$(".btn-reject-delivery-request").click(function(){
    delivery_id = $(this).val();
    $("#btn-do-reject").attr("data-delivery-id",delivery_id);
    $("#delivery-rejection-text").val("");
    $("#btn-do-reject").prop("disabled",true);
});

$("#btn-do-reject").click(function(){
    delivery_id = $(this).attr("data-delivery-id");
    reason = $("#delivery-rejection-text").val();
    if(delivery_id){
        $.ajax({
            url: '/dispatcher/ajax/set-delivery-rejection-reason/',
            type : 'GET',
            data : {
                'delivery_id' : delivery_id,
                'reason' : reason,
            },
            success: function (data) {
                //show success message
                location.reload(true);
            },
            error : function(){
                alert("error")
            }

        });
    }
});

$( "#delivery-rejection-text" ).on('keyup', function() {
    text_length = $.trim($(this).val()).length;
    if(text_length > 1){
        $("#btn-do-reject").prop("disabled",false);
    }else {
        $("#btn-do-reject").prop("disabled",true);
    }
});

// automatically check delivery table in the database every x millisecond to reload page if any new row
$(document).ready(function(){
    setInterval(function(){
        $.ajax({
            url : '/dispatcher/ajax/check-db-for-dispatcher/',
            type : 'GET',
            success : function(data){
               id =  data.last_delivery_id;
                if (typeof(Storage) !== "undefined") {
                    if(sessionStorage.last_delivery_id){
                        if(Number(sessionStorage.last_delivery_id) !== Number(id)){
                            sessionStorage.makeSoundAlert = 'yes';
                            sessionStorage.last_delivery_id = id;
                            location.reload(true);
                        }
                    }else {
                        sessionStorage.last_delivery_id = id;
                    }
                }
            },
            error : function() {
                id =  -1;
            },
        })
    }, 20000);
})





