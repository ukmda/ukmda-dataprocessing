$(function() {

    Morris.Area({
        element: 'morris-area-chart',
        data: [{
            period: '2010 Q1',
            iphone: 2666,
            ipad: null,
            itouch: 2647
        }, {
            period: '2010 Q2',
            iphone: 2778,
            ipad: 2294,
            itouch: 2441
        }, {
            period: '2010 Q3',
            iphone: 4912,
            ipad: 1969,
            itouch: 2501
        }, {
            period: '2010 Q4',
            iphone: 3767,
            ipad: 3597,
            itouch: 5689
        }, {
            period: '2011 Q1',
            iphone: 6810,
            ipad: 1914,
            itouch: 2293
        }, {
            period: '2011 Q2',
            iphone: 5670,
            ipad: 4293,
            itouch: 1881
        }, {
            period: '2011 Q3',
            iphone: 4820,
            ipad: 3795,
            itouch: 1588
        }, {
            period: '2011 Q4',
            iphone: 15073,
            ipad: 5967,
            itouch: 5175
        }, {
            period: '2012 Q1',
            iphone: 10687,
            ipad: 4460,
            itouch: 2028
        }, {
            period: '2012 Q2',
            iphone: 8432,
            ipad: 5713,
            itouch: 1791
        }],
        xkey: 'period',
        ykeys: ['iphone', 'ipad', 'itouch'],
        labels: ['iPhone', 'iPad', 'iPod Touch'],
        pointSize: 2,
        hideHover: 'auto',
        resize: true
    });

    Morris.Donut({
        element: 'morris-donut-chart',
        data: [{
            label: "Download Sales",
            value: 12
        }, {
            label: "In-Store Sales",
            value: 30
        }, {
            label: "Mail-Order Sales",
            value: 20
        }],
        resize: true
    });

    Morris.Bar({
        element: 'morris-bar-chart',
        data: [{
            y: '2006',
            a: 100,
            b: 90
        }, {
            y: '2007',
            a: 75,
            b: 65
        }, {
            y: '2008',
            a: 50,
            b: 40
        }, {
            y: '2009',
            a: 75,
            b: 65
        }, {
            y: '2010',
            a: 50,
            b: 40
        }, {
            y: '2011',
            a: 75,
            b: 65
        }, {
            y: '2012',
            a: 100,
            b: 90
        }],
        xkey: 'y',
        ykeys: ['a', 'b'],
        labels: ['Series A', 'Series B'],
        hideHover: 'auto',
        resize: true
    });
    
Morris.Line({
 element: 'morris-line-chart',
 data: [
    {time: 1385888200000,
    maxtemp: 15.5,
    mintemp: -1.2    },
    {time: 1388566611000,
    maxtemp: 14.9,
    mintemp: -0.1    },
    {time: 1391244945000,
    maxtemp: 12.6,
    mintemp: -0.4    },
    {time: 1393664233000,
    maxtemp: 14.2,
    mintemp: -0.2    },
    {time: 1396342749000,
    maxtemp: 22.1,
    mintemp: -0.5    },
    {time: 1398934746000,
    maxtemp: 23.3,
    mintemp: 2.2    },
    {time: 1401612960000,
    maxtemp: 27.0,
    mintemp: 3.4    },
    {time: 1404205101000,
    maxtemp: 26.6,
    mintemp: 6.2    },
    {time: 1406883437000,
    maxtemp: 33.6,
    mintemp: 9.8    },
    {time: 1408391082000,
    maxtemp: 26.5,
    mintemp: 10.9    },
    {time: 1412153939000,
    maxtemp: 27.4,
    mintemp: 7.0    },
    {time: 1414832361000,
    maxtemp: 21.5,
    mintemp: 3.4    },
    {time: 1417424177000,
    maxtemp: 17.3,
    mintemp: 1.1    }],
        xkey: 'time',
        ykeys: ['maxtemp', 'mintemp'],
        labels: ['Max Temp', 'Min Temp'],
        hideHover: 'auto',
		postUnits: '°C',
        resize: true
    });
});
