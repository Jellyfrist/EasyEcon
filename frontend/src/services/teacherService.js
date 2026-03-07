import axios from 'axios';

export const teacherService = {
  getMyRecentActivities() {
    return axios.get('/teacher/recent-activities');
  }
};