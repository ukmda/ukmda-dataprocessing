// initialize input widgets first
$('#jqueryExample .time').timepicker({
    'showDuration': true,
    'timeFormat': 'g:ia'
});

$('#jqueryExample .date').datepicker({
    'format': 'd/m/yyyy',
    'autoclose': true
});

// initialize datepair
var res = document.getElementById("jqueryExample");
var dateSelect = new Datepair(res, {
    'defaultDateDelta': 0,      // days
    'defaultTimeDelta': 7200000 // milliseconds
});
