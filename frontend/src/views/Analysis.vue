<template>
  <v-container fluid class="bg-surface" align="center">
    <v-row class="pa-1" style="max-width: 1200px">
      <!-- Column 1: Date Range (Page 15) -->
      <v-col>
        <v-sheet padding="2" height="250" class="pa-2">
          <p>Enter date range for Analysis</p>
          <v-divider></v-divider>
          <v-text-field label="Start date" type="Date" density="compact" variant="solo-inverted" class="mr-5" style="max-width: 300px" flat v-model="start"></v-text-field>
          <v-text-field label="End date" type="Date" density="compact" variant="solo-inverted" style="max-width: 300px" flat v-model="end"></v-text-field>
          <v-spacer></v-spacer>
          <v-btn class="text-caption" color="primary" variant="tonal" @click="updateLineCharts(); updateCards(); updateHistogramCharts();">Analyze</v-btn>
        </v-sheet>
      </v-col>

      <!-- Column 2: Temperature MMAR (Page 15-16) -->
      <v-col cols="3" align="center">
        <v-card title="Temperature" width="250" variant="outlined" color="primary" density="compact" rounded="lg">
          <v-card-item class="mb-n5">
            <v-chip-group class="d-flex flex-row justify-center" color="primaryContainer" variant="flat">
              <v-tooltip text="Min" location="start"><template v-slot:activator="{ props }"><v-chip v-bind="props">{{ temperature.min }}</v-chip></template></v-tooltip>
              <v-tooltip text="Range" location="top"><template v-slot:activator="{ props }"><v-chip v-bind="props">{{ temperature.range }}</v-chip></template></v-tooltip>
              <v-tooltip text="Max" location="end"><template v-slot:activator="{ props }"><v-chip v-bind="props">{{ temperature.max }}</v-chip></template></v-tooltip>
            </v-chip-group>
          </v-card-item>
          <v-card-item align="center">
            <span class="text-h1 text-primary font-weight-bold">{{ temperature.avg }}</span>
          </v-card-item>
        </v-card>
      </v-col>

      <!-- Column 3: Humidity MMAR (Page 16) -->
      <v-col cols="3" align="center">
        <v-card title="Humidity" width="250" variant="outlined" color="primary" density="compact" rounded="lg">
          <v-card-item class="mb-n5">
            <v-chip-group class="d-flex flex-row justify-center" color="primaryContainer" variant="flat">
              <v-tooltip text="Min" location="start"><template v-slot:activator="{ props }"><v-chip v-bind="props">{{ humidity.min }}</v-chip></template></v-tooltip>
              <v-tooltip text="Range" location="top"><template v-slot:activator="{ props }"><v-chip v-bind="props">{{ humidity.range }}</v-chip></template></v-tooltip>
              <v-tooltip text="Max" location="end"><template v-slot:activator="{ props }"><v-chip v-bind="props">{{ humidity.max }}</v-chip></template></v-tooltip>
            </v-chip-group>
          </v-card-item>
          <v-card-item align="center">
            <span class="text-h1 text-primary font-weight-bold">{{ humidity.avg }}</span>
          </v-card-item>
        </v-card>
      </v-col>
    </v-row>

    <!-- Row 2: Main Graphs (Page 16) -->
    <v-row style="max-width: 1200px">
      <v-col cols="12">
        <figure class="highcharts-figure">
          <div id="container"></div>
        </figure>
      </v-col>
      <v-col cols="12">
        <figure class="highcharts-figure">
          <div id="container0"></div>
        </figure>
      </v-col>
    </v-row>

    <!-- Row 3: Analysis Graphs (Page 14/16) -->
    <v-row style="max-width: 1200px">
      <v-col cols="4" border>
        <figure class="highcharts-figure">
          <div id="container1"></div>
        </figure>
      </v-col>
      <v-col cols="4">
        <figure class="highcharts-figure">
          <div id="container2"></div>
        </figure>
      </v-col>
      <v-col cols="4">
        <figure class="highcharts-figure">
          <div id="container3"></div>
        </figure>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue";
import Highcharts from "highcharts";
import { useAppStore } from "@/store/appStore";

const AppStore = useAppStore();
const start = ref("");
const end = ref("");

// Refs for Chart instances
const tempHiChart = ref(null);
const humidityChart = ref(null);
const histogramChart = ref(null);
const scatterTempHi = ref(null);
const scatterHumidHi = ref(null);

const temperature = reactive({ min: 0, max: 0, avg: 0, range: 0 });
const humidity = reactive({ min: 0, max: 0, avg: 0, range: 0 });

