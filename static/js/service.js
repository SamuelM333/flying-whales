$(document).ready(function () {
    let log_snippet = document.getElementById("log-snippet");
    log_snippet.scrollTo(0, log_snippet.scrollHeight);
    $('.datepicker').datepicker({autoClose: true, maxDate: new Date()});
    $('.timepicker').timepicker({autoClose: true});
    $('.modal').modal();
    let service_id = document.getElementById("service-name").textContent;
    console.log(service_id);
    $.ajax({url: `/service/${service_id}/download-logs/short/50`, success: function(result) {
        document.getElementById("log-snippet").innerHTML = result.log_lines;
    }});
});

$("#timerange").change(function () {
    this.checked ? $(".timerange").removeClass("hide") : $(".timerange").addClass("hide");
});
