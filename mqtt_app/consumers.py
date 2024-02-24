from channels.generic.websocket import WebsocketConsumer
import json
import paho.mqtt.client as mqtt
from django.conf import settings
from django.core.cache import  cache

class Boardcart(WebsocketConsumer):
    def connect(self):
        self.accept()

        print('have connection')
        def on_connect(mqtt_client, userdata, flags, rc):
            if rc == 0:
                print("Connected")

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
            self.send(text_data = json.dumps({
                'status':'log',
                'topic':msg.topic,
                'content_hex':hex_str,
                'qos':msg.qos

            }))
         


        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)

        self.client.on_connect = on_connect
        self.client.on_message = on_message
        # client.username_pw_set(settings.MQTT_USER, settings.MQTT_PASSWORD)
        self.client.connect(
            host=settings.MQTT_SERVER,
            port=settings.MQTT_PORT,
            keepalive=settings.MQTT_KEEPALIVE
        )
        

        self.client.loop_start()

    def disconnect(self, code):
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