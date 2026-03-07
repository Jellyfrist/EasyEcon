<template>
  <div class="editor-page prose-container">
    <header class="top-navbar">
      <button @click="router.push(`/teacher/modules/${courseId}`)" class="back-btn">
        <span class="material-symbols-outlined">arrow_back</span>
        Back To Module
      </button>
    </header>
    <div class="breadcrumb-bar">
      <button @click="$router.push(`/teacher/modules/${courseIdParam}`)" class="breadcrumb-link" style="background:none; border:none; padding:0; cursor:pointer;">Dashboard</button>
      <span class="material-symbols-outlined breadcrumb-sep">chevron_right</span>
      <span class="breadcrumb-current">Lesson Editor</span>
    </div>

    <div v-if="isLoading" class="state-box">
      <div class="spinner"></div>
      <p>Loading lesson data...</p>
    </div>

    <template v-else>
      <div class="editor-layout">

        <div class="editor-main">
          
          <div class="panel">
            <div class="form-group">
              <label class="field-label">Lesson Title</label>
              <input 
                type="text" 
                v-model="lesson.title" 
                class="input-field lesson-title-input" 
                placeholder="e.g. Introduction to Market Equilibrium" 
              />
            </div>
            <p class="author-text" style="margin-top: 10px;">
              Draft created by <span class="author-name">{{ authorName }}</span>
            </p>
          </div>

          <div class="panel section-editor-card" v-if="activeSection">
            <div class="form-group" style="margin-bottom: 1.5rem;">
              <label class="field-label">Section Name</label>
              <input 
                type="text" 
                v-model="activeSection.title" 
                class="input-field" 
                placeholder="e.g. Why Prices Change..." 
              />
            </div>

            <div class="editor-toolbar">
                <div class="tool-group">
                    <button @mousedown.prevent="execCmd('undo')" title="Undo (Ctrl+Z)" class="icon-btn hover:bg-slate-200 hover:text-rose-500 transition-colors">
                        <span class="material-symbols-outlined">undo</span>
                    </button>
                    <button @mousedown.prevent="execCmd('redo')" title="Redo (Ctrl+Y)" class="icon-btn hover:bg-slate-200 hover:text-rose-500 transition-colors">
                        <span class="material-symbols-outlined">redo</span>
                    </button>
                </div>

                <div class="divider"></div>

                <div class="font-size-selector">
                    <select v-model="currentFormat" @change="changeFormat($event)" class="size-select" title="Text Size">
                        <option value="P">Normal Text</option>
                        <option value="H1">Heading 1 (ใหญ่สุด)</option>
                        <option value="H2">Heading 2 (ใหญ่)</option>
                        <option value="H3">Heading 3 (กลาง)</option>
                    </select>
                </div>

                <div class="divider"></div>

                <div class="tool-group">
                    <button @click="execCmd('bold')" title="Bold" class="icon-btn"><span class="material-symbols-outlined">format_bold</span></button>
                    <button @click="execCmd('italic')" title="Italic" class="icon-btn"><span class="material-symbols-outlined">format_italic</span></button>
                    <button @click="execCmd('underline')" title="Underline" class="icon-btn"><span class="material-symbols-outlined">format_underlined</span></button>
                    <button @click="clearFormat" title="Clear Formatting" class="icon-btn"><span class="material-symbols-outlined">format_clear</span></button>
                </div>

                <div class="divider"></div>

                <div class="tool-group">
                    <button @click="execCmd('insertUnorderedList')" title="Bullet List" class="icon-btn"><span class="material-symbols-outlined">format_list_bulleted</span></button>
                    <button @click="execCmd('insertOrderedList')" title="Numbered List" class="icon-btn"><span class="material-symbols-outlined">format_list_numbered</span></button>
                </div>

                <div class="spacer"></div> <button @click="triggerImageUpload" class="btn-image-upload">
                    <span class="material-symbols-outlined">image</span>
                    <span>Add Photo</span>
                </button>
                <input type="file" accept="image/*" ref="imageInput" class="file-input" @change="onImageUpload" />
            </div>
            <div 
                class="rich-text-area prose max-w-none text-slate-700" 
                contenteditable="true" 
                ref="contentArea"
                @input="updateContent"
                @keyup="checkFormat"
                @mouseup="checkFormat"
                @keydown="handleKeydown"
            ></div>
          </div>
        </div>

        <aside class="editor-sidebar">
          <div class="sidebar-panel">
            <h3 class="sidebar-title">
              <span class="material-symbols-outlined">format_list_bulleted</span>
              Lesson Outline
            </h3>

            <div class="section-list">
              <div 
                v-for="(section, index) in lesson.sections" 
                :key="section.id"
                class="section-item"
                :class="{ 'section-item-active': activeSectionId === section.id }"
                @click="setActiveSection(section.id)"
              >
                <span class="section-name">{{ section.title || `Section ${index + 1}` }}</span>
                <button v-if="lesson.sections.length > 1" class="remove-img-btn" @click.stop="removeSection(section.id)">
                  <span class="material-symbols-outlined">delete</span>
                </button>
              </div>
              
              <button class="add-section-btn" @click="addSection">
                <span class="material-symbols-outlined">add</span> Add Section
              </button>
            </div>
            <div class="mt-8 bg-white border border-gray-200 rounded-2xl p-6 shadow-sm">
                <div class="flex items-center justify-between mb-4">
                    <div class="flex items-center gap-3">
                    <div class="w-10 h-10 rounded-full flex items-center justify-center font-bold" :class="quiz.isEnabled ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-400'">
                        <span class="material-symbols-outlined">quiz</span>
                    </div>
                    <div>
                        <h3 class="text-lg font-bold text-gray-800">แบบทดสอบท้ายบท (Mini Quiz)</h3>
                        <p class="text-sm text-gray-500">สร้างคำถามเพื่อทดสอบความเข้าใจของนักเรียน พร้อมระบบตรวจอัตโนมัติ</p>
                    </div>
                    </div>
                    
                    <button @click="toggleQuiz" class="px-5 py-2.5 rounded-xl font-bold transition-all" :class="quiz.isEnabled ? 'bg-red-50 text-red-500 hover:bg-red-100' : 'bg-green-500 text-white hover:bg-green-600 shadow-sm'">
                    {{ quiz.isEnabled ? 'ยกเลิก / ปิดแบบทดสอบ' : '+ เปิดใช้งานควิซ' }}
                    </button>
                </div>

                <div v-if="quiz.isEnabled" class="space-y-6 mt-6 border-t border-gray-100 pt-6">
                    <input v-model="quiz.title" type="text" class="w-full text-xl font-bold border-none outline-none focus:ring-0 px-0 text-gray-800 placeholder-gray-300" placeholder="ชื่อชุดแบบทดสอบ (เช่น ทดสอบความเข้าใจ บทที่ 1)">
                    
                    <div v-for="(q, qIndex) in quiz.questions" :key="q.id" class="bg-gray-50 p-5 rounded-2xl border border-gray-200 relative group">
                    <div class="flex justify-between items-center mb-4">
                        <span class="bg-green-100 text-green-700 px-3 py-1 rounded-lg text-sm font-bold">ข้อที่ {{ qIndex + 1 }}</span>
                        <button @click="removeQuizQuestion(qIndex)" class="text-gray-400 hover:text-red-500 transition-colors">
                        <span class="material-symbols-outlined text-lg">delete</span>
                        </button>
                    </div>

                    <textarea v-model="q.text" rows="2" class="w-full border border-gray-300 rounded-xl p-3 outline-none focus:border-green-400 focus:ring-1 focus:ring-green-400 mb-4 transition-all" placeholder="พิมพ์โจทย์คำถาม..."></textarea>
                    
                    <div class="space-y-2 mb-4">
                        <div v-for="(opt, optIndex) in q.options" :key="optIndex" class="flex items-center gap-3 p-2 rounded-xl hover:bg-white border border-transparent focus-within:border-green-300 transition-colors">
                        <input type="radio" :name="'quiz_' + q.id" :value="optIndex" v-model="q.correct_answer_index" title="เลือกข้อนี้เป็นคำตอบที่ถูกต้อง" class="w-5 h-5 text-green-500 focus:ring-green-500 cursor-pointer">
                        <input v-model="q.options[optIndex]" type="text" class="flex-1 bg-transparent border-none outline-none text-gray-700 placeholder-gray-400" :placeholder="'ตัวเลือกที่ ' + (optIndex + 1)">
                        </div>
                    </div>

                    <textarea v-model="q.explanation" rows="2" class="w-full border border-green-200 bg-green-50/50 rounded-xl p-3 outline-none focus:border-green-400 text-sm" placeholder="💡 คำอธิบายเฉลย (จะแสดงให้นักเรียนเห็นหลังจากตอบคำถามแล้ว)..."></textarea>
                    </div>

                    <button @click="addQuizQuestion" class="w-full py-4 border-2 border-dashed border-green-300 text-green-600 rounded-2xl hover:bg-green-50 font-bold transition-all flex items-center justify-center gap-2">
                    <span class="material-symbols-outlined">add</span> เพิ่มข้อคำถาม
                    </button>
                </div>
            </div>

            <div class="sidebar-actions" style="margin-top: 1.5rem; padding-top: 1.5rem; border-top: 1px solid var(--card-border);">
              <button 
                class="btn btn-primary sidebar-btn" 
                :disabled="isSaving || !lesson.title.trim()" 
                @click="saveLesson"
              >
                <span class="material-symbols-outlined">{{ isEditMode ? 'save' : 'add_circle' }}</span>
                {{ isSaving ? 'Saving...' : (isEditMode ? 'Save Changes' : 'Create Lesson') }}
              </button>
            </div>
            
          </div>
        </aside>

      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import learningService from '@/services/learningService'; 

