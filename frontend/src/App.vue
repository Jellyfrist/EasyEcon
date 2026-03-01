<template>
    <div id="app">
        <!-- Conditionally show Navbar -->
        <Navbar v-if="showNavbar" />
    
        <DashboardHero v-if="showDashboardHero" />
    
        <!-- Page content -->
        <router-view />
    
        <!-- Conditionally show Footer -->
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

// Show navbar for main layout, hide for auth layout
const showNavbar = computed(() => {
    return route.meta.showNavbar === true;
});

// Show Footer for main layout, hide for auth layout
const showFooter = computed(() => {
    return route.meta.showFooter === true;
});

// Show DashboardHero for Feature Dashboard layout
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