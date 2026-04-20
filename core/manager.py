import json
from core import connect

device_list = {}
on_message_callback = None

client = connect.make_client("iot-manager", clean_session=True)

def on_connect(c, userdata, flags, reason_code, properties):
    c.subscribe("iot/discovery", qos=1)
    c.subscribe("iot/+/data", qos=1)

def on_message(c, userdata, message):
    try:
        payload = json.loads(message.payload.decode())
    except Exception:
        return

    if message.topic == "iot/discovery":
        device_id = payload.get("id")
        if device_id:
            device_list[device_id] = payload

    if on_message_callback:
        on_message_callback(message.topic, payload)

client.on_connect = on_connect
client.on_message = on_message

def connect_():
    client.connect(connect.BROKER, connect.PORT)
    client.loop_start()

def disconnect():
    client.loop_stop()
    client.disconnect()

def send_command(device_id, mode):
    client.publish(
        f"iot/{device_id}/cmd",
        json.dumps({"mode": mode}),
        qos=1 #qos 1 ise mesaj garanti edilir, qos 0 ise mesaj garanti edilmez
    )
