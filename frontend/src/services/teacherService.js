import axios from 'axios';

export const teacherService = {
  // ดึงข้อมูลกิจกรรมล่าสุดของครูคนนี้ (FastAPI จะรู้เองว่าเป็นใครจาก JWT Token)
  getMyRecentActivities() {
    return axios.get('/teacher/recent-activities');
  }
};