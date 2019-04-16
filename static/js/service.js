const namespace = '/logger';
const socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);
let service_id;
let log_snippet_containers;
let scroll_log_snippet = true;

$(document).ready(function () {
    log_snippet_containers = document.getElementsByClassName("log-snippet");
    $('.datepicker').datepicker({autoClose: true, maxDate: new Date()});
    $('.timepicker').timepicker({autoClose: true});
    $('.modal').modal();
    service_id = document.getElementById("service-name").textContent;
    $.ajax({url: `/service/${service_id}/download-logs/short/50`, success: function(result) {
        Array.prototype.forEach.call(log_snippet_containers, function(log_snippet_container) {
            log_snippet_container.innerHTML = result.log_lines;
            log_snippet_container.scrollTo(0, log_snippet_container.scrollHeight);
        });
    }});
});

$("#timerange").change(function () {
    this.checked ? $(".timerange").removeClass("hide") : $(".timerange").addClass("hide");
});

socket.on('connect', function() {
    socket.emit('join', service_id);
});

socket.on('log_line', function(line) {
    Array.prototype.forEach.call(log_snippet_containers, function(log_snippet_container) {
        log_snippet_container.innerHTML += line;
        if (scroll_log_snippet) log_snippet_container.scrollTo(0, log_snippet_container.scrollHeight);
    });
});

$(window).bind('beforeunload', function(){
    socket.emit('leave', service_id);
});
