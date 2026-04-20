from device.simulator import client, connect

if __name__ == "__main__":
    client.connect(connect.BROKER, connect.PORT)
    client.loop_forever()
