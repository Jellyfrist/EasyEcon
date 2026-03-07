<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <button @click="router.push('/dashboard')" class="back-btn">
        ← กลับไปที่คลังบทเรียน
      </button>
      <p class="list-title">รายชื่อบทเรียน ({{ modules.length }} บท)</p>
    </div>

    <nav class="module-list">
      <div 
        v-for="mod in modules" 
        :key="mod.id"
        :class="['module-card', { active: activeModuleId === mod.id }]"
        @click="selectModule(mod.id)"
      >
        <div class="module-info">
          <span class="module-label">บทที่ {{ mod.order_index }}</span>
          <p class="module-name">{{ mod.title }}</p>
        </div>
        <span v-if="activeModuleId === mod.id" class="active-dot">●</span>
      </div>
    </nav>
  </aside>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import learningService from '@/services/learningService';

const router = useRouter();
const route = useRoute();
const modules = ref([]);

const fetchModules = async () => {
  try {
    const courseId = 1;
    const res = await learningService.listModules(courseId);
    modules.value = res.data;
  } catch (error) {
    console.error("Sidebar Error:", error);
  }
};

const activeModuleId = computed(() => {
  return Number(route.query.module_id) || (modules.value[0]?.id);
});

const selectModule = (id) => {
  router.push({ path: '/learning/dashboard', query: { module_id: id } });
};

onMounted(fetchModules);
</script>

<style scoped>
.sidebar {
  width: 320px;
  background-color: #fafafa;
  border-right: 1px solid #eee;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 1.5rem;
}

.back-btn {
  width: 100%;
  padding: 10px;
  border-radius: 8px;
  border: 1px solid #ddd;
  background: white;
  cursor: pointer;
  margin-bottom: 1.5rem;
}

.list-title {
  font-size: 0.85rem;
  color: #888;
  font-weight: 600;
}

.module-list {
  flex: 1;
  overflow-y: auto;
  padding: 0 1rem;
}

.module-card {
  padding: 1rem;
  border-radius: 12px;
  margin-bottom: 0.5rem;
  cursor: pointer;
  border: 1px solid transparent;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.2s;
}

.module-card.active {
  background-color: #fff1f2;
  border-color: #e63946;
}

.module-label {
  font-size: 0.75rem;
  color: #999;
}

.active .module-label {
  color: #e63946;
  font-weight: bold;
}

.module-name {
  font-size: 0.95rem;
  margin-top: 4px;
}

.active .module-name {
  color: #e63946;
  font-weight: 600;
}

.active-dot {
  color: #e63946;
}
</style>