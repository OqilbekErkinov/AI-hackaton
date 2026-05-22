<template>
    <div>
        <div class="row align-items-center mb-4 mt-3">
            <div class="col-md-7">
                <h2 class="premium-dashboard-title">Mening Portfolio Dashboardim</h2>
                <p class="text-muted small">Akademik yutuqlaringiz va portfolioingizni ushbu yerdan boshqaring.</p>
            </div>
            <div class="col-md-5 d-flex justify-content-md-end gap-3 mt-3 mt-md-0">
                <div class="glass-stats-pill">
                    <span class="pill-label">Hujjatlar</span>
                    <span class="pill-value">{{ documents.length }}</span>
                </div>
                <button class="btn btn-premium-add shadow-lg" @click="openAddAchievement">
                    <i class="bi bi-file-earmark-plus-fill me-2"></i> Yangi hujjat qo'shish
                </button>
            </div>
        </div>

        <div class="row g-4">
            <!-- MAIN CONTENT: Full Width Dashboard -->
            <div class="col-12">
                <div class="main-portfolio">
                    <div v-for="cat in categories" :key="cat.key" class="achievement-section mb-5">
                        <div v-if="getDocsByCategory(cat.key).length > 0">
                            <div class="section-header-wrap mb-4">
                                <div class="d-flex align-items-center gap-3">
                                    <div class="cat-badge-icon" :class="cat.key">
                                        <i :class="getCatIcon(cat.key)"></i>
                                    </div>
                                    <h5 class="section-cat-title">
                                        {{ cat.label }}
                                        <span class="count-bubble">{{ getDocsByCategory(cat.key).length }}</span>
                                    </h5>
                                </div>
                            </div>
                            
                            <div class="row g-4">
                                <div v-for="doc in getDocsByCategory(cat.key)" :key="doc.id" class="col-12 col-md-6 col-xl-4">
                                    <div class="glass-card growth-card h-100">
                                        <div class="card-glow"></div>
                                        <div class="card-content">
                                            <div class="d-flex justify-content-between align-items-start mb-3">
                                                <div class="status-badge" :class="doc.status || 'pending'">
                                                    <span v-if="doc.status === 'approved'">Tasdiqlangan</span>
                                                    <span v-else-if="doc.status === 'rejected'">Rad etildi</span>
                                                    <span v-else>Kutilmoqda</span>
                                                </div>
                                                <button @click="deleteAchievement(doc.id)" class="btn-delete-card">
                                                    <i class="bi bi-trash"></i>
                                                </button>
                                            </div>

                                            <h6 class="doc-name-main" :title="doc.meta?.title">
                                                {{ doc.meta?.title || cat.label }}
                                            </h6>
                                            
                                            <div class="doc-meta-grid">
                                                <div v-if="doc.meta?.journal" class="meta-tag">
                                                    <i class="bi bi-journal-check"></i>
                                                    {{ doc.meta.journal }}
                                                </div>
                                                <div v-if="doc.meta?.level" class="meta-tag gold">
                                                    <i class="bi bi-award"></i>
                                                    {{ doc.meta.level }} ({{ doc.meta.score || '' }})
                                                </div>
                                                <div v-if="doc.doc_type === 'transcript' && doc.meta?.score" class="meta-tag gold">
                                                    <i class="bi bi-mortarboard-fill"></i>
                                                    GPA: {{ doc.meta.score }}
                                                </div>
                                            </div>

                                            <div class="footer-actions mt-4 pt-3 border-top d-flex justify-content-between align-items-center">
                                                <span class="created-date">{{ formatDate(doc.created_at) }}</span>
                                                <a :href="doc.file_url" target="_blank" class="view-link">
                                                    Ko'rish <i class="bi bi-arrow-right-short"></i>
                                                </a>
                                            </div>
                                            
                                            <div v-if="doc.status === 'rejected' && doc.admin_note" class="admin-feedback mt-3">
                                                <i class="bi bi-exclamation-triangle-fill"></i>
                                                {{ doc.admin_note }}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div v-if="documents.length === 0" class="empty-dashboard-state mt-5">
                        <div class="empty-dashboard-visual">
                            <i class="bi bi-grid-3x3-gap"></i>
                        </div>
                        <h5>Yutuqlar hali yo'q</h5>
                        <p>O'zingizning akademik o'sishingizni ko'rsatish uchun hujjatlarni yuklang!</p>
                        <button class="btn btn-premium-add shadow px-5 mt-3" @click="step = 1; bsAchievementModal.show()">
                            <i class="bi bi-rocket-takeoff-fill me-2"></i> Yuklashni boshlash
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Achievement Modal -->
        <Teleport to="body">
        <div class="modal fade" id="achievementModal" tabindex="-1" aria-hidden="true" ref="achievementModalRef">
            <div class="modal-dialog modal-dialog-centered modal-dialog-scrollable">
                <div class="modal-content">
                    <div class="modal-header border-0 pb-0">
                        <h5 class="modal-title">
                            {{ achForm.editing ? "Yutuqni tahrirlash" : "Yutuq qo'shish" }}
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Yopish"></button>
                    </div>

                    <div class="modal-body py-4">

                        <div v-if="step === 1">
                            <div class="mb-4 text-center">
                                <h5 class="fw-bold text-main">Hujjat turini tanlang</h5>
                                <p class="text-muted small">Davom etish uchun quyidagilardan birini tanlang</p>
                            </div>
                            <div class="category-grid">
                                <div v-for="c in categories" :key="c.key" 
                                     class="cat-card-btn" 
                                     :class="{ active: achForm.category === c.key }"
                                     @click="selectCategory(c.key)">
                                    <div class="cat-icon-wrap">
                                        <i :class="getCatIcon(c.key)"></i>
                                    </div>
                                    <span class="cat-label">{{ c.label }}</span>
                                </div>
                            </div>
                        </div>

                        <div v-if="step === 2" class="step-content px-2">
                            <div class="mb-4 text-center">
                                <h5 class="fw-bold text-main">Hujjat tafsilotlari</h5>
                                <div class="badge bg-light text-primary px-3 py-2 rounded-pill">
                                    {{ categories.find(c => c.key === achForm.category)?.label }}
                                </div>
                            </div>

                            <!-- GPA only for transcript -->
                            <div v-if="achForm.category === 'transcript'" class="mb-4">
                                <label class="form-label premium-label">GPA Ko'rsatkichi (O'rtacha baho)</label>
                                <div class="custom-form-select">
                                    <div class="custom-form-trigger" @click="toggleFormDropdown('transcript')">
                                        <span>{{ achForm.score ? 'GPA: ' + achForm.score : 'GPA qiymatini tanlang' }}</span>
                                        <span class="arrow">▾</span>
                                    </div>
                                    <div v-if="openFormDropdown === 'transcript'" class="custom-form-menu">
                                        <div v-for="g in ['5.0', '4.9', '4.8', '4.7', '4.6', '4.5', '4.4', '4.3', '4.2', '4.1', '4.0', '3.9', '3.8', '3.7', '3.6', '3.5']" 
                                             :key="g" 
                                             class="custom-form-option"
                                             :class="{ selected: achForm.score === g }"
                                             @click="selectFormOption('score', g)">
                                            GPA: {{ g }} ({{ g == '5.0' ? '10' : g == '4.9' ? '9.7' : g == '4.8' ? '9.3' : g == '4.7' ? '9' : g == '4.6' ? '8.7' : g == '4.5' ? '8.3' : g == '4.4' ? '8' : g == '4.3' ? '7.7' : g == '4.2' ? '7.3' : g == '4.1' ? '7' : g == '4.0' ? '6.7' : g == '3.9' ? '6.3' : g == '3.8' ? '6' : g == '3.7' ? '5.7' : g == '3.6' ? '5.3' : '5' }} ball)
                                        </div>
                                    </div>
                                </div>
                                <div class="form-text small text-muted mt-1">Eslatma: GPA 3.5 dan past bo'lganda ball berilmaydi.</div>
                            </div>

                            <!-- Language Certificate Level Selection -->
                            <div v-if="achForm.category === 'language_cert'" class="mb-4">
                                <label class="form-label premium-label">Til bilish darajasi (IELTS / CEFR)</label>
                                <div class="custom-form-select">
                                    <div class="custom-form-trigger" @click="toggleFormDropdown('language_cert')">
                                        <span>
                                            {{ 
                                                achForm.level === 'c2' ? 'IELTS 8.0 - 9.0 / CEFR C2 (20 ball)' :
                                                achForm.level === 'c1' ? 'IELTS 7.0 - 7.5 / CEFR C1 (18 ball)' :
                                                achForm.level === 'b2' ? 'IELTS 6.0 - 6.5 / CEFR B2 (15 ball)' :
                                                achForm.level === 'b1' ? 'IELTS 5.0 - 5.5 / CEFR B1 (10 ball)' :
                                                'Darajani tanlang'
                                            }}
                                        </span>
                                        <span class="arrow">▾</span>
                                    </div>
                                    <div v-if="openFormDropdown === 'language_cert'" class="custom-form-menu">
                                        <div class="custom-form-option" :class="{ selected: achForm.level === 'c2' }" @click="selectFormOption('level', 'c2')">IELTS 8.0 - 9.0 / CEFR C2 (20 ball)</div>
                                        <div class="custom-form-option" :class="{ selected: achForm.level === 'c1' }" @click="selectFormOption('level', 'c1')">IELTS 7.0 - 7.5 / CEFR C1 (18 ball)</div>
                                        <div class="custom-form-option" :class="{ selected: achForm.level === 'b2' }" @click="selectFormOption('level', 'b2')">IELTS 6.0 - 6.5 / CEFR B2 (15 ball)</div>
                                        <div class="custom-form-option" :class="{ selected: achForm.level === 'b1' }" @click="selectFormOption('level', 'b1')">IELTS 5.0 - 5.5 / CEFR B1 (10 ball)</div>
                                    </div>
                                </div>
                            </div>

                            <!-- Article level Selection -->
                            <div v-if="achForm.category === 'article'" class="mb-4">
                                <label class="form-label premium-label">Maqola toifasi (Darajasi)</label>
                                <div class="custom-form-select">
                                    <div class="custom-form-trigger" @click="toggleFormDropdown('article')">
                                        <span>
                                            {{ 
                                                achForm.level === 'international' ? 'Xalqaro miqyosdagi maqola / Scopus / Web of Science (10 ball)' :
                                                achForm.level === 'national' ? 'Respublika OAK ro\'yxatidagi ilmiy maqola (8 ball)' :
                                                achForm.level === 'local' ? 'OAV, mahalliy to\'plam yoki boshqa maqola (6 ball)' :
                                                'Toifani tanlang'
                                            }}
                                        </span>
                                        <span class="arrow">▾</span>
                                    </div>
                                    <div v-if="openFormDropdown === 'article'" class="custom-form-menu">
                                        <div class="custom-form-option" :class="{ selected: achForm.level === 'international' }" @click="selectFormOption('level', 'international')">Xalqaro miqyosdagi maqola / Scopus / Web of Science (10 ball)</div>
                                        <div class="custom-form-option" :class="{ selected: achForm.level === 'national' }" @click="selectFormOption('level', 'national')">Respublika OAK ro'yxatidagi ilmiy maqola (8 ball)</div>
                                        <div class="custom-form-option" :class="{ selected: achForm.level === 'local' }" @click="selectFormOption('level', 'local')">OAV, mahalliy to'plam yoki boshqa maqola (6 ball)</div>
                                    </div>
                                </div>
                            </div>

                            <!-- Thesis level Selection -->
                            <div v-if="achForm.category === 'thesis'" class="mb-4">
                                <label class="form-label premium-label">Tezis darajasi</label>
                                <div class="custom-form-select">
                                    <div class="custom-form-trigger" @click="toggleFormDropdown('thesis')">
                                        <span>
                                            {{ 
                                                achForm.level === 'international' ? 'Xalqaro konferensiya tezisi (10 ball)' :
                                                achForm.level === 'local' ? 'Respublika yoki oliygoh miqyosidagi tezis (6 ball)' :
                                                'Darajani tanlang'
                                            }}
                                        </span>
                                        <span class="arrow">▾</span>
                                    </div>
                                    <div v-if="openFormDropdown === 'thesis'" class="custom-form-menu">
                                        <div class="custom-form-option" :class="{ selected: achForm.level === 'international' }" @click="selectFormOption('level', 'international')">Xalqaro konferensiya tezisi (10 ball)</div>
                                        <div class="custom-form-option" :class="{ selected: achForm.level === 'local' }" @click="selectFormOption('level', 'local')">Respublika yoki oliygoh miqyosidagi tezis (6 ball)</div>
                                    </div>
                                </div>
                            </div>

                            <!-- Publication level Selection -->
                            <div v-if="achForm.category === 'publication'" class="mb-4">
                                <label class="form-label premium-label">Nashr turi</label>
                                <div class="custom-form-select">
                                    <div class="custom-form-trigger" @click="toggleFormDropdown('publication')">
                                        <span>
                                            {{ 
                                                achForm.level === 'monograph' ? 'Kitob, monografiya yoki darslik (10 ball)' :
                                                achForm.level === 'local' ? 'O\'quv qo\'llanma, uslubiy qo\'llanma (6 ball)' :
                                                'Turni tanlang'
                                            }}
                                        </span>
                                        <span class="arrow">▾</span>
                                    </div>
                                    <div v-if="openFormDropdown === 'publication'" class="custom-form-menu">
                                        <div class="custom-form-option" :class="{ selected: achForm.level === 'monograph' }" @click="selectFormOption('level', 'monograph')">Kitob, monografiya yoki darslik (10 ball)</div>
                                        <div class="custom-form-option" :class="{ selected: achForm.level === 'local' }" @click="selectFormOption('level', 'local')">O'quv qo'llanma, uslubiy qo'llanma (6 ball)</div>
                                    </div>
                                </div>
                            </div>

                            <!-- IT Certificate Level Selection -->
                            <div v-if="achForm.category === 'ict_cert'" class="mb-4">
                                <label class="form-label premium-label">IT sertifikat darajasi</label>
                                <div class="custom-form-select">
                                    <div class="custom-form-trigger" @click="toggleFormDropdown('ict_cert')">
                                        <span>
                                            {{ 
                                                achForm.level === 'international' ? 'Xalqaro IT sertifikat (Google, Microsoft, Cisco, Coursera va b.) (10 ball)' :
                                                achForm.level === 'local' ? 'Mahalliy IT sertifikat (6 ball)' :
                                                'Sertifikat turini tanlang'
                                            }}
                                        </span>
                                        <span class="arrow">▾</span>
                                    </div>
                                    <div v-if="openFormDropdown === 'ict_cert'" class="custom-form-menu">
                                        <div class="custom-form-option" :class="{ selected: achForm.level === 'international' }" @click="selectFormOption('level', 'international')">Xalqaro IT sertifikat (Google, Microsoft, Cisco, Coursera va b.) (10 ball)</div>
                                        <div class="custom-form-option" :class="{ selected: achForm.level === 'local' }" @click="selectFormOption('level', 'local')">Mahalliy IT sertifikat (6 ball)</div>
                                    </div>
                                </div>
                            </div>

                            <!-- Conference Level Selection -->
                            <div v-if="achForm.category === 'conference'" class="mb-4">
                                <label class="form-label premium-label">Konferensiya darajasi</label>
                                <div class="custom-form-select">
                                    <div class="custom-form-trigger" @click="toggleFormDropdown('conference')">
                                        <span>
                                            {{ 
                                                achForm.level === 'international' ? 'Xalqaro ilmiy-amaliy konferensiya (5 ball)' :
                                                achForm.level === 'local' ? 'Respublika yoki oliygoh konferensiyasi (3 ball)' :
                                                'Darajani tanlang'
                                            }}
                                        </span>
                                        <span class="arrow">▾</span>
                                    </div>
                                    <div v-if="openFormDropdown === 'conference'" class="custom-form-menu">
                                        <div class="custom-form-option" :class="{ selected: achForm.level === 'international' }" @click="selectFormOption('level', 'international')">Xalqaro ilmiy-amaliy konferensiya (5 ball)</div>
                                        <div class="custom-form-option" :class="{ selected: achForm.level === 'local' }" @click="selectFormOption('level', 'local')">Respublika yoki oliygoh konferensiyasi (3 ball)</div>
                                    </div>
                                </div>
                            </div>

                            <div class="mb-4">
                                <label class="form-label premium-label">Qisqacha izoh / Sarlavha</label>
                                <textarea v-model="achForm.note" class="form-control premium-input" rows="3" placeholder="Hujjat haqida qisqacha ma'lumot..."></textarea>
                            </div>

                            <div class="mb-2">
                                <label class="form-label premium-label">Hujjat fayli (PDF, JPG, PNG)</label>
                                <div class="upload-zone" @click="$refs.fileInput.click()">
                                    <input type="file" ref="fileInput" class="d-none" @change="onProofSelected" />
                                    <div v-if="!achForm.proofFile && !achForm.proofUrl" class="upload-placeholder">
                                        <i class="bi bi-cloud-arrow-up fs-2 mb-2"></i>
                                        <span>Faylni tanlash uchun bosing</span>
                                    </div>
                                    <div v-else class="upload-success">
                                        <i class="bi bi-file-earmark-check-fill fs-2 text-success mb-2"></i>
                                        <span class="text-truncate d-block w-100 px-3">
                                            {{ achForm.proofFile ? achForm.proofFile.name : 'Hujjat yuklangan' }}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="modal-footer border-0 pb-4 px-4">
                        <div class="w-100 d-flex gap-3">
                            <button class="btn btn-light flex-grow-1 py-2 rounded-3 fw-bold" :disabled="step === 1" @click="prevStep">
                                <i class="bi bi-arrow-left me-2"></i> Ortga
                            </button>
                            
                            <button v-if="step === 1" class="btn btn-yutuq flex-grow-1 py-2 rounded-3 shadow-sm" @click="nextStep" :disabled="!achForm.category">
                                Keyingi <i class="bi bi-arrow-right ms-2"></i>
                            </button>
                            <button v-else class="btn btn-yutuq flex-grow-1 py-2 rounded-3 shadow-sm" @click="submitAchievement" :disabled="submitting || (!achForm.proofFile && !achForm.editing)">
                                <span v-if="submitting" class="spinner-border spinner-border-sm me-2"></span>
                                {{ achForm.editing ? "Saqlash" : "Tayyor, yuklash" }}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        </Teleport>
    </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch, computed } from "vue";
