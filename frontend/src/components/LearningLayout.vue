<template>
  <div class="learning-layout">
    <Navbar />

    <div class="main-container">
      <Sidebar />

      <main class="content-area">
        <router-view />
      </main>
    </div>

    <Footer />
  </div>
</template>

<script setup>
import Navbar from '@/components/Navbar.vue';
import Footer from '@/components/Footer.vue';
import Sidebar from '@/components/Sidebar.vue';
</script>

<style scoped>
.learning-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.main-container {
  display: flex;
  flex: 1; 
  overflow: hidden;
}

.content-area {
  flex: 1;
  overflow-y: auto;
  background-color: #ffffff;
  padding: 0; 
}
</style>