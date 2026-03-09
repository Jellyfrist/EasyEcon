<template>
  <div class="verify-page">
    <div class="card">
      
      <div v-if="isLoading" class="state-box">
        <div class="spinner"></div>
        <h2>กำลังตรวจสอบอีเมลของคุณ...</h2>
        <p class="text-gray-500">กรุณารอสักครู่</p>
      </div>

      <div v-else-if="isSuccess" class="state-box success">
        <span class="material-symbols-outlined icon">check_circle</span>
        <h2>ยืนยันอีเมลสำเร็จ! 🎉</h2>
        <p class="text-gray-500">บัญชีของคุณพร้อมใช้งานแล้ว ระบบจะพาคุณไปหน้าเข้าสู่ระบบ...</p>
        <button @click="goToLogin" class="btn-primary mt-4">ไปหน้าเข้าสู่ระบบทันที</button>
      </div>

      <div v-else class="state-box error">
        <span class="material-symbols-outlined icon">cancel</span>
        <h2>ไม่สามารถยืนยันอีเมลได้ ❌</h2>
        <p class="text-gray-500">{{ errorMessage }}</p>
        <button @click="goToLogin" class="btn-outline mt-4">กลับไปหน้าเข้าสู่ระบบ</button>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import authService from '@/services/authService'; // ปรับ path ให้ตรงกับโปรเจกต์คุณ

const route = useRoute();
const router = useRouter();

const isLoading = ref(true);
const isSuccess = ref(false);
const errorMessage = ref('ลิงก์ยืนยันไม่ถูกต้อง หรือหมดอายุแล้ว');

onMounted(async () => {
  // ดึงค่า token จาก URL query (?token=...)
  const token = route.query.token;

  if (!token) {
    isLoading.value = false;
    isSuccess.value = false;
    return;
  }

  try {
    // ส่งไปเช็คกับ Backend
    await authService.verifyEmail(token);
    isSuccess.value = true;
    
    // สำเร็จปุ๊บ ให้นับถอยหลัง 3 วินาทีแล้วเด้งไปหน้า Login
    setTimeout(() => {
      goToLogin();
    }, 3000);

  } catch (error) {
    isSuccess.value = false;
    errorMessage.value = error.response?.data?.detail || 'เกิดข้อผิดพลาดในการตรวจสอบ';
  } finally {
    isLoading.value = false;
  }
});

const goToLogin = () => {
  router.push('/login'); // ปรับให้ตรงกับ path หน้า login ของคุณ
};
</script>

<style scoped>
.verify-page { display: flex; justify-content: center; align-items: center; min-height: 100vh; background-color: #f8fafc; font-family: 'Sarabun', sans-serif; }
.card { background: white; padding: 3rem; border-radius: 24px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); text-align: center; max-width: 450px; width: 90%; border: 1px solid #f1f5f9; }
.state-box { display: flex; flex-direction: column; align-items: center; gap: 1rem; }
.spinner { width: 50px; height: 50px; border: 4px solid #f1f5f9; border-top-color: #e11d48; border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 1rem; }
@keyframes spin { to { transform: rotate(360deg); } }
.icon { font-size: 72px; margin-bottom: 0.5rem; }
.success .icon { color: #10b981; }
.error .icon { color: #ef4444; }
h2 { color: #0f172a; font-size: 1.5rem; font-weight: 800; margin: 0; }
.text-gray-500 { color: #64748b; margin: 0; line-height: 1.5; }
.btn-primary { background: #e11d48; color: white; padding: 12px 24px; border: none; border-radius: 12px; cursor: pointer; font-weight: 700; width: 100%; transition: all 0.2s; }
.btn-primary:hover { background: #be123c; }
.btn-outline { background: white; color: #64748b; border: 2px solid #e2e8f0; padding: 12px 24px; border-radius: 12px; cursor: pointer; font-weight: 700; width: 100%; transition: all 0.2s; }
.btn-outline:hover { background: #f8fafc; color: #0f172a; }
.mt-4 { margin-top: 1rem; }
</style>