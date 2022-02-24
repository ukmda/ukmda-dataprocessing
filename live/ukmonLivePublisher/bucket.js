var AWS = require('aws-sdk');

var AWSMqtt = require('aws-mqtt');

AWS.config.update({
    region: "eu-west-1"
});

const WebSocket = require('ws');

const publish = AWSMqtt.publisher({
    WebSocket: WebSocket,
    region: AWS.config.region,
    credentials: AWS.config.credentials,
    endpoint: 'a1v8kpr7nxi3a1.iot.eu-west-1.amazonaws.com'
})



s3 = new AWS.S3({apiVersion: '2006-03-01'});


var bucketParams = {
    Bucket : 'dev-jsn'
};

// Call S3 to create the bucket
s3.listObjects(bucketParams, function(err, data) {
    if (err) {
        console.log("Error", err);
    } else {
        data.Contents.forEach((d)=>{
            try{
                publish('/bucketChanged',JSON.stringify(d));
                console.log(d);
            } catch (e) {
                console.log(e);
            }
        });
    }
});
