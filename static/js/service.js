$(document).ready(function () {
    $('.datepicker').datepicker({ autoClose: true, maxDate: new Date() });
    $('.timepicker').timepicker({ autoClose: true });
    $('.modal').modal();
});

$("#timerange").change(function () {
    this.checked ? $(".timerange").removeClass("hide") : $(".timerange").addClass("hide");
});

// $('#log_form').submit(function () {
//     // TODO Why [0] ? $(#) should select just one.
//     // TODO Add time to date range validation (same day validation)
//     let date_start = M.Datepicker.getInstance($("#date-start")[0]).date;
//     let timerange = $("#timerange")[0].checked;
//
//     if (timerange) {
//         if (date_end >= date_start) {
//             return true;
//         } else {
//             M.Modal.getInstance($("#error-modal")).open();
//             return false;
//         }
//     } else {
//         return true;
//     }
// });