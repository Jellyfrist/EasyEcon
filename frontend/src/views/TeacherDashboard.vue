<template>
  <div class="teacher-dashboard">
    <section class="welcome-banner">
      <div class="banner-content">
        <h1>Good Morning, Professor!</h1>
        <p>Ready to create something new today? Your students are performing 12% better than last semester. Keep up the great momentum!</p>
      </div>
    </section>

    <section class="quick-actions-section">
      <div class="section-header">
        <h2>Quick Actions</h2>
        <button class="view-all-btn">View all tools</button>
      </div>
      
      <div class="actions-grid">
        <div class="action-card">
          <div class="icon-wrapper pink-bg">🗂️</div>
          <h3>Create Flashcard Set</h3>
          <p>Master core economic concepts with interactive visual aids.</p>
          <button class="action-link pink-text" @click="goTo('/teacher/flashcards/new')">
            START CREATING ➔
          </button>
        </div>

        <div class="action-card">
          <div class="icon-wrapper green-bg">📖</div>
          <h3>Build New Lesson</h3>
          <p>Design engaging lectures with rich media and interactive charts.</p>
          <button class="action-link green-text" @click="goTo('/teacher/lesson-editor/new')">
            BUILD NOW ➔
          </button>
        </div>

        <div class="action-card">
          <div class="icon-wrapper blue-bg">📋</div>
          <h3>Design New Test</h3>
          <p>Generate comprehensive assessments with automated grading.</p>
          <button class="action-link blue-text" @click="goTo('/teacher/exams/new')">
            DESIGN TEST ➔
          </button>
        </div>
      </div>
    </section>

    <section class="recent-activity-section">
        <div class="section-header">
        <h2>Recent Activity</h2>
        <div class="filter-tabs">
            <span class="tab active">All Projects</span>
            <span class="tab">In Progress</span>
        </div>
        </div>

        <div v-if="isLoading" class="loading-state">
        <p>กำลังโหลดโปรเจกต์ของคุณ...</p>
        </div>

        <div v-else-if="recentActivities.length === 0" class="empty-state">
        <p>คุณยังไม่มีโปรเจกต์ ลองสร้างบทเรียนแรกดูสิ!</p>
        </div>

        <div v-else class="activity-list">
        <div v-for="item in recentActivities" :key="`${item.type}-${item.id}`" class="activity-item">
            <div class="item-left">
            <div :class="['activity-icon', getTheme(item.type)]">{{ getIcon(item.type) }}</div>
            <div class="activity-details">
                <h4>{{ item.title }}</h4>
                <p>อัปเดตเมื่อ {{ formatDate(item.updated_at) }} • {{ item.meta_info }}</p>
            </div>
            </div>
            <div class="item-right">
            <button class="btn-preview" @click="previewItem(item)">Preview</button>
            <button class="btn-edit" @click="editItem(item)">Edit</button>
            </div>
        </div>
        </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
// สมมติว่าใบชาแยก service ของครูไว้ หรือใช้ learningService ตัวเดิมก็ได้
import { teacherService } from '@/services/teacherService'; 

const router = useRouter();
const recentActivities = ref([]);
const isLoading = ref(true);

// --- ฟังก์ชัน Helper จัดการความสวยงาม ---
const getIcon = (type) => {
  if (type === 'lesson') return '📖';
  if (type === 'exam') return '📋';
  if (type === 'flashcard') return '🗂️';
  return '📁';
};

const getTheme = (type) => {
  if (type === 'lesson') return 'green-theme';
  if (type === 'exam') return 'blue-theme';
  if (type === 'flashcard') return 'pink-theme';
  return 'gray-theme';
};

const formatDate = (dateString) => {
  if (!dateString) return 'ไม่ทราบเวลา';
  const date = new Date(dateString);
  return date.toLocaleDateString('th-TH', { year: 'numeric', month: 'short', day: 'numeric' });
};

// --- ดึงข้อมูลจาก Backend ---
const fetchMyProjects = async () => {
  isLoading.value = true;
  try {
    // API นี้ Backend ต้องดึงเฉพาะของ User ที่ล็อกอิน (เช็คจาก Token)
    const res = await teacherService.getMyRecentActivities();
    recentActivities.value = res.data;
  } catch (error) {
    console.error("ดึงข้อมูลโปรเจกต์ล้มเหลว:", error);
  } finally {
    isLoading.value = false;
  }
};

onMounted(fetchMyProjects);

// --- ระบบนำทาง (จราจรของปุ่ม Edit / Preview) ---
const previewItem = (item) => {
  // เวลาพรีวิว ให้พาไปหน้าเดียวกับที่นักเรียนเห็น
  if (item.type === 'lesson') router.push(`/learning/page/${item.id}`);
  else if (item.type === 'exam') router.push(`/exam/preview/${item.id}`);
  else if (item.type === 'flashcard') router.push(`/flashcard/preview/${item.id}`);
};