const route = useRoute();
const router = useRouter();

const authorName = ref('Wannee (Baicha)');
const isSaving = ref(false);
const isLoading = ref(true);

// ดึงค่าจาก URL Params ทั้งหมด
const courseIdParam = route.params.courseId;
const moduleIdParam = route.params.moduleId;
const pageIdParam = route.params.pageId;

const isEditMode = computed(() => {
  return !!pageIdParam; 
});

const lesson = ref({
  id: isEditMode.value ? parseInt(pageIdParam, 10) : null,
  title: '',
  module_id: parseInt(moduleIdParam, 10), 
  sections: [
    { id: Date.now(), title: '', content: '' }
  ]
});

// State สำหรับจัดการ Mini Quiz
const quiz = ref({
  isEnabled: false,
  title: 'แบบทดสอบท้ายบท (Mini Quiz)',
  questions: []
});

const activeSectionId = ref(lesson.value.sections[0].id);
const contentArea = ref(null);
const imageInput = ref(null);

const activeSection = computed(() => {
  return lesson.value.sections.find(s => s.id === activeSectionId.value);
});

// --- ระบบจัดการรูปภาพ (Base64) ---
const fileToBase64 = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
};

const triggerImageUpload = () => { imageInput.value.click(); };

const onImageUpload = async (e) => {
  const file = e.target.files[0];
  if (!file) return;
  try {
    const base64Str = await fileToBase64(file);
    execCmd('insertImage', base64Str);
  } catch (error) {
    alert("เกิดข้อผิดพลาดในการโหลดรูปภาพ");
  }
  e.target.value = '';
};

