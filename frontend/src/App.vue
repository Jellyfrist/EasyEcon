<template>
  <div id="app">

    <!-- Conditionally display the Navbar -->
    <Navbar v-if="showNavbar" />

    <!-- Conditionally display the DashboardHero -->
    <DashboardHero v-if="showDashboardHero" />

    <!-- Page content -->
    <router-view />

    <!-- Conditionally display the Footer -->
    <Footer v-if="showFooter" />

  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';

import Navbar from '@/components/Navbar.vue';
import Footer from '@/components/Footer.vue';
import DashboardHero from '@/components/DashboardHero.vue';

const route = useRoute();

// Show the Navbar for the main layout; hide it for the auth layout
const showNavbar = computed(() => {
  return route.meta.showNavbar === true;
});

// Show the Footer for the main layout; hide it for the auth layout
const showFooter = computed(() => {
  return route.meta.showFooter === true;
});

// Show the DashboardHero only for the Feature Dashboard layout
const showDashboardHero = computed(() => {
  return route.meta.showDashboardHero === true;
});

</script>

<style>
@import './style.css';

* {
  font-family: 'Kanit', 'Lexend', sans-serif;
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  margin: 0;
  min-height: 100vh;
}

#app {
  width: 100%;
  min-height: 100vh;
}
</style>