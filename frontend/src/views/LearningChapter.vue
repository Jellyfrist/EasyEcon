<template>
  <div v-if="pageData" class="study-page">
    <article class="content-render">
      <span class="badge">TOPIC {{ pageData.order_index }}</span>
      <h2>{{ pageData.title }}</h2>
      
      <div v-for="block in pageData.content_blocks" :key="block.id" class="content-block">
        
        <div v-if="block.type === 'rich_text_section'" class="rich-text-section">
          <div v-html="block.data.html" class="html-content"></div>
        </div>

        <div v-else-if="block.type === 'mini_quiz'" class="quiz-card">
             </div>

      </div>
    </article>

    <footer class="bottom-nav">
      <button @click="router.back()" class="prev-btn">❮ ย้อนกลับ</button>
      <button @click="finishLesson" class="next-btn">เรียนจบแล้ว ❯</button>
    </footer>
  </div>
  <div v-else class="loading">กำลังเตรียมบทเรียน...</div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import learningService from '@/services/learningService';
import { useLearningStore } from '@/store/learningStore'; // 🚨 เพิ่ม Store เข้ามาเพื่อดึงรายชื่อบทเรียน

const route = useRoute();
const router = useRouter();
const learningStore = useLearningStore();
const pageData = ref(null);

// ระบบจับเวลา
const timeSpent = ref(0);
let timer = null;

// สร้างฟังก์ชันแยกสำหรับโหลดข้อมูลบทเรียน (เพื่อให้เรียกซ้ำได้ตอนไปหน้าถัดไป)
const loadLesson = async (pageId) => {
  pageData.value = null; // เคลียร์ข้อมูลเก่าให้ขึ้นหน้าจอ Loading
  try {
    const res = await learningService.studyPage(pageId);
    pageData.value = res.data;
    
    // รีเซ็ตและเริ่มจับเวลาใหม่
    timeSpent.value = 0;
    if (timer) clearInterval(timer);
    timer = setInterval(() => {
      timeSpent.value += 1;
    }, 1000);
  } catch (err) {
    console.error("โหลดข้อมูลบทเรียนล้มเหลว", err);
  }
};

onMounted(() => {
  loadLesson(route.params.pageId);
});

onUnmounted(() => {
  if (timer) clearInterval(timer);
});

// ✨ ไฮไลต์สำคัญ: ดักจับเวลา URL เปลี่ยน (เช่น ตอนเด้งไปหน้าถัดไป)
// เพื่อให้หน้าเว็บไปดึงข้อมูลบทเรียนใหม่มาโชว์โดยไม่ต้อง Refresh หน้าเว็บ
watch(
  () => route.params.pageId,
  (newPageId) => {
    if (newPageId) {
      loadLesson(newPageId);
    }
  }
);

const finishLesson = async () => {
  try {
    // 1. ส่งข้อมูลไป Backend ว่าเรียนจบหน้านี้แล้ว
    await learningService.completePage(route.params.pageId);
    
    // 2. ดึงรายการบทเรียนทั้งหมดใน Module นี้มาดู
    const moduleId = route.params.moduleId;
    const currentPageId = parseInt(route.params.pageId, 10);
    
    const res = await learningStore.fetchModuleDashboard(moduleId);
    const lessons = res.lessons || [];
    
    // 3. หาตำแหน่งของหน้าปัจจุบันในลิสต์
    const currentIndex = lessons.findIndex(lesson => lesson.id === currentPageId);
    
    if (currentIndex !== -1 && currentIndex < lessons.length - 1) {
      // ⏭ ถ้าไม่ใช่หน้าสุดท้าย ให้พาไปหน้าถัดไปเลย!
      const nextPageId = lessons[currentIndex + 1].id;
      router.push(`/course/${moduleId}/lesson/${nextPageId}`);
    } else {
      // 🏆 ถ้าเป็นหน้าสุดท้ายของบทนี้แล้ว ค่อยพาไปหน้าสรุปคะแนน
      router.push(`/course/${moduleId}/complete/learn/${route.params.pageId}?time=${timeSpent.value}`);
    }
  } catch (err) {
    console.error("เกิดข้อผิดพลาดในการเปลี่ยนหน้า:", err);
    // กันเหนียว ถ้าเน็ตหลุดหรือมีปัญหา ให้เด้งกลับไปหน้า Dashboard 
    router.push(`/course/${route.params.moduleId}/dashboard`);
  }
};
</script>

<style scoped>
.study-page { max-width: 800px; margin: 0 auto; padding: 2rem; background: white; min-height: 100vh; box-shadow: 0 0 20px rgba(0,0,0,0.02); }
.badge { display: inline-block; background: #fdf2f8; color: #e91e63; padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.05em; margin-bottom: 1rem; }
.content-render h2 { font-size: 2rem; color: #0f172a; margin-bottom: 2rem; border-bottom: 2px solid #f1f5f9; padding-bottom: 1rem; }

.content-block { margin-bottom: 24px; }
.html-content :deep(h1) { font-size: 2rem; margin-top: 2rem; margin-bottom: 1rem; color: #0f172a; }
.html-content :deep(h2) { font-size: 1.5rem; margin-top: 1.5rem; margin-bottom: 1rem; color: #1e293b; }
.html-content :deep(h3) { font-size: 1.25rem; margin-top: 1.5rem; margin-bottom: 0.5rem; color: #334155; }
.html-content :deep(p) { line-height: 1.8; color: #334155; margin-bottom: 1rem; font-size: 1.05rem; }
.html-content :deep(ul), .html-content :deep(ol) { padding-left: 1.5rem; margin-bottom: 1rem; color: #334155; line-height: 1.8; font-size: 1.05rem; }
.html-content :deep(img) { max-width: 100%; height: auto; border-radius: 12px; margin: 1.5rem 0; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }

.bottom-nav { display: flex; justify-content: space-between; margin-top: 4rem; border-top: 1px solid #e2e8f0; padding-top: 2rem; }
.prev-btn { background: transparent; color: #64748b; border: 1px solid #cbd5e1; padding: 12px 24px; border-radius: 8px; font-weight: 600; cursor: pointer; transition: all 0.2s; }
.prev-btn:hover { background: #f8fafc; color: #334155; }
.next-btn { background: #10b981; color: white; border: none; padding: 12px 24px; border-radius: 8px; font-weight: 600; cursor: pointer; transition: all 0.2s; box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2); }
.next-btn:hover { background: #059669; transform: translateY(-2px); }
.loading { text-align: center; padding: 5rem; color: #64748b; }
</style>