import { defineStore } from "pinia";
import { ref } from "vue";

export const useMqttStore = defineStore(
  "mqtt",
  () => {
    // STATES
    const mqtt = ref(null);

    // CTRL+F: MQTT_HOST
    const host = ref("www.yanacreations.com");

    // CTRL+F: MQTT_WS_PORT
    // NOTE: This is a WebSocket port, NOT 1883.
    // Ask your demonstrator for the correct WS port if this doesn’t connect.
    const port = ref(9001);

    const payload = ref({});
    const payloadTopic = ref("");
    const subTopics = ref({});

    const onSuccess = () => {
      // connect ack received
    };

    const onConnected = (reconnect, URI) => {
      console.log(`Connected to: ${URI} , Reconnect: ${reconnect}`);
      if (reconnect) {
        const topics = Object.keys(subTopics.value);
        if (topics.length > 0) {
          topics.forEach((topic) => {
            subscribe(topic);
          });
        }
      }
    };

    const onConnectionLost = (response) => {
      if (response.errorCode !== 0) {
        console.log(`MQTT: Connection lost - ${response.errorMessage}`);
      }
    };

    const onFailure = (response) => {
      const hostName = response.invocationContext.host;
      console.log(
        `MQTT: Connection to ${hostName} failed.\nError message: ${response.errorMessage}`
      );
    };

    const onMessageArrived = (response) => {
      try {
        payload.value = JSON.parse(response.payloadString);
        payloadTopic.value = response.destinationName;
        console.log(
          `Topic: ${payloadTopic.value}\nPayload: ${response.payloadString}`
        );
      } catch (error) {
        console.log(`onMessageArrived Error: ${error}`);
      }
    };

    const makeid = (length) => {
      let result = "";
      const characters =
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
      const charactersLength = characters.length;

      for (let i = 0; i < length; i++) {
        result += characters.charAt(
          Math.floor(Math.random() * charactersLength)
        );
      }
      return `IOT_F_${result}`;
    };

    // SUBSCRIBE
    const sub_onSuccess = (response) => {
      const topic = response.invocationContext.topic;
      console.log(`MQTT: Subscribed to - ${topic}`);
      subTopics.value[topic] = "subscribed";
    };

    const sub_onFailure = (response) => {
      const topic = response.invocationContext.topic;
      console.log(
        `MQTT: Failed to subscribe to - ${topic}\nError message: ${response.errorMessage}`
      );
    };

    const subscribe = (topic) => {
      try {
        const subscribeOptions = {
          onSuccess: sub_onSuccess,
          onFailure: sub_onFailure,
          invocationContext: { topic },
        };
        mqtt.value.subscribe(topic, subscribeOptions);
      } catch (error) {
        console.log(`MQTT: Unable to Subscribe ${error}`);
      }
    };

    // UNSUBSCRIBE
    const unSub_onSuccess = (response) => {
      const topic = response.invocationContext.topic;
      console.log(`MQTT: Unsubscribed from - ${topic}`);
      delete subTopics.value[topic];
    };

    const unSub_onFailure = (response) => {
      const topic = response.invocationContext.topic;
      console.log(
        `MQTT: Failed to unsubscribe from - ${topic}\nError message: ${response.errorMessage}`
      );
    };

    const unsubcribe = (topic) => {
      const unsubscribeOptions = {
        onSuccess: unSub_onSuccess,
        onFailure: unSub_onFailure,
        invocationContext: { topic },
      };
      mqtt.value.unsubscribe(topic, unsubscribeOptions);
    };

    const unsubcribeAll = () => {
      const topics = Object.keys(subTopics.value);
      if (topics.length > 0) {
        topics.forEach((topic) => {
          const unsubscribeOptions = {
            onSuccess: unSub_onSuccess,
            onFailure: unSub_onFailure,
            invocationContext: { topic },
          };
          mqtt.value.unsubscribe(topic, unsubscribeOptions);
        });
      }
      disconnect();
    };

    // PUBLISH
    const publish = (topic, payloadStr) => {
      const message = new Paho.MQTT.Message(payloadStr);
      message.destinationName = topic;
      mqtt.value.send(message);
    };

    // DISCONNECT
    const disconnect = () => {
      mqtt.value.disconnect();
    };

    // NEW: set broker easily
    const setBroker = (newHost, newPort) => {
      host.value = newHost;
      port.value = newPort;
    };

    // CONNECT
    const connect = () => {
      const IDstring = makeid(12);

      console.log(`MQTT: Connecting to Server: ${host.value} Port: ${port.value}`);

      // NOTE: For Paho WS, the path is often "/mqtt" or "/ws"
      // You are using "/mqtt" in your original code; we keep it.
      mqtt.value = new Paho.MQTT.Client(host.value, port.value, "/mqtt", IDstring);

      const options = {
        timeout: 3,
        onSuccess,
        onFailure,
        invocationContext: { host: host.value, port: port.value },
        useSSL: false,
        reconnect: true,
        uris: [`ws://${host.value}:${port.value}/mqtt`],
      };

      mqtt.value.onConnectionLost = onConnectionLost;
      mqtt.value.onMessageArrived = onMessageArrived;
      mqtt.value.onConnected = onConnected;

      mqtt.value.connect(options);
    };

    return {
      payload,
      payloadTopic,
      subscribe,
      unsubcribe,
      unsubcribeAll,
      publish,
      connect,
      disconnect,
      setBroker,
    };
  },
  { persist: true }
);