import useAuth from "@/composables/useAuth";
import useApi from "@/composables/useApi";

const auth = useAuth();
const api = useApi();
const config = useRuntimeConfig();
const API_BASE_URL = config.public.apiUrl.replace(/\/api$/, "");

const documents = ref([]);
const badges = ref([]);
const submitting = ref(false);
const step = ref(1);
const achievementModalRef = ref(null);
let bsAchievementModal = null;

const categories = [
    { key: "transcript", label: "Baholar (Transcript)" },
    { key: "recommendation", label: "Tavsiyanoma" },
    { key: "article", label: "Ilmiy maqola" },
    { key: "thesis", label: "Tezis" },
    { key: "publication", label: "Boshqa nashr" },
    { key: "language_cert", label: "Til sertifikati" },
    { key: "ict_cert", label: "IT sertifikat" },
    { key: "history_cert", label: "Tarix fanidan natija" },
    { key: "conference", label: "Konferensiya" },
];

const achForm = reactive({
    editing: false,
    id: null,
    category: null,
    title: "",
    journal: "",
    year: "",
    lang: "uz",
    level: "",
    score: "",
    role: "speaker",
    note: "",
    proofFile: null,
    proofUrl: ""
});

const openFormDropdown = ref(null);
function toggleFormDropdown(name) {
    openFormDropdown.value = openFormDropdown.value === name ? null : name;
}
function selectFormOption(field, val) {
    achForm[field] = val;
    openFormDropdown.value = null;
}

