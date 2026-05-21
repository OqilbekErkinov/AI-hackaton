<template>
  <div class="p-3 scholarship-detail">
    <!-- BACK -->
    <button class="back-btn mb-4" @click="$router.push('/scholarship')">
      ← Orqaga
    </button>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status" />
      <p class="mt-2">Yuklanmoqda...</p>
    </div>

    <div v-else-if="scholarship" class="row g-4">
      <!-- LEFT SIDE: INFO -->
      <div class="col-lg-8">
        <div class="card detail-card border-0 shadow-sm mb-4">
          <h1 class="detail-title">
            {{ scholarship.title }}
          </h1>

          <div class="meta mb-3">
            <span class="badge amount-badge me-3"> 💰 {{ scholarship.amount }} </span>
            <span class="badge deadline-badge me-3">
              ⏰ {{ formatDate(scholarship.deadline) }}
            </span>
            <span class="badge org-badge me-3"> 🏫 {{ scholarship.organization }} </span>
          </div>

          <div class="description-box mb-4">
            <h5 class="fw-bold">Tavsif</h5>
            <p class="description">
              {{ scholarship.description }}
            </p>
          </div>

          <h5 class="fw-bold mb-3">Stipendiya talablari</h5>
          <ul class="requirements-list">
            <li v-for="(req, i) in scholarship.requirements" :key="i">
              <i class="bi bi-check2-circle me-2 text-primary"></i>
              {{ req.text }}
            </li>
          </ul>
        </div>
      </div>

      <!-- RIGHT SIDE: APPLY -->
      <div class="col-lg-4">
        <!-- STATUS BANNER IF APPLIED -->
        <div v-if="eligibility.already_applied" class="card status-card border-0 shadow-sm p-4 mb-4 text-center">
          <div class="status-icon" :class="eligibility.application_status">
            <i v-if="eligibility.application_status === 'approved'" class="bi bi-check-circle-fill" />
            <i v-else-if="eligibility.application_status === 'rejected'" class="bi bi-x-circle-fill" />
            <i v-else class="bi bi-clock-fill" />
          </div>
          <h4 class="mt-3 capitalize">{{ statusLabel(eligibility.application_status) }}</h4>
          <p class="small text-muted mb-0">
            Siz ushbu stipendiyaga ariza topshirgansiz. Ariza holati: <b>{{ statusLabel(eligibility.application_status) }}</b>
          </p>
          <div v-if="eligibility.admin_note" class="alert alert-info small mt-3 text-start">
            <div class="fw-bold mb-1">Admin izohi:</div>
            {{ eligibility.admin_note }}
          </div>
        </div>

        <!-- APPLY FORM -->
        <div v-else class="card apply-card border-0 shadow-sm p-4">
          <div class="d-flex justify-content-between align-items-center mb-3">
             <h4 class="mb-0">Ariza topshirish</h4>
             <span v-if="eligibility.eligible" class="badge bg-light text-dark">Qadam {{ currentStep }}/2</span>
          </div>

          <!-- STEP 1: ELIGIBILITY ERRORS OR SELECTION -->
          <div v-if="!eligibility.eligible && eligibility.errors.length > 0" class="alert alert-warning small mb-4">
            <div class="fw-bold mb-1">Afsuski, siz talablarga mos kelmaysiz:</div>
            <ul class="mb-0 ps-3">
              <li v-for="(err, i) in eligibility.errors" :key="i">{{ err }}</li>
            </ul>
          </div>

          <div v-if="eligibility.eligible">
            
            <!-- STEP 1: SELECT DOCUMENTS -->
            <div v-if="currentStep === 1">
              <p class="small text-muted mb-3">
                Ushbu stipendiya talablariga muvofiq, portfoliongizdan kerakli hujjatlarni tanlang:
              </p>

              <div v-for="rule in scholarship.requirements" :key="rule.id" class="mb-4">
                <!-- Eslatma: Backenddan ScholarshipRequirement kelayapti, 
                     Lekin biz ScholarshipRule turlarini bilishimiz kerak. 
                     Hozircha barcha hujjatlarni bir joyda ko'rsatamiz 
                     yoki ScholarshipRule modelini ham fetch qilamiz. 
                -->
              </div>

              <!-- SODDALASHTRISH: Barcha yuklangan hujjatlardan stipendiya uchun moslarini tanlash -->
              <div class="rule-selection mb-4">
                 <label class="form-label small fw-bold">Hujjatlarni biriktirish</label>
                 <div class="doc-grid">
                    <div 
                      v-for="doc in userDocuments" 
                      :key="doc.id" 
                      class="doc-item-mini"
                      :class="{ selected: selectedDocIds.includes(doc.id) }"
                      @click="toggleDocSelection(doc.id)"
                    >
                       <div class="doc-icon">📄</div>
                       <div class="doc-info">
                          <div class="doc-name text-truncate">{{ doc.doc_type_display }}</div>
                          <div class="doc-date">{{ formatDate(doc.created_at) }}</div>
                       </div>
                       <div class="doc-check">
                          <i v-if="selectedDocIds.includes(doc.id)" class="bi bi-check-circle-fill text-success" />
                          <i v-else class="bi bi-circle" />
                       </div>
                    </div>
                 </div>
                 <div v-if="userDocuments.length === 0" class="text-danger small mt-2">
                    Hujjatlar topilmadi. Avval Profil bo'limiga yuklang.
                 </div>
              </div>

              <div class="mt-4">
                <button class="btn btn-primary w-100 py-2" :disabled="userDocuments.length === 0" @click="currentStep = 2">
                  Keyingi qadam →
                </button>
              </div>
            </div>

            <!-- STEP 2: MOTIVATION -->
            <div v-if="currentStep === 2">
              <p class="small text-muted mb-3">
                Yakuniy qadam: Motivatsiya xatingizni yozing.
              </p>

              <div class="mb-3">
                <label class="form-label small">Motivatsiya xati</label>
                <textarea 
                  v-model="motivation" 
                  class="form-control" 
                  rows="5" 
                  placeholder="Nima uchun aynan siz ushbu stipendiyaga munosibsiz?" 
                />
              </div>

              <div class="selected-docs-summary mb-3 p-2 bg-light rounded small">
                 <b>Tanlangan hujjatlar:</b> {{ selectedDocIds.length }} ta
              </div>

              <div class="d-flex gap-2">
                <button class="btn btn-light" @click="currentStep = 1">Ortga</button>
                <button 
                  class="btn btn-primary flex-grow-1 py-2 d-flex align-items-center justify-content-center gap-2" 
                  :disabled="submitting || !motivation.trim()" 
                  @click="applyScholarship"
                >
                  <span v-if="submitting" class="spinner-border spinner-border-sm" />
                  <span>Arizani jo'natish</span>
                </button>
              </div>
            </div>
          </div>
          
          <div v-else class="text-center py-3">
             <i class="bi bi-info-circle text-muted fs-2" />
             <p class="small text-muted mt-2">
               Talablarga javob bermaganingiz sababli ariza topshira olmaysiz.
             </p>
             <NuxtLink to="/profile" class="btn btn-sm btn-outline-primary mt-2">
               Profilni to'ldirish
             </NuxtLink>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from "vue";
