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
  min-height: 100vh; /* ให้หน้าเว็บสูงเต็มจอเสมอ */
}

.main-container {
  display: flex;
  flex: 1; /* ให้ส่วนกลางขยายเต็มพื้นที่ที่เหลือระหว่าง Navbar กับ Footer */
  overflow: hidden; /* ป้องกัน Scroll ซ้อนกัน */
}

.content-area {
  flex: 1;
  overflow-y: auto; /* ให้เลื่อนดูเนื้อหาบทเรียนได้ */
  background-color: #ffffff;
  padding: 0; /* เราจะไปคุม Padding ในหน้าเนื้อหาแทนเพื่อให้เป๊ะตามดีไซน์ */
}
</style>