// ================= ระบบ Text Editor เพิ่มเติม =================
const currentFormat = ref('P');

const changeFormat = (event) => {
  const tag = event.target.value;
  document.execCommand('formatBlock', false, tag);
  updateContent();
  currentFormat.value = tag; 
};

const checkFormat = () => {
  if (!contentArea.value) return;
  let block = document.queryCommandValue('formatBlock');
  if (block) {
    block = block.toUpperCase();
    if (['H1', 'H2', 'H3', 'P'].includes(block)) {
      currentFormat.value = block;
    } else {
      currentFormat.value = 'P';
    }
  } else {
    currentFormat.value = 'P';
  }
};

const clearFormat = () => {
  document.execCommand('removeFormat', false, null);
  updateContent();
};

const handleKeydown = (e) => {
  if (e.key === 'Tab') {
    e.preventDefault();
    document.execCommand('insertHTML', false, '&nbsp;&nbsp;&nbsp;&nbsp;');
    updateContent();
  }
};

const execCmd = (command, value = null) => {
  // 1. บังคับให้เคอร์เซอร์กลับไปอยู่ในกล่องข้อความก่อนเสมอ
  if (contentArea.value) {
    contentArea.value.focus();
  }
  
  // 2. รันคำสั่ง จัดหน้า / ย้อนกลับ
  document.execCommand(command, false, value);
  
  // 3. อัปเดตข้อมูลเก็บลงตัวแปร
  updateContent();
};

