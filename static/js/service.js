const namespace = '/logger';
const socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);
let service_id;
let log_snippet;
let scroll_log_snippet = true;

$(document).ready(function () {
    log_snippet = document.getElementById("log-snippet");
    $('.datepicker').datepicker({autoClose: true, maxDate: new Date()});
    $('.timepicker').timepicker({autoClose: true});
    $('.modal').modal();
    service_id = document.getElementById("service-name").textContent;
    $.ajax({url: `/service/${service_id}/download-logs/short/50`, success: function(result) {
        log_snippet.innerHTML = result.log_lines;
        log_snippet.scrollTo(0, log_snippet.scrollHeight);
    }});
});

$("#timerange").change(function () {
    this.checked ? $(".timerange").removeClass("hide") : $(".timerange").addClass("hide");
});

socket.on('connect', function() {
    socket.emit('join', service_id);
});

socket.on('log_line', function(line) {
    console.log(line);
    log_snippet.innerHTML += line;
    if (scroll_log_snippet) log_snippet.scrollTo(0, log_snippet.scrollHeight);
});

$(window).bind('beforeunload', function(){
    socket.emit('leave', service_id);
});

socket.on('debug', function(line) {
    console.log("DEBUG: " + line)
});
