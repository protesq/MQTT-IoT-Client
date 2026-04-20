import uuid
import json
from core import connect

device_id = str(uuid.uuid4())
client = connect.make_client(f"device-{device_id}", clean_session=False)

client.will_set(
    f"iot/{device_id}/status",
    json.dumps({"id": device_id, "state": "offline"}),
    qos=1,
    retain=True
)

def on_connect(c, userdata, flags, reason_code, properties):
    c.publish(
        "iot/discovery",
        json.dumps({"id": device_id, "state": "online"}),
        qos=1,
        retain=True
    )
    c.subscribe(f"iot/{device_id}/cmd", qos=1)
    print(f"[{device_id}] Bağlandı.")

def on_message(c, userdata, message):
    try:
        command = json.loads(message.payload.decode())
    except Exception:
        return
    mode = command.get("mode")
    print(f"[{device_id}] Komut: {mode}")
    c.publish(
        f"iot/{device_id}/data",
        json.dumps({"ack": True, "mode": mode}),
        qos=1
    )

client.on_connect = on_connect
client.on_message = on_message

if __name__ == "__main__":
    client.connect(connect.BROKER, connect.PORT)
    client.loop_forever()
