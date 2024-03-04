from channels.generic.websocket import WebsocketConsumer
import json
import paho.mqtt.client as mqtt
from django.core.cache import  cache
from django.conf import settings
import ssl 
import socket


MQTT_SERVER = ''
MQTT_PORT = 0
MQTT_KEEPALIVE = 60


class Boardcart(WebsocketConsumer):
    def connect(self):
        global on_connect, on_message
        self.accept()

        def on_connect(mqtt_client, userdata, flags, rc):

            if rc == 0:
            
                print(f"Connected successfully to MQTT broker {rc}")

                #main topic
                mqtt_client.subscribe('django-24092006')    
                topics = cache.get('all_topics', [])
                if topics:

                    for topic in topics:
                        mqtt_client.subscribe(topic)

                #
            else:
                print('Bad connection. Code:', rc)

        def on_message(mqtt_client, userdata, msg):
            #check xem có phải hex?
            try:
                hex_str = msg.payload.decode("utf-8")
            except UnicodeDecodeError:
                hex_str = msg.payload.hex()
                print(hex_str)
            self.send(text_data = json.dumps({
                'status':'log',
                'topic':msg.topic,
                'content_hex':hex_str,
                'qos':msg.qos

            }))
         



        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
        self.client.on_connect = on_connect
        self.client.on_message = on_message


    def disconnect(self, code):
        cache.set('all_topics', [])
        self.close()


    def receive(self, text_data):
        data = json.loads(text_data)
       
        if data['status'] == 'create_topic':
            if "+" in data['topic'] or "#" in data['topic']:
                return 
            all_topic_cache = cache.get('all_topics')
            if data['topic'] in all_topic_cache:
                return self.send(text_data = json.dumps({
                    'status': 'topic_exist'
                }))
            all_topic_cache.append(data['topic'])
            cache.set('all_topics', all_topic_cache, settings.CACHE_TIMEOUT)
            try:
                self.client.subscribe(data['topic'])
                return self.send(text_data = json.dumps({
                        'status': 'created_successfully'
                    }))
            except:
                pass

        elif data['status'] == 'connect_mqtt_server':
            host = data['host']
            port = data['port']

            if not host.startswith('mqtt'):
                return self.send(json.dumps({
                   'status':'connect_fail'
                }))
            try:
                self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
                self.client.on_connect = on_connect
                self.client.on_message = on_message
                if host.startswith('mqtts://'):
                    self.client.tls_set(cert_reqs=ssl.CERT_NONE)
                MQTT_SERVER = host.split('//')[1]
                MQTT_PORT = int(port)
                self.client.connect(
                    host=MQTT_SERVER,
                    port=MQTT_PORT,
                    keepalive=MQTT_KEEPALIVE
                )
                self.client.loop_start()
           

            except ValueError:
                 return self.send(json.dumps({
                    'status':'connect_fail'
                }))
            except socket.timeout:
                return self.send(json.dumps({
                    'status':'connect_fail'
                }))
       
            cache.set('all_topics', [])
            return self.send(json.dumps({
                    'status':'connect_success'
                }))

        elif data['status'] == 'disconnect_mqtt_server':
            self.client.loop_stop()
            self.client.disconnect()
            cache.set('all_topics', [])
            return self.send(json.dumps({
                'status':'disconnect_success'
            }))