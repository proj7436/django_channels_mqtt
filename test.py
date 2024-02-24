import paho.mqtt.client as mqtt

# Định nghĩa hàm callback khi kết nối thành công với broker MQTT
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    # Đăng ký tham gia vào một chủ đề sau khi kết nối thành công
    client.subscribe("test/topic")

# Định nghĩa hàm callback khi nhận được một tin nhắn từ broker MQTT
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))

# Khởi tạo một client MQTT
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)

# Thiết lập các hàm callback
client.on_connect = on_connect
client.on_message = on_message

# Kết nối tới broker MQTT
client.connect("localhost", 1883, 60)

# Lặp vô hạn để giữ kết nối với broker
client.loop_forever()