function getCatIcon(key) {
    const icons = {
        transcript: "bi bi-award",
        article: "bi bi-journal-text",
        thesis: "bi bi-briefcase",
        publication: "bi bi-book",
        language_cert: "bi bi-translate",
        ict_cert: "bi bi-laptop",
        history_cert: "bi bi-bank",
        conference: "bi bi-people",
        recommendation: "bi bi-chat-quote"
    };
    return icons[key] || "bi bi-file-earmark-text";
}

function getDocsByCategory(catKey) {
    return documents.value.filter(d => d.doc_type === catKey);
}

function formatDate(ts) {
    return ts ? new Date(ts).toLocaleDateString() : "";
}

async function loadDocuments() {
    try {
        const resp = await api.get("/documents/");
        documents.value = resp.data;
    } catch (err) {
        console.error("loadDocuments error:", err);
    }
}

async function loadBadges(userId) {
    try {
        const res = await api.get("/social-achievements/");
        badges.value = res.data
            .filter(a => String(a.user) === String(userId) && a.status === "approved")
            .map(a => ({
                id: a.id,
                title: a.sub_category || "Ijtimoiy faollik",
                score: Number(a.score || 0),
            }));
    } catch (err) {
        console.error("loadBadges error", err);
    }
}

function openAddAchievement() {
    resetForm();
    step.value = 1;
    bsAchievementModal?.show();
}

