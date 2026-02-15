<template>
  <v-container fluid class="bg-surface" align="center">
    <!-- Row 1: Temperature Graph and Info Cards -->
    <v-row class="max-width-1200">
      <v-col cols="9">
        <figure class="highcharts-figure">
          <div id="container"></div>
        </figure>
      </v-col>

      <v-col cols="3">
        <v-card class="mb-5" max-width="500" color="primaryContainer" subtitle="Temperature">
          <v-card-item>
            <span class="text-h3 text-onPrimaryContainer">{{ temperature }}</span>
          </v-card-item>
        </v-card>

        <v-card class="mb-5" max-width="500" color="tertiaryContainer" subtitle="Heat Index (Feels like)">
          <v-card-item>
            <span class="text-h3 text-onTertiaryContainer">{{ heatindex }}</span>
          </v-card-item>
        </v-card>

        <v-card class="mb-5" max-width="500" color="secondaryContainer" subtitle="Humidity">
          <v-card-item>
            <span class="text-h3 text-onSecondaryContainer">{{ humidity }}</span>
          </v-card-item>
        </v-card>
      </v-col>
    </v-row>

    <!-- Row 2: Humidity Graph (Justify Start per Page 12) -->
    <v-row class="max-width-1200" justify="start">
      <v-col cols="9">
        <figure class="highcharts-figure">
          <div id="container1"></div>
        </figure>
      </v-col>
      <!-- Page 12, Bullet 4: Other columns must be set to 3 -->
      <v-col cols="3"></v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { computed, onMounted, onBeforeUnmount } from "vue";
import { useMqttStore } from "@/store/mqttStore";
import { storeToRefs } from "pinia";
import Highcharts from "highcharts";

const mqttStore = useMqttStore();
const { payload } = storeToRefs(mqttStore);

// COMPUTED PROPERTIES (Page 13)
const temperature = computed(() => {
  if (!!payload.value) {
    return `${payload.value.temperature.toFixed(2)} °C`;
  }
  return "0.00 °C";
});

const humidity = computed(() => {
  if (!!payload.value) {
    return `${payload.value.humidity.toFixed(2)} %`;
  }
  return "0.00 %";
});

const heatindex = computed(() => {
  if (!!payload.value) {
    return `${payload.value.heatindex.toFixed(2)} °C`;
  }
  return "0.00 °C";
});

// HIGHCHARTS LOGIC (Spoon-fed version of the Appendix)
onMounted(() => {
  // Initialize Temperature Chart
  Highcharts.chart("container", {
    chart: { type: "line" },
    title: { text: "Temperature Analysis (Live)", align: 'left' },
    xAxis: { type: "datetime" },
    yAxis: { title: { text: "Celsius (°C)" } },
    series: [{ name: "Temperature", data: [] }]
  });

  // Initialize Humidity Chart
  Highcharts.chart("container1", {
    chart: { type: "line" },
    title: { text: "Humidity Analysis (Live)", align: 'left' },
    xAxis: { type: "datetime" },
    yAxis: { title: { text: "Percentage (%)" } },
    series: [{ name: "Humidity", data: [], color: "#00ff00" }]
  });
});
</script>

<style scoped>
.max-width-1200 {
  max-width: 1200px;
}

.highcharts-figure {
  margin: 0;
}
</style>