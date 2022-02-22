var AWS = require('aws-sdk');
var AWSMqtt = require('aws-mqtt');
let async = require('async');
var docClient = new AWS.DynamoDB.DocumentClient();
var moment = require('moment');

AWS.config.update({
    region: "eu-west-1"
});

//timestamp - int
//add Year
//add Month
//add Day


exports.handler = (event, context, callback) => {

    const WebSocket = require('ws');

    const publish = AWSMqtt.publisher({
        WebSocket: WebSocket,
        region: AWS.config.region,
        credentials: AWS.config.credentials,
        endpoint: process.env.AWS_MQTT_ENDPOINT
    });

    publish('/bucketChanged',JSON.stringify(event)).then(
        res => {
            callback(null, res)
        },
        err => callback(err)
    );

    function getTimestampAndStation(imageName) {
        if(
            imageName.includes('$') || imageName.includes('<') || imageName.includes('\\') ||
            imageName.includes('&') || imageName.includes('>') || imageName.includes('^') ||
            imageName.includes(',') || imageName.includes('#') || imageName.includes('~') ||
            imageName.includes('/') || imageName.includes('%') || imageName.includes('[') ||
            imageName.includes(':') || imageName.includes('{') || imageName.includes(']') ||
            imageName.includes(';') || imageName.includes('}') || imageName.includes('`') ||
            imageName.includes('=') || imageName.includes('|') || imageName.includes('"')
        ) {
            return false;
        }

        let date = imageName.substr(1,imageName.indexOf('_'));
        let time = imageName.substr(date.length+1);

        time = time.substr(0,time.indexOf('_'));
        let name = (imageName.substr(imageName.indexOf(time)+time.length+1));
        name = name.substr(0,name.indexOf('P.jpg'));
        name = name.replace(new RegExp('_','g'),' ');
        name = name.replace('+','_');

        time = time[0]+time[1]+':'+time[2]+time[3]+':'+time[4]+time[5];
        date = date[0]+date[1]+date[2]+date[3]+'/'+date[4]+date[5]+'/'+date[6]+date[7];

        let dateTime = moment(new Date(date+' '+time));
        let dtStr = dateTime.format('D MMM YYYY') +' at '+dateTime.format('HH:mm:ss')+' UT';
        return {
            timestamp: dateTime.format('x'),
            station_name:name
        }

    }

    let msg = event;
    for(let i = 0; i<msg.Records.length; i++){
        if(msg.Records[i].s3.object.key.includes('P.jpg')){
            let itemData = getTimestampAndStation(msg.Records[i].s3.object.key);
            if(!itemData) continue;
            let item = {
                TableName: 'live',
                Item: {
                    image_name:msg.Records[i].s3.object.key,
                    timestamp: itemData.timestamp,
                    image_timestamp: (itemData.timestamp+1)-1,
                    station_name: itemData.station_name,
                    year: moment.unix(itemData.timestamp.substr(0,10)).format('YYYY'),
                    month: moment.unix(itemData.timestamp.substr(0,10)).format('MM'),
                }
            };

            if(msg.Records[i].eventName === 'ObjectCreated:Put') {
                item.Item.is_deleted = false;
            } else if(msg.Records[i].eventName === 'ObjectRemoved:Delete') {
                item.Item.is_deleted = true;
            }

            docClient.put(item, (d,e)=>{});
        }
    }
}

if (process.env.IS_LOCAL) {
    require('dotenv').config()
    exports.handler({}, {}, console.log);
}

