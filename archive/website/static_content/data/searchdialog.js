// initialize input widgets first
$('#selectInterval .time').timepicker({
    'showDuration': true,
    'timeFormat': 'g:ia'
});

$('#selectInterval .date').datepicker({
    'format': 'd/m/yyyy',
    'autoclose': true
});

// initialize datepair
var res = document.getElementById("selectInterval");
var dateSelect = new Datepair(res, {
    'defaultDateDelta': 0,      // days
    'defaultTimeDelta': 7200000 // milliseconds
});

$('#selectInterval').on('rangeSelected', function(){
    var startdate = $('#selectInterval .date:first').datepicker('getDate');
    var starttime = $('#selectInterval .time:first').timepicker('getTime', startdate);
    if(starttime != null){
        var dateval  = starttime.getTime();
        var timediff = dateSelect.getTimeDiff();
        var endval = dateval + timediff;
        endtime = new Date();
        endtime.setTime(endval);
        $('#datestart').text(starttime.toISOString()); //.toLocaleString('en-GB', { timeZone: 'UTC' }));
        $('#dateend').text(endtime.toISOString()); //.toLocaleString('en-GB', { timeZone: 'UTC' }));
        if(timediff > 0){
            $('#statusfield').text('Valid range selected');
        }else{
            $('#statusfield').text('Date range must be > 0');
        }
    }
});
      
var apiurl = 'https://0zbnc358p0.execute-api.eu-west-1.amazonaws.com/test';
var form = document.querySelector("form");
form.addEventListener("submit", function (event) {
  //console.log("Saving value", form.elements.value.value);
  var d1 = document.getElementById("datestart").innerHTML;
  var a = Date.parse(d1);
  var d2 = document.getElementById("dateend").innerHTML;
  var b = Date.parse(d2);
  var op = "foo";
  //jQuery.support.cors = true;
  payload = {"a":  a, "b": b, "op":  op };
  console.log(payload);
  $.ajax({
    url: apiurl, 
    type: "GET",
    data: payload,
    dataType: 'jsonp',
    complete: function (xhr, status, ex) {
      if (status === 'error' ) {
        alert(status + "," + ex );
      }
    }
  });
  event.preventDefault();}
  );
function myFunc(myObj) {
    var x, txt = "";
    for (x in myObj) {
      txt += myObj[x].name + "<br>";
    }
    document.getElementById("dateend").innerHTML = txt;
}