const updateContent = () => {
  if (activeSection.value && contentArea.value) {
    activeSection.value.content = contentArea.value.innerHTML;
  }
};

// --- จัดการ Sections (เนื้อหา) ---
const setActiveSection = async (id) => {
  // เซฟเนื้อหาเดิมก่อนเปลี่ยนแท็บ
  if (activeSection.value && contentArea.value) {
    activeSection.value.content = contentArea.value.innerHTML;
  }
  
  activeSectionId.value = id;
  
  // รอให้หน้าเว็บวาดกล่องเสร็จ แล้วค่อยยัดเนื้อหาใหม่ลงไป
  await nextTick();
  if (contentArea.value && activeSection.value) {
    contentArea.value.innerHTML = activeSection.value.content || '';
  }
};

const addSection = () => {
  const newSection = { id: Date.now(), title: '', content: '' };
  lesson.value.sections.push(newSection);
  setActiveSection(newSection.id);
};

const removeSection = (id) => {
  lesson.value.sections = lesson.value.sections.filter(s => s.id !== id);
  if (activeSectionId.value === id && lesson.value.sections.length > 0) {
    setActiveSection(lesson.value.sections[0].id);
  } else if (lesson.value.sections.length === 0) {
    addSection();
  }
};

// ================= จัดการ Mini Quiz =================
const toggleQuiz = () => {
  quiz.value.isEnabled = !quiz.value.isEnabled;
  if (quiz.value.isEnabled && quiz.value.questions.length === 0) {
    addQuizQuestion();
  }
};

const addQuizQuestion = () => {
  quiz.value.questions.push({
    id: 'q_' + Date.now(),
    text: '',
    options: ['', '', '', ''], 
    correct_answer_index: 0, 
    explanation: ''
  });
};

const removeQuizQuestion = (index) => {
  if (confirm('ต้องการลบคำถามข้อนี้ใช่หรือไม่?')) {
    quiz.value.questions.splice(index, 1);
  }
};

// ================= โหลดข้อมูลบทเรียน =================
const loadLessonData = async () => {
  if (!isEditMode.value) {
    isLoading.value = false;
    return;
  }

  try {
    isLoading.value = true;
    const res = await learningService.getPageForTeacher(lesson.value.id); 
    const data = res.data;
    lesson.value.title = data.title;
    lesson.value.module_id = data.module_id;
    
    let blocks = data.content_blocks;
    if (typeof blocks === 'string') {
      blocks = JSON.parse(blocks);
    }
    
    if (blocks && blocks.length > 0) {
      const loadedSections = [];
      
      blocks.forEach((block) => {
        if (block.type === 'rich_text_section') {
          loadedSections.push({
            id: block.id || Date.now() + Math.random(),
            title: block.data?.title || '',
            content: block.data?.html || ''
          });
        } else if (block.type === 'mini_quiz') {
          quiz.value.isEnabled = true;
          quiz.value.title = block.data?.title || 'แบบทดสอบท้ายบท (Mini Quiz)';
          if (block.data?.questions) {
            quiz.value.questions = block.data.questions.map(q => ({
              ...q,
              correct_answer_index: q.correct_index !== undefined ? q.correct_index : 0
            }));
          }
        }
      });

      if (loadedSections.length > 0) {
        lesson.value.sections = loadedSections;
        activeSectionId.value = lesson.value.sections[0].id;
      }
    }
  } catch (error) {
    console.error("Load Error:", error);
    alert("ไม่สามารถโหลดเนื้อหาได้ กรุณาตรวจสอบ ID บทเรียน");
  } finally {
    isLoading.value = false;
    await nextTick();
    if (contentArea.value && activeSection.value) {
      contentArea.value.innerHTML = activeSection.value.content || '';
    }
  }
};

