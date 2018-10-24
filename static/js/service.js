$(document).ready(function () {
    $('.datepicker').datepicker({ autoClose: true, maxDate: new Date() });
    $('.timepicker').timepicker({ autoClose: true });
    $('.modal').modal();
});

$("#timerange").change(function () {
    this.checked ? $(".timerange").removeClass("hide") : $(".timerange").addClass("hide");
});