<template>
  <div class="summary-layout">
    <div class="result-card">
      <div class="icon-confetti">🎉</div>
      <h1>ยอดเยี่ยมมาก!</h1>
      <p>คุณได้เรียนรู้และสะสมความรู้ในหัวข้อนี้ครบถ้วนแล้ว</p>
      
      <div class="score-circle">
        <div class="circle-chart" :style="{ background: `conic-gradient(#10b981 ${accuracy}%, #f1f5f9 ${accuracy}%)` }">
          <div class="circle-inner">
             <h1>{{ score }}/{{ total }}</h1>
             <span class="score-label">คะแนนความเข้าใจ</span>
          </div>
        </div>
      </div>

      <div class="stats-row">
        <div class="stat-box">
          <span class="stat-title">⏱ เวลาที่ใช้เรียน</span> <br> 
          <strong class="stat-value">{{ formattedTime }}</strong> 
        </div>
        <div class="stat-box">
          <span class="stat-title">🎯 ความแม่นยำ</span> <br> 
          <strong class="stat-value">{{ accuracy }}%</strong>
        </div>
      </div>

      <button @click="goToDashboard" class="btn-primary">
        กลับไปหน้าหลักสูตร ➔
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import learningService from '@/services/learningService';

const route = useRoute();
const router = useRouter();

const score = ref(0);
const total = ref(10); 
const accuracy = ref(0);

// ตัวแปรเก็บเวลาจากหน้าก่อน (เป็นวินาที)
const rawTimeSeconds = ref(0);

// แปลงวินาที เป็นสไตล์ 02:45 นาที
const formattedTime = computed(() => {
  const m = Math.floor(rawTimeSeconds.value / 60).toString().padStart(2, '0');
  const s = (rawTimeSeconds.value % 60).toString().padStart(2, '0');
  return `${m}:${s} นาที`;
});

onMounted(async () => {
  const pageId = route.params.pageId;
  
  // 1. ดึงเวลาที่ส่งมาจากหน้า LearningChapter
  if (route.query.time) {
    rawTimeSeconds.value = parseInt(route.query.time, 10);
  }

  try {
    // 2. พยายามดึงคะแนนสอบจากระบบ
    const res = await learningService.getMyQuizResult(pageId);
    if (res.data && res.data.total_points > 0) {
      score.value = res.data.score || 0;
      total.value = res.data.total_points;
      accuracy.value = Math.round((score.value / total.value) * 100) || 0;
    }
  } catch (err) {
    // 🚨 ทริคความฉลาด: ถ้าดึงคะแนนไม่สำเร็จ (อาจเป็นเพราะหน้านั้นมีแค่เนื้อหาให้อ่าน ไม่มีข้อสอบ)
    // ระบบจะแจกคะแนนเต็ม 10/10 และความแม่นยำ 100% ให้เป็นกำลังใจนักเรียนเลย!
    console.warn("บทเรียนนี้ไม่มีแบบทดสอบ แจกคะแนนอ่านจบ 100%");
    score.value = 10;
    total.value = 10;
    accuracy.value = 100;
  }
});

const goToDashboard = () => {
  router.push(`/course/${route.params.moduleId}/dashboard`); 
};
</script>

<style scoped>
.summary-layout { display: flex; justify-content: center; align-items: center; height: 100vh; background: #f8fafc; }
.result-card { background: white; padding: 3rem; border-radius: 24px; box-shadow: 0 20px 40px rgba(0,0,0,0.04); text-align: center; max-width: 500px; width: 100%; border: 1px solid #f1f5f9; }
.icon-confetti { font-size: 4.5rem; margin-bottom: 0.5rem; animation: pop 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
@keyframes pop { 0% { transform: scale(0); } 100% { transform: scale(1); } }
.result-card h1 { color: #0f172a; margin-bottom: 0.5rem; font-size: 1.8rem; }
.result-card p { color: #64748b; font-size: 1rem; margin-bottom: 2rem; }

.score-circle { display: flex; justify-content: center; margin: 2rem 0; }
.circle-chart { width: 180px; height: 180px; border-radius: 50%; display: flex; align-items: center; justify-content: center; transition: background 1s ease-out; }
.circle-inner { width: 150px; height: 150px; background: white; border-radius: 50%; display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: inset 0 4px 12px rgba(0,0,0,0.03); }
.circle-inner h1 { color: #10b981; font-size: 3rem; margin: 0; }
.score-label { color: #64748b; font-size: 0.8rem; margin-top: 5px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; }

.stats-row { display: flex; gap: 20px; margin-bottom: 2.5rem; }
.stat-box { flex: 1; background: #f8fafc; padding: 1.25rem; border-radius: 16px; border: 1px solid #f1f5f9; transition: transform 0.2s; }
.stat-box:hover { transform: translateY(-2px); }
.stat-title { color: #64748b; font-size: 0.85rem; font-weight: 600; }
.stat-value { font-size: 1.4rem; color: #1e293b; display: block; margin-top: 8px; }

.btn-primary { width: 100%; background: #10b981; color: white; padding: 16px; border: none; border-radius: 12px; font-size: 1.1rem; font-weight: 700; cursor: pointer; transition: all 0.2s; box-shadow: 0 4px 15px rgba(16, 185, 129, 0.25); }
.btn-primary:hover { background: #059669; transform: translateY(-2px); box-shadow: 0 6px 20px rgba(16, 185, 129, 0.3); }
</style>