import { useRoute, useRouter } from "vue-router";
import useApi from "@/composables/useApi";

const route = useRoute();
const router = useRouter();
const api = useApi();

const scholarship = ref(null);
const loading = ref(true);
const submitting = ref(false);
const motivation = ref("");

const eligibility = reactive({
  eligible: false,
  errors: [],
  already_applied: false,
  application_status: null,
  admin_note: null,
});

const currentStep = ref(1);
const userDocuments = ref([]);
const selectedDocIds = ref([]);

const formatDate = (dateStr) => {
  if (!dateStr) return "";
  return new Date(dateStr).toLocaleDateString("uz-UZ", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
};

const statusLabel = (st) => {
  const map = {
    pending: "Kutilmoqda",
    approved: "Tasdiqlandi",
    rejected: "Rad etildi",
  };
  return map[st] || st;
};

const isDocRule = (type) => {
  return [
    "min_articles", "min_thesis", "min_publications", 
    "min_conferences", "require_language", "require_ict", "require_history"
  ].includes(type);
};

const ruleLabel = (type) => {
  const map = {
    min_articles: "maqolalar",
    min_thesis: "tezislar",
    min_publications: "nashr ishlari",
    min_conferences: "konferensiyalar",
    require_language: "til sertifikatlari",
    require_ict: "IT sertifikati",
    require_history: "tarix natijasi",
  };
  return map[type] || type;
};

const getMatchingDocs = (ruleType) => {
  const typeMap = {
    min_articles: "article",
    min_thesis: "thesis",
    min_publications: "publication",
    min_conferences: "conference",
    require_language: "language_cert",
    require_ict: "ict_cert",
    require_history: "history_cert",
  };
  const targetType = typeMap[ruleType];
  return userDocuments.value.filter(d => d.doc_type === targetType);
};

const toggleDocSelection = (id) => {
  const idx = selectedDocIds.value.indexOf(id);
  if (idx > -1) selectedDocIds.value.splice(idx, 1);
  else selectedDocIds.value.push(id);
};

const fetchScholarship = async () => {
  const id = route.params.id;
  try {
    const res = await api.get(`/scholarships/${id}/`);
    scholarship.value = res.data;
  } catch (err) {
    console.error("fetchScholarship error", err);
  }
};

const checkEligibility = async () => {
  const id = route.params.id;
  try {
    const res = await api.get(`/scholarships/${id}/check/`);
    Object.assign(eligibility, res.data);
  } catch (err) {
    console.error("checkEligibility error", err);
  }
};

const fetchUserDocuments = async () => {
  try {
    const res = await api.get("/documents/");
    userDocuments.value = res.data;
  } catch (err) {
    console.error("fetchUserDocuments error", err);
  }
};

const applyScholarship = async () => {
  if (!motivation.value.trim()) return;
  const id = route.params.id;
  submitting.value = true;
  try {
    await api.post(`/scholarships/${id}/apply/`, {
      motivation_letter: motivation.value,
      attached_documents: selectedDocIds.value,
    });
    alert("Ariza muvaffaqiyatli yuborildi!");
    await checkEligibility(); // Refresh status
  } catch (err) {
    console.error("applyScholarship error", err);
    const msg = err.response?.data?.error || err.response?.data?.detail || "Xatolik yuz berdi.";
    alert(msg);
  } finally {
    submitting.value = false;
  }
};

onMounted(async () => {
  loading.value = true;
  await Promise.all([
    fetchScholarship(), 
    checkEligibility(),
    fetchUserDocuments()
  ]);
  loading.value = false;
});
</script>