function selectCategory(k) {
    achForm.category = k;
    step.value = 2;
}

function nextStep() {
    if (step.value === 1 && !achForm.category) {
        alert("Kategoriya tanlang");
        return;
    }
    step.value++;
}

function prevStep() {
    if (step.value > 1) step.value--;
}

function onProofSelected(e) {
    const file = e.target.files?.[0];
    if (file) achForm.proofFile = file;
}

function resetForm() {
    achForm.editing = false;
    achForm.id = null;
    achForm.category = null;
    achForm.title = "";
    achForm.journal = "";
    achForm.year = "";
    achForm.lang = "uz";
    achForm.level = "";
    achForm.score = "";
    achForm.role = "speaker";
    achForm.note = "";
    achForm.proofFile = null;
    achForm.proofUrl = "";
}

async function submitAchievement() {
    if (submitting.value) return;
    if (!achForm.proofFile && !achForm.editing) {
        alert("Faylni tanlang");
        return;
    }

    submitting.value = true;
    try {
        const fd = new FormData();
        fd.append("doc_type", achForm.category);
        if (achForm.proofFile) {
            fd.append("file", achForm.proofFile);
        }
        
        const meta = {
            title: achForm.title,
            journal: achForm.journal,
            year: achForm.year,
            lang: achForm.lang,
            level: achForm.level,
            score: achForm.score,
            role: achForm.role,
            note: achForm.note
        };
        fd.append("meta", JSON.stringify(meta));

        if (achForm.editing) {
            await api.patch(`/documents/${achForm.id}/`, fd);
        } else {
            await api.post("/documents/upload/", fd);
        }

        await loadDocuments();
        bsAchievementModal?.hide();
        resetForm();
    } catch (err) {
        console.error("submit error:", err);
        const errorData = err.response?.data;
        let msg = "Xatolik yuz berdi";
        if (errorData) {
            msg = typeof errorData === 'object' ? JSON.stringify(errorData) : errorData;
        }
        alert(msg);
    } finally {
        submitting.value = false;
    }
}

