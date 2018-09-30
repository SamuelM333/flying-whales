$(document).ready(() => {
    $('.datepicker').datepicker({ autoClose: true, maxDate: new Date() });
    $('.timepicker').timepicker({ autoClose: true });
    $('.modal').modal();
});

$("#date-start").change(() => {
    let date_start = M.Datepicker.getInstance($("#date-start")[0]).date;
    $('#date-end').datepicker({ autoClose: true, minDate: date_start, maxDate: new Date() });
});

$("#timerange").change(() => {
    this.checked ? $(".timerange").removeClass("hide") : $(".timerange").addClass("hide");
});

$('#log_form').submit(() => {
    // TODO Why [0] ? $(#) should select just one.
    // TODO Add time to date range validation (same day validation)
    let date_start = M.Datepicker.getInstance($("#date-start")[0]).date;
    let date_end = M.Datepicker.getInstance($("#date-end")[0]).date;
    let timerange = $("#timerange")[0].checked;

    if (timerange) {
        if (date_end >= date_start) {
            return true;
        } else {
            M.Modal.getInstance($("#error-modal")).open();
            return false;
        }
    } else {
        return true;
    }
});