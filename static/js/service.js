$(document).ready(function () {
    let log_snippet = document.getElementById("log-snippet");
    $('.datepicker').datepicker({autoClose: true, maxDate: new Date()});
    $('.timepicker').timepicker({autoClose: true});
    $('.modal').modal();
    let service_id = document.getElementById("service-name").textContent;
    console.log(service_id);
    $.ajax({url: `/service/${service_id}/download-logs/short/50`, success: function(result) {
        log_snippet.innerHTML = result.log_lines;
        log_snippet.scrollTo(0, log_snippet.scrollHeight);
    }});
});

$("#timerange").change(function () {
    this.checked ? $(".timerange").removeClass("hide") : $(".timerange").addClass("hide");
});

var namespace = '/test';
var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);

socket.on('connect', function() {
    socket.emit('my_event', {data: 'I\'m connected!'});
});

socket.on('my_response', function(msg) {
    console.log(msg);
});
