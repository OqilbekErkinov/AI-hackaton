<template>
  <div class="cv-generator-container p-3 p-md-5">
    <div class="container-fluid max-w-1200">

      <!-- SARLAVHA -->
      <div class="header-section mb-5 text-center" v-show="!isGenerating && !generatedCv">
        <h1 class="display-4 fw-bold gradient-text mb-3">AI CV Generator</h1>
        <p class="lead text-muted">Profilingiz, yutuqlaringiz va tajribangiz asosida professional rezyume tayyorlang.</p>
        <div class="header-badges d-flex justify-content-center gap-3 mt-4">
          <span class="badge bg-primary-soft text-primary px-3 py-2"><i class="bi bi-lightning-fill me-1"></i> Tezkor</span>
          <span class="badge bg-success-soft text-success px-3 py-2"><i class="bi bi-shield-check me-1"></i> Professional</span>
          <span class="badge bg-purple-soft text-purple px-3 py-2"><i class="bi bi-robot me-1"></i> AI-Powered</span>
        </div>
      </div>

      <div class="row g-4 justify-content-center">

        <!-- CV YO'Q BO'LSA: BOSHLASH KARTASI -->
        <div class="col-lg-10" v-if="!generatedCv">
          <div class="card border-0 shadow-lg main-card glass-morph overflow-hidden">
            <div class="card-body p-4 p-md-5 text-center">
              <div class="illustration-box mb-4">
                <div class="pulse-ring"></div>
                <i class="bi bi-file-earmark-person ai-icon"></i>
              </div>
              <h3 class="fw-bold mb-3">Tayyormisiz?</h3>
              <p class="text-muted mb-4 px-md-5">
                Sun'iy intellekt tizimimiz barcha yutuqlaringizni, XP ballaringizni va akademik
                ko'rsatkichlaringizni tahlil qilib, eng munosib CV variantini tayyorlab beradi.
              </p>
              <button
                @click="generateCv"
                class="btn btn-custom btn-lg px-5 py-3 rounded-pill shadow-glow"
                :disabled="isGenerating"
              >
                <span v-if="!isGenerating"><i class="bi bi-magic me-2"></i> REZYUME YARATISH</span>
                <span v-else>
                  <div class="spinner-border spinner-border-sm me-2" role="status"></div>
                  AI tahlil qilmoqda...
                </span>
              </button>

              <!-- PROGRESS BAR -->
              <div v-if="isGenerating" class="mt-5">
                <div class="d-flex justify-content-between mb-2">
                  <span class="small fw-medium text-primary">{{ currentStepText }}</span>
                  <span class="small text-muted">{{ progress }}%</span>
                </div>
                <div class="progress rounded-pill" style="height: 6px;">
                  <div class="progress-bar progress-bar-striped progress-bar-animated" :style="{ width: progress + '%' }"></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- CV TAYYOR BO'LSA: NATIJA -->
        <div class="col-lg-12" v-if="generatedCv" id="cv-result-area">
          <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-3">
            <h4 class="fw-bold m-0">
              <i class="bi bi-check-circle-fill text-success me-2"></i> Rezyumeingiz tayyor!
            </h4>
            <div class="d-flex gap-2">
              <button @click="copyToClipboard" class="btn btn-custom rounded-pill px-4 shadow-sm fw-bold">
                <i class="bi bi-clipboard me-1"></i> Nusxalash
              </button>
              <button @click="downloadPdf" class="btn btn-custom rounded-pill px-4 shadow-sm fw-bold" :disabled="isDownloading">
                <i class="bi bi-download me-1"></i> PDF YUKLASH
              </button>
              <button @click="generatedCv = null" class="btn btn-light rounded-pill px-3">
                <i class="bi bi-arrow-repeat"></i>
              </button>
            </div>
          </div>

          <div class="card border-0 shadow-lg cv-preview-card" id="cv-capture-area">
            <div class="cv-verified-stamp">
              <div class="stamp-inner">
                <i class="bi bi-shield-fill-check"></i>
                <span>VERIFIED</span>
              </div>
            </div>

            <div class="card-body p-0">
              <div class="cv-render-wrapper" v-html="generatedCv"></div>
            </div>

            <div class="cv-footer-official px-5 py-3 border-top bg-light">
              <div class="d-flex align-items-center justify-content-between small text-muted">
                <div>
                  <i class="bi bi-patch-check-fill text-primary me-1"></i>
                  Ushbu rezyume platforma tomonidan rasmiy tasdiqlangan ma'lumotlar asosida shakllantirildi.
                </div>
                <div class="fw-bold">ID: RE-{{ cvId }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- TOAST XABAR -->
    <div v-if="notification" class="toast-container position-fixed bottom-0 end-0 p-3">
      <div class="toast show text-white bg-dark border-0">
        <div class="d-flex">
          <div class="toast-body">{{ notification }}</div>
          <button class="btn-close btn-close-white me-2 m-auto" @click="notification = null"></button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { jsPDF } from 'jspdf';

const api = useApi();

// html2canvas — CDN orqali yuklanadi
let html2canvas;
if (typeof window !== 'undefined') {
  const s = document.createElement('script');
  s.src = 'https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js';
  s.onload = () => { html2canvas = window.html2canvas; };
  document.head.appendChild(s);
}

const isGenerating = ref(false);
const generatedCv = ref(null);
const progress = ref(0);
const currentStepText = ref('');
const notification = ref(null);
const isDownloading = ref(false);
const cvId = ref(Math.random().toString(36).substr(2, 9).toUpperCase());

const steps = [
  "Profil ma'lumotlari yuklanmoqda...",
  "Yutuqlar tahlil qilinmoqda...",
  "AI rezyume strukturasini tuzmoqda...",
  "Matn generatsiya qilinmoqda...",
  "Yakuniy formatlash bajarilmoqda..."
];

const showNotification = (msg) => {
  notification.value = msg;
  setTimeout(() => { notification.value = null; }, 3000);
};

const generateCv = async () => {
  isGenerating.value = true;
  progress.value = 0;

  // Progress animatsiyasi
  for (let i = 0; i < steps.length; i++) {
    currentStepText.value = steps[i];
    const duration = 1000 + Math.random() * 1500;
    const target = ((i + 1) / steps.length) * 80;
    const start = progress.value;
    const inc = (target - start) / 20;
    for (let j = 0; j < 20; j++) {
      progress.value = Math.round(start + inc * j);
      await new Promise(r => setTimeout(r, duration / 20));
    }
  }

  try {
    const res = await api.post('/ai/generate-cv/');
    let content = res.data.content || '';
    content = content.replace(/```html/g, '').replace(/```/g, '').trim();
    generatedCv.value = content;
    progress.value = 100;
    currentStepText.value = 'Tayyor!';
    showNotification('Rezyume muvaffaqiyatli yaratildi!');
  } catch (e) {
    console.error(e);
    showNotification("Xatolik yuz berdi. Qaytadan urinib ko'ring.");
  } finally {
    isGenerating.value = false;
  }
};

const copyToClipboard = () => {
  navigator.clipboard.writeText(generatedCv.value);
  showNotification('Nusxa olindi!');
};

const downloadPdf = async () => {
  if (!html2canvas) return showNotification('Kutubxona yuklanmoqda...');
  isDownloading.value = true;
  try {
    const el = document.getElementById('cv-capture-area');
    const canvas = await html2canvas(el, { scale: 1.5, useCORS: true, backgroundColor: '#fff' });
    const imgData = canvas.toDataURL('image/jpeg', 0.85);
    const pdf = new jsPDF({ orientation: 'p', unit: 'mm', format: 'a4', compress: true });
    pdf.addImage(imgData, 'JPEG', 0, 0, pdf.internal.pageSize.getWidth(), pdf.internal.pageSize.getHeight());
    pdf.save(`CV_${Date.now()}.pdf`);
    showNotification('PDF yuklandi!');
  } catch (e) {
    showNotification("PDF yaratishda xatolik.");
  } finally {
    isDownloading.value = false;
  }
};
</script>

<style scoped>
.cv-generator-container {
  background-color: var(--bg-app);
  min-height: 100vh;
}

.gradient-text {
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.bg-primary-soft { background-color: rgba(17, 45, 78, 0.1); }
.bg-success-soft { background-color: rgba(16, 106, 43, 0.1); }
.bg-purple-soft { background-color: rgba(139, 92, 246, 0.1); }
.text-purple { color: #8b5cf6; }

.glass-morph {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.4) !important;
}

.illustration-box {
  position: relative;
  width: 120px;
  height: 120px;
  margin: 0 auto;
}

.ai-icon {
  font-size: 64px;
  color: var(--primary);
  position: relative;
  z-index: 2;
}

.pulse-ring {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 100px;
  height: 100px;
  background: var(--primary);
  border-radius: 50%;
  opacity: 0.15;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { transform: translate(-50%, -50%) scale(0.95); opacity: 0.2; }
  70% { transform: translate(-50%, -50%) scale(1.2); opacity: 0; }
  100% { transform: translate(-50%, -50%) scale(0.95); opacity: 0; }
}

.btn-custom {
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
  color: white;
  border: none;
  transition: all 0.3s ease;
}

.btn-custom:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(var(--primary-rgb), 0.3);
  color: white;
}

.shadow-glow {
  box-shadow: 0 8px 16px rgba(var(--primary-rgb), 0.2);
}

.cv-preview-card {
  position: relative;
  background: white;
  min-height: 1000px;
}

.cv-verified-stamp {
  position: absolute;
  top: 40px;
  right: 40px;
  transform: rotate(15deg);
  z-index: 10;
  pointer-events: none;
}

.stamp-inner {
  border: 3px solid #106a2b;
  color: #106a2b;
  padding: 5px 15px;
  border-radius: 8px;
  font-weight: 800;
  letter-spacing: 2px;
  font-size: 14px;
  background: rgba(16, 106, 43, 0.05);
}

/* ================= CV TEMPLATE STYLES ================= */
.cv-render-wrapper :deep(.cv-layout) {
  display: flex;
  min-height: 1000px;
  font-family: 'Inter', sans-serif;
  color: #334155;
  line-height: 1.5;
}

.cv-render-wrapper :deep(.cv-sidebar) {
  width: 280px;
  background: #1e293b;
  color: white;
  padding: 40px 30px;
}

.cv-render-wrapper :deep(.cv-main) {
  flex: 1;
  padding: 60px 50px;
  background: white;
}

.cv-render-wrapper :deep(.cv-photo-container) {
  margin-bottom: 30px;
  text-align: center;
}

.cv-render-wrapper :deep(.cv-photo-container img) {
  width: 140px;
  height: 140px;
  border-radius: 20px;
  object-fit: cover;
  border: 4px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
}

.cv-render-wrapper :deep(.cv-sidebar-section) {
  margin-bottom: 35px;
}

.cv-render-wrapper :deep(.cv-sidebar-section h3) {
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 1.5px;
  color: #94a3b8;
  margin-bottom: 15px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.2);
  padding-bottom: 8px;
}

.cv-render-wrapper :deep(.cv-main h1) {
  font-size: 38px;
  font-weight: 800;
  color: #0f172a;
  margin-bottom: 10px;
}

.cv-render-wrapper :deep(.cv-main .cv-title) {
  font-size: 18px;
  color: #3b82f6;
  font-weight: 600;
  margin-bottom: 30px;
}

.cv-render-wrapper :deep(.cv-content-section) {
  margin-bottom: 40px;
}

.cv-render-wrapper :deep(.cv-content-section h2) {
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.cv-render-wrapper :deep(.cv-content-section h2::after) {
  content: '';
  flex: 1;
  height: 1px;
  background: #e2e8f0;
}

.cv-render-wrapper :deep(ul) {
  padding-left: 20px;
  margin-bottom: 0;
}

.cv-render-wrapper :deep(li) {
  margin-bottom: 8px;
}

.cv-footer-official {
  border-bottom-left-radius: var(--radius-lg);
  border-bottom-right-radius: var(--radius-lg);
}
</style>