// ================= บันทึกข้อมูลบทเรียน =================
const saveLesson = async () => {
  if (!lesson.value.module_id || isNaN(lesson.value.module_id)) {
    alert("ไม่พบข้อมูล Module (บทเรียนหลัก)! กรุณาเข้าหน้านี้ผ่านหน้าจัดการคอร์สครับ");
    return;
  }

  updateContent();
  isSaving.value = true;
  
  try {
    const contentBlocks = lesson.value.sections.map((sec, index) => ({
      id: `sec_${index}_${Date.now()}`,
      type: "rich_text_section",
      data: { title: sec.title, html: sec.content }
    }));

    if (quiz.value.isEnabled && quiz.value.questions.length > 0) {
      const formattedQuestions = quiz.value.questions.map(q => ({
        id: q.id,
        type: 'multiple_choice',
        text: q.text,
        options: q.options,
        correct_answer: q.options[q.correct_answer_index] || q.options[0],
        correct_index: q.correct_answer_index,
        explanation: q.explanation
      }));

      contentBlocks.push({
        id: `quiz_${Date.now()}`,
        type: "mini_quiz",
        data: {
          title: quiz.value.title || 'แบบทดสอบท้ายบท',
          questions: formattedQuestions
        }
      });
    }

    const payload = {
      title: lesson.value.title || 'Untitled Lesson',
      module_id: lesson.value.module_id,
      order_index: 0,
      template_type: "standard_text", 
      is_published: true, 
      content_blocks: contentBlocks
    };
    
    if (isEditMode.value) {
      await learningService.updatePage(lesson.value.id, payload);
      alert('บันทึกการแก้ไขเรียบร้อยแล้ว! 💾');
    } else {
      await learningService.createPage(payload);
      alert('สร้างบทเรียนสำเร็จ! 🎉');
    }

    router.push(`/teacher/modules/${courseIdParam}`);

  } catch (error) {
    console.error("Save Error:", error);
    alert('เกิดข้อผิดพลาดในการบันทึกข้อมูล');
  } finally {
    isSaving.value = false;
  }
};

onMounted(() => {
  loadLessonData();
  document.execCommand('defaultParagraphSeparator', false, 'p');
});
</script>

