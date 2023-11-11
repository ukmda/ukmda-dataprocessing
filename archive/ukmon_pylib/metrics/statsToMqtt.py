import paho.mqtt.client as mqtt
import platform
from shutil import disk_usage
import datetime


# The callback function. It will be triggered when trying to connect to the MQTT broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected success")
    else:
        print("Connected fail with code", rc)


def on_publish(client, userdata, result):
    #print('data published - {}'.format(result))
    return


def statsToMqtt(diskspace, pctused):
    broker = 'themcintyres.ddns.net'
    topicbase = 'servers' 
    servername = platform.node().lower()

    client = mqtt.Client(servername)
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.connect(broker, 9883, 60)

    topic = f'{topicbase}/{servername}/freespace'
    ret = client.publish(topic, payload=diskspace, qos=0, retain=False)
    topic = f'{topicbase}/{servername}/pctused'
    ret = client.publish(topic, payload=pctused, qos=0, retain=False)
    topic = f'{topicbase}/{servername}/timestamp'
    ts = datetime.datetime.now().isoformat()
    ret = client.publish(topic, payload=ts, qos=0, retain=False)
    return ret


if __name__ == '__main__':
    dfs = disk_usage('/')
    freespace = round(dfs[2]/1024/1024/1024,2)
    pctused = round(dfs[1]*100.0/dfs[0],2)
    statsToMqtt(freespace, pctused)
