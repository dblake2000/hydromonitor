########################################################################################################
#                                                                                                      #
#   MQTT Paho Documentation - https://eclipse.dev/paho/index.php?page=clients/python/docs/index.php    #
#                                                                                                      #
########################################################################################################

import paho.mqtt.client as mqtt
from random import randint
from json import loads


class MQTT:
    ID = f"IOT_B_{randint(1, 1000000)}"

    # ESP32 publishes sensor JSON here
    HW_TOPIC = "620167361"

    # Must match the broker you use
    MQTT_HOST = "www.yanacreations.com"
    MQTT_PORT = 1883

    sub_topics = [(HW_TOPIC, 0)]

    def __init__(self, mongo):
        self.mongo = mongo

        self.client = mqtt.Client(
            client_id=self.ID,
            clean_session=True,
            reconnect_on_failure=True,
        )

        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_subscribe = self.on_subscribe

        # Register topic-specific callback
        self.client.message_callback_add(self.HW_TOPIC, self.update)

        # Connect async (run.py starts loop_start)
        self.client.connect_async(self.MQTT_HOST, self.MQTT_PORT, 60)

    def connack_string(self, rc):
        connection = {
            0: "Connection successful",
            1: "Connection refused - incorrect protocol version",
            2: "Connection refused - invalid client identifier",
            3: "Connection refused - server unavailable",
            4: "Connection refused - bad username or password",
            5: "Connection refused - not authorised",
        }
        return connection.get(rc, f"Unknown result code {rc}")

    def on_connect(self, client, userdata, flags, rc):
        print(
            "\n\nMQTT:",
            self.connack_string(rc),
            "ID:",
            client._client_id.decode("utf-8"),
        )

        # DEBUG: show what we subscribe to
        print("MQTT: subscribing to", self.sub_topics)

        client.subscribe(self.sub_topics)

    def on_subscribe(self, client, userdata, mid, granted_qos):
        print("MQTT: Subscribed to", [topic[0] for topic in self.sub_topics])

    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            print("MQTT: Unexpected Disconnection. rc =", rc)

    # ---------------------------------------------------------------------
    # Lab 2 requirement: insert hardware sensor JSON into MongoDB
    # ---------------------------------------------------------------------
    def update(self, client, userdata, msg):
        try:
            payload = msg.payload.decode("utf-8")

            # DEBUG: prove backend is receiving hardware messages
            print("MQTT RX:", msg.topic, payload)

            data = loads(payload)

            ok = self.mongo.addUpdate(data)

            if ok:
                print("DB: inserted")
            else:
                print("DB: insert failed (maybe duplicate timestamp)")
        except Exception as e:
            print("MQTT update error:", str(e))