<style scoped>
/* 🎨 Layout & Main Containers */
.editor-page { max-width: 1200px; margin: 0 auto; padding: 1.5rem 1.5rem 5rem; background-color: #f8fafc; min-height: 100vh; }
.editor-layout { display: flex; gap: 2rem; align-items: flex-start; }
.editor-main { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 1.5rem; }

/* 🍞 Breadcrumb Navigation */
.breadcrumb-bar { display: flex; align-items: center; gap: 4px; font-size: 0.85rem; color: #64748b; margin-bottom: 1.5rem; }
.breadcrumb-link:hover { color: #e91e63; text-decoration: underline; }
.breadcrumb-current { font-weight: 600; color: #e91e63; }
.breadcrumb-sep { font-size: 16px; opacity: 0.5; }

/* 🛠 Toolbar Styling (อัปเกรดให้เลื่อนตามหน้าจอ) */
.editor-toolbar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px;
  padding: 10px;
  background: rgba(241, 245, 249, 0.95); /* ทำให้พื้นหลังกึ่งโปร่งใส */
  backdrop-filter: blur(8px); /* เบลอพื้นหลังที่ถูกทับให้ดูพรีเมียม */
  border-radius: 8px;
  margin-bottom: 15px;
  border: 1px solid #e2e8f0;
  
  /* 🚨 โค้ดพระเอก: สั่งให้แถบเครื่องมือลอยตามหน้าจอ (Sticky) */
  position: sticky;
  top: 80px; /* กะระยะไม่ให้ชนกับแถบ Navbar หลักของเว็บ (ปรับตัวเลขได้ถ้ามันทับกัน) */
  z-index: 40; /* ให้อยู่เหนือตัวหนังสือเสมอ */
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05); /* ใส่เงาบางๆ เวลาลอยทับเนื้อหาจะได้ดูมีมิติ */
}

/* 🔠 Font Size Selector */
.size-select { height: 34px; padding: 0 8px; border: 1px solid #cbd5e1; border-radius: 6px; background: white; font-weight: 500; color: #334155; cursor: pointer; outline: none; }
.size-select:hover { border-color: #e91e63; }

/* 📸 Special Button: Add Photo */
.btn-image-upload { display: flex; align-items: center; gap: 6px; padding: 6px 12px !important; background: rgba(233, 30, 99, 0.1) !important; color: #e91e63 !important; font-weight: 600 !important; border: 1px solid rgba(233, 30, 99, 0.2) !important; }

/* 🚨 บังคับขนาดและรูปแบบใน Editor */
.rich-text-area { min-height: 350px; outline: none; padding: 10px 5px; }

/* บังคับระยะห่างบรรทัด */
.rich-text-area :deep(*) { line-height: 1.7 !important; }

/* ทำลายสไตล์แปลกปลอม */
.rich-text-area :deep(span), .rich-text-area :deep(font) { font-size: inherit !important; font-family: inherit !important; line-height: inherit !important; }

/* กำหนดขนาด Heading */
.rich-text-area :deep(h1) { font-size: 2.2rem !important; font-weight: 800; margin: 15px 0 10px 0; color: #0f172a; }
.rich-text-area :deep(h2) { font-size: 1.7rem !important; font-weight: 700; margin: 15px 0 10px 0; color: #1e293b; }
.rich-text-area :deep(h3) { font-size: 1.3rem !important; font-weight: 600; margin: 10px 0; color: #334155; }
.rich-text-area :deep(p) { font-size: 1rem !important; margin: 8px 0; }

/* 🚨 🌟 การเพิ่มรูปแล้วรูปไม่ล้น ✨ */
/* ย้ายกฎรูปภาพมาอยู่ในกลุ่ม deep ของพื้นที่เนื้อหาหลักเพื่อความแน่นอน */
.rich-text-area :deep(img) {
  max-width: 100% !important; /* กว้างสุดไม่เกินภาชนะบรรจุ */
  height: auto !important;     /* รักษาสัดส่วนภาพอัตโนมัติ */
  border-radius: 8px;
  margin: 1.5em 0;           /* เพิ่มระยะขอบให้สวยงาม */
  display: block;             /* ช่วยให้ margin ทำงานได้ดีที่สุด */
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06); /* เพิ่มเงานิดหน่อยให้ดูมีมิติ */
}

/* 🗂 Sidebar & Section List */
.editor-sidebar { width: 300px; flex-shrink: 0; position: sticky; top: 1.5rem; }
.sidebar-panel { background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.5rem; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); }
.section-item { padding: 12px; background-color: #f8fafc; border-radius: 8px; margin-bottom: 8px; cursor: pointer; display: flex; justify-content: space-between; align-items: center; border: 1px solid transparent; transition: all 0.2s; }
.section-item:hover { background-color: #f1f5f9; transform: translateX(4px); }
.section-item-active { background-color: #fdf2f8; color: #e91e63; border-color: #f472b6; font-weight: 600; }

/* 🔘 Common Components */
.panel { background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.5rem; }
.btn-primary { width: 100%; background: #e91e63; color: white; border: none; padding: 14px; border-radius: 10px; font-weight: 700; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px; transition: all 0.2s; }
.btn-primary:hover:not(:disabled) { background: #d81b60; transform: translateY(-1px); box-shadow: 0 4px 12px rgba(233, 30, 99, 0.2); }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }

/* 🌀 Loading Spinner */
.state-box { display: flex; flex-direction: column; align-items: center; gap: 1rem; padding: 5rem; color: #64748b; }
.spinner { width: 40px; height: 40px; border: 4px solid #f1f5f9; border-top-color: #e91e63; border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* 📱 Responsive */
@media (max-width: 1024px) { .editor-layout { flex-direction: column; } .editor-sidebar { width: 100%; position: static; } }
</style>