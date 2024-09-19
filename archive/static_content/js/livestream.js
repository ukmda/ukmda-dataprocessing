// Copyright (C) 2018-2023 Mark McIntyre 
// initialize input widgets first
$('#selectInterval .time').timepicker({
    'showDuration': true,
    'timeFormat': 'g:ia'
});

$('#selectInterval .date').datepicker({
    'format': 'd/m/yyyy',
    'autoclose': true,
    'endDate': '0'
});

// initialize datepair
var res = document.getElementById("selectInterval");
var dateSelect = new Datepair(res, {
    'defaultDateDelta': 0,      // days
    'defaultTimeDelta': 900000 // milliseconds = 15 mins
});

$('#selectInterval').on('rangeSelected', function(){
    var startdate = $('#selectInterval .date:first').datepicker('getDate');
    var starttime = $('#selectInterval .time:first').timepicker('getTime', startdate);
    console.log(startdate, starttime);
    if(starttime != null){
        var dateval  = starttime.getTime();
        var timediff = dateSelect.getTimeDiff();
        var endval = dateval + timediff;
        var endtime = new Date();
        endtime.setTime(endval);
        $('#datestart').text(starttime.toISOString()); 
        $('#dateend').text(endtime.toISOString()); 
        if(timediff > 0){
            $('#statusfield').text('Valid range selected');
        }else{
            $('#statusfield').text('Date range must be > 0');
        }
    }
});
      
var apiurl = 'https://api.ukmeteors.co.uk/liveimages/getlive';
var form = document.querySelector("form");
form.addEventListener("submit", function (event) {
  //console.log("Saving value", form.elements.value.value);
  var d1 = document.getElementById("datestart").innerHTML;
  var d2 = document.getElementById("dateend").innerHTML;
  console.log(d1, d2);
  var dtval = "";
  var strstat = "";
  var enddtval = "";
  var statSelect = document.getElementById("statselect").value;
  if (statSelect != 1 ) {
    var e = document.getElementById("statselect");
    strstat = e.options[e.selectedIndex].text;
  }
  if (d1==="") {
    dtval = "latest";
    enddtval = "latest";
  }
  else
  {
    dtval = d1;
    enddtval = d2;
  }
  var payload = { dtstr: dtval, enddtstr : enddtval, statid: strstat };
  console.log(payload);
  document.getElementById("searchresults").innerHTML = "<font size=\"+2\">Searching....</font>";
  $.ajax({
    url: apiurl, 
    type: "GET",
    data: payload,
    dataType: 'jsonp',
    error: function (xhr, status, ex ) {
      if (status === 'error' ) {
        //alert("Too much data, try a narrower range");
        console.log(xhr.status);
        document.getElementById("searchresults").innerHTML = "<font size=\"+2\">No Matching Data</font>";
      }
    },
    complete: function (xhr, status) {
    }
  });
  event.preventDefault();}
);


function getCurrentDate() {
  var now=new Date();
  var yr = now.getFullYear();
  var mt = (now.getMonth()+1).toString().padStart(2,"0");
  var dy = (now.getDate()).toString().padStart(2,"0");
  var hr = (now.getHours()).toString().padStart(2,"0");
  var z =  + yr + mt + dy + "_" + hr;
  return z;  
}

function getTitle(urlstr){
  var filename = urlstr.substring(urlstr.lastIndexOf('/')+1);
  var qm = filename.lastIndexOf('?')-5;
  filename = filename.substring(1,qm);

  return filename;
}

function showImages(myObj) {
  pagetok = myObj.pagetoken;
  urls = myObj.urls;
  //console.log(urls);
  txt = "";
  for (x in urls) {
    thisurl = urls[x].url
    txt += "<a href=\"" + 
      thisurl+ "\" title=\"" + getTitle(thisurl) + "\"><img src=\"" + 
      thisurl + "\" width=\"18%\"></a>\n";
  }
  numimgs = urls.length;
  console.log(numimgs);
  document.getElementById("searchresults").innerHTML = txt;
  document.getElementById("eventcount").innerHTML = numimgs;
}
