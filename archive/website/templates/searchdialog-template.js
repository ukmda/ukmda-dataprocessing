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
      
var apiurl = '{{APIURL}}';
var form = document.querySelector("form");
form.addEventListener("submit", function (event) {
  //console.log("Saving value", form.elements.value.value);
  var d1 = document.getElementById("datestart").innerHTML;
  var d2 = document.getElementById("dateend").innerHTML;
  var op = "foo";
  //jQuery.support.cors = true;
  payload = {"a":  d1, "b": d2, "op":  op };
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
    console.log(myObj);
    var x, txt = "";
    txt = "<table class=\"table table-striped table-bordered table-hover table-condensed\">"
    txt += "<tr><td><b>DateTime</b></td><td><b>Source</b></td><td><b>Shower</b></td>";
    txt += "<td><b>Mag</b></td><td><b>Camera</b></td><td><b>Link</b></td></tr>";
    for (x in myObj) {
      console.log(myObj[x]);
      var dtarr = myObj[x].split(',');
      if (dtarr[0] > 0 ){
        txt +='<tr><td>';
        dt = new Date(dtarr[0]*1000);
        txt += dt.toISOString();
        txt += "</td><td>";
        txt += dtarr[1];
        txt += "</td><td>";
        txt += dtarr[2];
        txt += "</td><td>";
        txt += dtarr[3];
        txt += "</td><td>";
        txt += dtarr[4];
        txt += "</td><td>";
        errimg = "onerror=\"this.onerror=null;this.src='/img/missing.png';\"";
        txt += "<a href=\"" + dtarr[5] + "\" target=\"_blank\"><img src=\"" + dtarr[6] + "\" " + errimg + " alt=\"Image unavailable\" width=\"100\"></a>";
        txt += "</tr>";
      }
    }
    txt += "</table>";
    document.getElementById("searchresults").innerHTML = txt;
}