async function deleteAchievement(id) {
    if (!confirm("O'chirishni tasdiqlaysizmi?")) return;
    try {
        await api.delete(`/documents/${id}/delete/`);
        await loadDocuments();
    } catch (err) {
        console.error("delete error:", err);
    }
}

onMounted(async () => {
    const { Modal } = await import("bootstrap");
    if (achievementModalRef.value) {
        bsAchievementModal = new Modal(achievementModalRef.value, {
            backdrop: "static",
        });
    }
    if (auth.user?.value?.id) {
        await loadDocuments();
        await loadBadges(auth.user.value.id);
    }
});

watch(
    () => auth.user?.value?.id,
    async (id) => {
        if (id) {
            await loadBadges(id);
            await loadDocuments();
        } else {
            badges.value = [];
            documents.value = [];
        }
    },
    { immediate: true }
);
</script>

<style scoped>
/* Achievements Component Styles */

.premium-dashboard-title {
    font-weight: 800;
    color: var(--text-main);
    letter-spacing: -1px;
    margin-bottom: 4px;
}

.glass-stats-pill {
    background-color: var(--bg-app);
    border: 1px solid var(--border-color);
    padding: 8px 18px;
    border-radius: 100px;
    display: flex;
    align-items: center;
    gap: 10px;
}