const editItem = (item) => {
  // เวลาแก้ไข พาเข้าหลังบ้านครู (ระบบ Editor)
  if (item.type === 'lesson') router.push(`/teacher/lessons/edit/${item.id}`);
  else if (item.type === 'exam') router.push(`/teacher/exams/edit/${item.id}`);
  else if (item.type === 'flashcard') router.push(`/teacher/flashcards/edit/${item.id}`);
};

// ฟังก์ชันสำหรับ Quick Actions ด้านบน (เหมือนเดิม)
const goTo = (path) => {
  router.push(path);
};
</script>

<style scoped>
.loading-state, .empty-state {
  text-align: center;
  padding: 3rem;
  color: #64748b;
  background: white;
  border-radius: 12px;
  border: 1px dashed #cbd5e1;
}

/* พื้นที่หลัก จำกัดความกว้างไม่ให้หน้าจอดูโล่งเกินไปตอนไม่มี Sidebar */
.teacher-dashboard {
  max-width: 1000px;
  margin: 0 auto;
  padding: 2rem;
  font-family: 'Prompt', sans-serif; /* แนะนำให้ใช้ฟอนต์ Prompt เพื่อความสวยงาม */
}

/* 1. Welcome Banner */
.welcome-banner {
  background: linear-gradient(135deg, #ff4d8d, #e91e63);
  border-radius: 20px;
  padding: 2.5rem 3rem;
  color: white;
  margin-bottom: 2.5rem;
  box-shadow: 0 10px 25px rgba(244, 63, 94, 0.2);
}
.welcome-banner h1 { margin: 0 0 10px 0; font-size: 2rem; }
.welcome-banner p { margin: 0; font-size: 1.05rem; opacity: 0.9; line-height: 1.5; max-width: 700px; }

/* Section Headers */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}
.section-header h2 { margin: 0; font-size: 1.4rem; color: #1e293b; }
.view-all-btn { background: none; border: none; color: #f43f5e; font-weight: 600; cursor: pointer; }

/* 2. Quick Actions Grid */
.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}
.action-card {
  background: white;
  border-radius: 16px;
  padding: 1.8rem;
  box-shadow: 0 4px 15px rgba(0,0,0,0.03);
  border: 1px solid #f1f5f9;
  transition: transform 0.2s;
}
.action-card:hover { transform: translateY(-5px); }
.icon-wrapper {
  width: 50px; height: 50px;
  border-radius: 12px;
  display: flex; justify-content: center; align-items: center;
  font-size: 1.5rem; margin-bottom: 1rem;
}
.action-card h3 { margin: 0 0 10px 0; font-size: 1.2rem; color: #1e293b; }
.action-card p { margin: 0 0 20px 0; font-size: 0.9rem; color: #64748b; line-height: 1.5; min-height: 40px; }
.action-link {
  background: none; border: none; font-weight: bold; font-size: 0.85rem; cursor: pointer; padding: 0; letter-spacing: 0.5px;
}

/* Colors for Quick Actions */
.pink-bg { background: #ffe4e6; color: #e11d48; }
.pink-text { color: #e11d48; }
.green-bg { background: #dcfce7; color: #16a34a; }
.green-text { color: #16a34a; }
.blue-bg { background: #dbeafe; color: #2563eb; }
.blue-text { color: #2563eb; }

/* 3. Recent Activity */
.filter-tabs { display: flex; gap: 15px; }
.filter-tabs .tab { color: #64748b; font-size: 0.9rem; font-weight: 500; cursor: pointer; }
.filter-tabs .tab.active { color: #f43f5e; border-bottom: 2px solid #f43f5e; padding-bottom: 4px; }

.activity-list { display: flex; flex-direction: column; gap: 1rem; }
.activity-item {
  display: flex; justify-content: space-between; align-items: center;
  background: white; padding: 1.2rem 1.5rem;
  border-radius: 12px; border: 1px solid #f1f5f9;
  box-shadow: 0 2px 8px rgba(0,0,0,0.02);
}
.item-left { display: flex; align-items: center; gap: 1rem; }
.activity-icon {
  width: 45px; height: 45px; border-radius: 10px;
  display: flex; justify-content: center; align-items: center; font-size: 1.2rem;
}
.activity-details h4 { margin: 0 0 5px 0; font-size: 1.05rem; color: #1e293b; }
.activity-details p { margin: 0; font-size: 0.85rem; color: #64748b; }

.item-right { display: flex; gap: 10px; }
.btn-preview {
  background: none; border: none; color: #f43f5e; font-weight: 500; cursor: pointer; padding: 8px 12px;
}
.btn-edit {
  background: #f43f5e; color: white; border: none; border-radius: 20px;
  padding: 8px 20px; font-weight: 500; cursor: pointer; transition: 0.2s;
}
.btn-edit:hover { background: #e11d48; }

/* Themes for Activity Icons */
.green-theme { background: #dcfce7; }
.blue-theme { background: #dbeafe; }
.pink-theme { background: #ffe4e6; }
</style>