onMounted(() => {
  // Temp and Heat Index Line Graph
  tempHiChart.value = Highcharts.chart("container", {
    chart: { type: "line", zoomType: "x" },
    title: { text: "Temperature and Heat Index Analysis", align: "left" },
    subtitle: { text: 'The heat index, also known as the "apparent temperature," is a measure that combines air temperature and relative humidity to assess how hot it feels to the human body.' },
    xAxis: { type: "datetime", title: { text: "Time" } },
    yAxis: { title: { text: "Air Temperature & Heat Index" }, labels: { format: "{value} °C" } },
    tooltip: { shared: true, pointFormat: "Humidity: {point.x} % <br/> Temperature: {point.y} °C" },
    series: [
      { name: "Temperature", data: [], color: "#E91E63" },
      { name: "Heat Index", data: [], color: "#2196F3" },
    ],
  });

  // Humidity Analysis
  humidityChart.value = Highcharts.chart("container0", {
    chart: { type: "line", zoomType: "x" },
    title: { text: "Humidity Analysis", align: "left" },
    xAxis: { type: "datetime", title: { text: "Time" } },
    yAxis: { title: { text: "Air Temperature & Heat Index" }, labels: { format: "{value} %" } },
    tooltip: { shared: true, pointFormat: "Humidity: {point.x} % <br/> Temperature: {point.y} °C" },
    series: [{ name: "Humidity", data: [], color: "#4CAF50" }],
  });

  // Frequency Distribution Analysis
  histogramChart.value = Highcharts.chart("container1", {
    chart: { type: "column", zoomType: "x" },
    title: { text: "Frequency Distribution Analysis", align: "left" },
    series: [
      { name: "Temperature", data: [] },
      { name: "Humidity", data: [] },
      { name: "Heat Index", data: [] },
    ],
  });

  // Temperature & Heat Index Correlation
  scatterTempHi.value = Highcharts.chart("container2", {
    chart: { type: "scatter", zoomType: "x" },
    title: { text: "Temperature & Heat Index Correlation Analysis", align: "left" },
    subtitle: { text: "Visualize the relationship between Temperature and Heat Index" },
    xAxis: { title: { text: "Temperature" }, labels: { format: "{value} °C" } },
    yAxis: { title: { text: "Heat Index" }, labels: { format: "{value} °C" } },
    tooltip: { pointFormat: "Temperature: {point.x} °C <br/> Heat Index: {point.y} °C" },
    series: [{ name: "Analysis", data: [] }],
  });

  // Humidity & Heat Index Correlation
  scatterHumidHi.value = Highcharts.chart("container3", {
    chart: { type: "scatter", zoomType: "x" },
    title: { text: "Humidity & Heat Index Correlation Analysis", align: "left" },
    subtitle: { text: "Visualize the relationship between Humidity and Heat Index" },
    xAxis: { title: { text: "Humidity" }, labels: { format: "{value} %" } },
    yAxis: { title: { text: "Heat Index" }, labels: { format: "{value} °C" } },
    tooltip: { pointFormat: "Humidity: {point.x} % <br/> Heat Index: {point.y} °C" },
    series: [{ name: "Analysis", data: [] }],
  });
});

const updateCards = async () => {
  if (!!start.value && !!end.value) {
    let startDate = new Date(start.value).getTime() / 1000;
    let endDate = new Date(end.value).getTime() / 1000;
    const temp = await AppStore.getTemperatureMMAR(startDate, endDate);
    const humid = await AppStore.getHumidityMMAR(startDate, endDate);
    if (temp && temp[0]) {
      temperature.max = temp[0].max.toFixed(1);
      temperature.min = temp[0].min.toFixed(1);
      temperature.avg = temp[0].avg.toFixed(1);
      temperature.range = temp[0].range.toFixed(1);
    }
    if (humid && humid[0]) {
      humidity.max = humid[0].max.toFixed(1);
      humidity.min = humid[0].min.toFixed(1);
      humidity.avg = humid[0].avg.toFixed(1);
      humidity.range = humid[0].range.toFixed(1);
    }
  }
};

const updateHistogramCharts = async () => {
  if (!!start.value && !!end.value) {
    let startDate = new Date(start.value).getTime() / 1000;
    let endDate = new Date(end.value).getTime() / 1000;
    const tempDist = await AppStore.getFreqDistro("temperature", startDate, endDate);
    const humidDist = await AppStore.getFreqDistro("humidity", startDate, endDate);
    const hiDist = await AppStore.getFreqDistro("heatindex", startDate, endDate);

    histogramChart.value.series[0].setData(tempDist.map((r) => ({ x: r["_id"], y: r["count"] })));
    histogramChart.value.series[1].setData(humidDist.map((r) => ({ x: r["_id"], y: r["count"] })));
    histogramChart.value.series[2].setData(hiDist.map((r) => ({ x: r["_id"], y: r["count"] })));
  }
};

const updateLineCharts = async () => {
  if (!!start.value && !!end.value) {
    let startDate = new Date(start.value).getTime() / 1000;
    let endDate = new Date(end.value).getTime() / 1000;
    const data = await AppStore.getAllInRange(startDate, endDate);

    const tData = [], hData = [], hiData = [], t_hi_corr = [], h_hi_corr = [];

    data.forEach((row) => {
      const ts = row.timestamp * 1000;
      tData.push([ts, row.temperature]);
      hData.push([ts, row.humidity]);
      hiData.push([ts, row.heatindex]);
      t_hi_corr.push([row.temperature, row.heatindex]);
      h_hi_corr.push([row.humidity, row.heatindex]);
    });

    tempHiChart.value.series[0].setData(tData);
    tempHiChart.value.series[1].setData(hiData);
    humidityChart.value.series[0].setData(hData);
    scatterTempHi.value.series[0].setData(t_hi_corr);
    scatterHumidHi.value.series[0].setData(h_hi_corr);
  }
};
</script>