.pill-label { 
    font-size: 11px; 
    font-weight: 700; 
    text-transform: uppercase; 
    color: var(--text-muted); 
}

.pill-value { 
    font-size: 16px; 
    font-weight: 800; 
    color: var(--primary); 
}

.btn-premium-add {
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
    color: #fff;
    border: none;
    padding: 10px 24px;
    border-radius: 14px;
    font-weight: 700;
    transition: var(--transition-base);
}

.btn-premium-add:hover {
    transform: scale(1.03) translateY(-2px);
    box-shadow: var(--shadow-md);
    color: #fff;
}

/* Glassmorphism Cards */
.glass-card {
    background-color: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 28px;
    padding: 24px;
    position: relative;
    overflow: hidden;
    transition: var(--transition-base);
    box-shadow: var(--shadow-sm);
}

.glass-card:hover {
    transform: translateY(-8px);
    box-shadow: var(--shadow-md);
    border-color: var(--primary);
}

.card-glow {
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(var(--primary-rgb), 0.03) 0%, transparent 70%);
    pointer-events: none;
}

/* Category Sections */
.cat-badge-icon {
    width: 42px;
    height: 42px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    background-color: var(--primary);
    color: #fff;
}

.section-cat-title {
    font-size: 1.25rem;
    font-weight: 800;
    color: var(--text-main);
    margin: 0;
    display: flex;
    align-items: center;
    gap: 10px;
}

