<template>
  <v-container fluid class="d-flex justify-center">
    <v-row class="w-100" style="max-width: 1200px" justify="center">
      <v-col cols="12" md="7" align="center">
        <v-sheet
          class="mb-1 rounded-t-lg"
          color="surface"
          elevation="0"
          max-width="800"
          width="100%"
        >
          <v-card
            class="text-secondary"
            title="LED Controls"
            subtitle="Recent settings"
            color="surface"
            variant="tonal"
            flat
          />
        </v-sheet>

        <v-sheet
          class="mb-1"
          color="surface"
          elevation="0"
          max-width="800"
          width="100%"
        >
          <v-card class="pt-5" color="surface" variant="tonal">
            <v-slider
              class="pt-2 bg-surface"
              v-model="led.brightness"
              append-icon="mdi:mdi-car-light-high"
              density="compact"
              thumb-size="16"
              color="secondary"
              label="Brightness"
              direction="horizontal"
              min="0"
              max="250"
              step="10"
              show-ticks
              thumb-label="always"
            />
          </v-card>
        </v-sheet>

        <v-sheet
          class="mb-1 d-flex justify-center align-center"
          color="surface"
          elevation="0"
          max-width="800"
          width="100%"
        >
          <v-card class="pt-5" color="surface" variant="tonal" width="100%">
            <v-slider
              class="pt-2 bg-surface"
              v-model="led.leds"
              append-icon="mdi:mdi-led-on"
              density="compact"
              thumb-size="16"
              color="secondary"
              label="LED Nodes"
              direction="horizontal"
              min="1"
              max="7"
              step="1"
              show-ticks
              thumb-label="always"
            />
          </v-card>
        </v-sheet>

        <v-sheet
          class="pa-2 d-flex justify-center align-center"
          color="surface"
          elevation="0"
          max-width="800"
          width="100%"
          border
        >
          <v-progress-circular
            :model-value="led.leds * 15"
            :color="indicatorColor"
            rotate="0"
            size="200"
            width="15"
          >
            <span class="text-onSurface font-weight-bold">
              {{ led.leds }} LED(s)
            </span>
          </v-progress-circular>
        </v-sheet>
      </v-col>

      <v-col cols="12" md="5" align="center">
        <v-color-picker v-model="led.color" />
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { computed, reactive, watch, onMounted } from "vue";
import { useMqttStore } from "@/store/mqttStore";

// CTRL+F: SUB_TOPIC
const SUB_TOPIC = "620167361_sub";

const Mqtt = useMqttStore();

const led = reactive({
  brightness: 255,
  leds: 1,
  color: { r: 255, g: 0, b: 255, a: 1 },
});

let ID = 1000;

onMounted(() => {
  Mqtt.connect();
});

// WATCHERS
watch(
  led,
  (controls) => {
    clearTimeout(ID);
    ID = setTimeout(() => {
      const message = JSON.stringify({
        type: "controls",
        brightness: controls.brightness,
        leds: controls.leds,
        color: controls.color,
      });

      // DEBUG: prove publish is happening
      console.log("PUBLISHING TO", SUB_TOPIC, message);

      Mqtt.publish(SUB_TOPIC, message);
    }, 1000);
  },
  { deep: true }
);

// COMPUTED PROPERTIES
const indicatorColor = computed(() => {
  return `rgba(${led.color.r},${led.color.g},${led.color.b},${led.color.a})`;
});
</script>