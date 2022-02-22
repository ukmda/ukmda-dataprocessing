const aws = require('aws-sdk');
aws.config.update({
    region: "eu-west-1"
});


const dynamodb = new aws.DynamoDB.DocumentClient();

var items = [];

var needID = 'M20161021_235004_MC1_c1';
var newUrl = 'https://archive.ukmeteornetwork.co.uk/data/mc1/c1/2016/201610/20161021/M20161021_235004_MC1_c1P.jpg';

var updateQuery = {
    TableName: 'meteor',
    Key: {
        'clip_name': needID
    },
    ExpressionAttributeNames: {
        "#image_url": "image_url"
    },
    ExpressionAttributeValues: {
        ":new_url": newUrl
    },
    UpdateExpression: "set #image_url = :new_url"
};


var scanQuery = {
    TableName: 'meteor',
    FilterExpression: 'contains(#image_url, :backup)',
    ExpressionAttributeNames: {
        '#image_url': 'image_url'
    },
    ExpressionAttributeValues: {
        ':backup' : 'backup'
    }
};
dynamodb.scan(scanQuery,onScan);

function onScan(err,data) {
    if(err){
        console.log(err);
        return;
    }
    data.Items.forEach(function(item) {
        console.log(item.image_url)
        items.push(item);
    });

    if (typeof data.LastEvaluatedKey != "undefined") {
        scanQuery.ExclusiveStartKey = data.LastEvaluatedKey;
        dynamodb.scan(scanQuery, onScan);
    } else  {
        items.forEach(function (t) {
           t.image_url = t.image_url.replace(
               'https://archive.ukmeteornetwork.co.uk/backup',
               'https://archive.ukmeteornetwork.co.uk/data'
           ) ;
            updateQuery.ExpressionAttributeValues = {
                ":new_url": t.image_url
            };

            updateQuery.Key = {
                'clip_name': t.clip_name
            };

            console.log('update => '+t.clip_name);

            dynamodb.update(updateQuery,(err,data)=>{
                if(err){
                    console.log(err);
                } else {
                    console.log(data);
                }
            });
        });

        console.log('Items count is ' + items.length)
    }
}

