import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883

def make_client(client_id, clean_session=True):
    return mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id=client_id,
        clean_session=clean_session
    )