.count-bubble {
    font-size: 12px;
    background-color: var(--bg-app);
    color: var(--text-muted);
    padding: 2px 10px;
    border-radius: 20px;
}

/* Document Cards Content */
.doc-name-main {
    font-weight: 700;
    color: var(--text-main);
    margin-bottom: 12px;
}

.meta-tag {
    font-size: 11px;
    background-color: var(--bg-app);
    border: 1px solid var(--border-color);
    padding: 5px 12px;
    border-radius: 10px;
    color: var(--text-muted);
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}

.status-badge {
    padding: 6px 14px;
    border-radius: 12px;
    font-size: 10px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.status-badge.approved { background-color: #dcfce7; color: #166534; border: 1px solid #bbf7d0; }
.status-badge.pending { background-color: #fef3c7; color: #92400e; border: 1px solid #fde68a; }
.status-badge.rejected { background-color: #fee2e2; color: #991b1b; border: 1px solid #fecaca; }

.btn-delete-card {
    background-color: var(--bg-card);
    border: 1px solid #fee2e2;
    color: #ef4444;
    width: 32px;
    height: 32px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: var(--transition-base);
}

.btn-delete-card:hover {
    background-color: #ef4444;
    color: #fff;
    transform: scale(1.1);
}

.view-link {
    background-color: var(--bg-app);
    color: var(--text-main);
    padding: 8px 18px;
    border-radius: 12px;
    font-size: 13px;
    font-weight: 700;
    text-decoration: none;
    transition: var(--transition-base);
    display: flex;
    align-items: center;
    gap: 6px;
}

.view-link:hover {
    background-color: var(--primary);
    color: #fff;
    transform: translateX(3px);
}

/* Modal Specifics */
.category-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
    gap: 12px;
}

.cat-card-btn {
    background-color: var(--bg-app);
    border: 2px solid transparent;
    border-radius: 16px;
    padding: 16px;
    text-align: center;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
}

.cat-card-btn:hover {
    background-color: var(--bg-card);
    border-color: var(--border-color);
    transform: translateY(-3px);
}

.cat-card-btn.active {
    background-color: var(--bg-card);
    border-color: var(--primary);
    box-shadow: 0 4px 12px rgba(var(--primary-rgb), 0.15);
}

.cat-icon-wrap {
    width: 44px;
    height: 44px;
    border-radius: 12px;
    background-color: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    /* color: var(--primary); */
    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
}

.cat-card-btn.active .cat-icon-wrap {
    background-color: var(--primary);
    color: #fff;
}

.cat-label {
    font-size: 11px;
    font-weight: 700;
    color: var(--text-muted);
}

.cat-card-btn.active .cat-label {
    color: var(--primary);
}

.upload-zone {
    border: 2px dashed var(--border-color);
    border-radius: 16px;
    padding: 30px 20px;
    text-align: center;
    cursor: pointer;
    transition: all 0.2s ease;
    background-color: var(--bg-app);
}

.upload-zone:hover {
    border-color: var(--primary);
    background-color: rgba(var(--primary-rgb), 0.02);
}

.upload-placeholder {
    color: var(--text-muted);
    font-size: 13px;
}

.upload-success {
    color: var(--text-main);
}

.step-dot {
    width: 24px;
    height: 6px;
    border-radius: 10px;
    background-color: var(--border-color);
    transition: all 0.3s ease;
}

.step-dot.active {
    background-color: var(--primary-light);
}

.step-dot.current {
    width: 40px;
    background-color: var(--primary);
}

.modal-content {
    border-radius: 24px;
    border: none;
    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
}

/* Custom Dropdown Styles */
.custom-form-select {
    position: relative;
    width: 100%;
}

.custom-form-trigger {
    background-color: var(--bg-app);
    border: 1px solid var(--border-color);
    border-radius: 14px;
    padding: 12px 16px;
    font-size: 14px;
    font-weight: 700;
    color: var(--text-main);
    cursor: pointer;
    display: flex;
    justify-content: space-between;
    align-items: center;
    transition: all 0.2s ease;
}

.custom-form-trigger:hover {
    border-color: var(--primary);
    box-shadow: 0 4px 12px rgba(var(--primary-rgb), 0.05);
}

.custom-form-menu {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    margin-top: 6px;
    background-color: #ffffff;
    border: 1px solid var(--border-color);
    border-radius: 16px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.08);
    z-index: 1050;
    max-height: 250px;
    overflow-y: auto;
    padding: 6px;
}

.custom-form-option {
    padding: 10px 14px;
    font-size: 13px;
    font-weight: 700;
    color: #475569;
    border-radius: 10px;
    cursor: pointer;
    transition: all 0.15s ease;
    text-align: left;
}

.custom-form-option:hover {
    background-color: var(--primary);
    color: #ffffff;
}

.custom-form-option.selected {
    background-color: var(--primary);
    color: #ffffff;
}
</style>
