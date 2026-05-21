<template>
  <div class="social-page container-fluid py-4 min-vh-100">
    <div class="card border-0 shadow-sm p-4 mb-4 rounded-4 main-header text-white">
      <div class="row align-items-center">
        <div class="col-md-7">
          <h2 class="fw-bold mb-2">Ijtimoiy faollik indeksi (100 ball)</h2>
          <p class="mb-0 opacity-75">
            Nizom bo'yicha joriy o'quv yili uchun to'plangan ballaringiz tahlili
          </p>
        </div>
        <div class="col-md-5 text-md-end mt-3 mt-md-0">
          <div class="score-badge d-inline-block p-3 rounded-4 shadow-lg">
            <span class="d-block small text-uppercase opacity-75">Jami tasdiqlangan ball</span>
            <span class="display-5 fw-bold">{{ totalScore }} / 100</span>
          </div>
        </div>
      </div>
    </div>

    <div class="mb-4">
      <div class="nav-segmented d-inline-flex p-1 bg-glass rounded-4 shadow-sm border border-light-subtle">
        <button v-for="tab in ['talaba', 'tutor', 'tizim']" :key="tab"
          @click="activeTab = tab"
          class="btn rounded-3 px-4 py-2 text-capitalize fw-bold transition-base border-0"
          :class="activeTab === tab ? 'bg-white shadow-sm text-primary' : 'text-secondary opacity-75'">
          {{ tab }}
        </button>
      </div>
    </div>

    <div class="row g-4">
      <div class="col-lg-9">
        <TransitionGroup name="page-list" tag="div">
          <div v-for="(category, idx) in filteredCategories" :key="category.id"
            class="criterion-card card border-0 shadow-sm mb-4 rounded-4 overflow-hidden shadow-hover theme-card">
            <div class="card-body p-4">
              <div class="d-flex justify-content-between align-items-start mb-3">
                <div class="d-flex align-items-center gap-3">
                  <div class="icon-box p-3 rounded-3" :style="{ backgroundColor: category.color + '15' }">
                    <span class="fs-4" :style="{ color: category.color }">{{
                      category.icon
                    }}</span>
                  </div>
                  <div>
                    <h5 class="fw-bold mb-0">
                      {{ idx + 1 }}. {{ category.title }}
                    </h5>
                    <span class="text-primary small fw-semibold">Maksimal: {{ category.maxPoints }} ball</span>
                  </div>
                </div>
                <div class="text-end">
                  <h4 class="fw-bold mb-0" :class="category.currentScore > 0 ? 'text-success' : 'text-muted'">
                    {{ category.currentScore }}
                  </h4>
                  <div class="d-flex align-items-center justify-content-end gap-1">
                      <small class="text-muted">Tasdiqlangan</small>
                      <span v-if="category.evidences.length > 0" class="badge rounded-pill border extra-small-pill">
                          {{ category.validCount }}/2
                      </span>
                  </div>
                </div>
              </div>

              <p class="text-secondary small mb-4">{{ category.description }}</p>

              <div v-if="category.evidences.length" class="mb-4">
                <div v-for="ev in category.evidences" :key="ev.id"
                  class="evidence-row d-flex align-items-center justify-content-between p-3 rounded-3 mb-2 border border-dashed">
                  <div class="d-flex align-items-center gap-3 flex-grow-1">
                    <div
                      class="evidence-preview rounded-2 border d-flex align-items-center justify-content-center shadow-sm">
                      <i v-if="ev.type === 'pdf'" class="bi bi-file-earmark-pdf text-danger fs-5"></i>
                      <img v-else :src="ev.preview" class="img-fluid rounded-2 h-100 w-100 object-fit-cover" />
                    </div>
                    <div>
                      <div class="fw-semibold small">
                        {{ ev.subCategory }}
                        <span v-if="ev.rank" class="badge bg-secondary ms-1">{{ ev.rank }}-o'rin</span>
                      </div>
                      <div class="text-secondary x-small">{{ ev.date }}</div>
                      <div class="x-small mt-1 fst-italic">
                        "{{ ev.description }}"
                      </div>
                    </div>
                  </div>
                  <div>
                    <div class="text-start mt-1 fw-bold me-5">
                      {{ ev.score }}
                    </div>
                  </div>
                  <div class="d-flex align-items-center gap-3">
                    <span class="badge rounded-pill px-3" :class="statusClass(ev.status)">{{ statusLabel(ev.status) }}</span>
                    <button v-if="ev.status !== 'approved'" @click="deleteItem(category.id, ev.id)" class="btn btn-sm btn-outline-danger border-0">
                      <i class="bi bi-trash"></i>
                    </button>
                  </div>
                </div>
              </div>
              <div class="action-box p-3 rounded-4">
                <div v-if="category.integration === 'HEMIS'"
                  class="d-flex align-items-center gap-2 text-primary small fw-medium">
                  <i class="bi bi-hdd-network-fill"></i>
                  <span>Ma'lumotlar HEMIS tizimidan avtomatik olinadi.</span>
                </div>
                  <button v-else 
                    class="btn rounded-pill px-5 fw-bold" 
                    :class="category.validCount >= 2 ? 'btn-outline-secondary opacity-50' : 'btn-custom'"
                    :disabled="category.validCount >= 2"
                    @click="openModal(category)">
                    <i class="bi" :class="category.validCount >= 2 ? 'bi-lock-fill' : 'bi-plus-circle'"></i> 
                    {{ category.validCount >= 2 ? "Limitga yetildi (Max: 2)" : "Ma'lumot qo'shish" }}
                  </button>
                </div>
            </div>
          </div>
        </TransitionGroup>
      </div>

      <div class="col-lg-3">
        <div class="card border-0 shadow-sm p-4 rounded-4 sticky-top theme-card" style="top: 60px">
          <h6 class="fw-bold mb-3 border-bottom pb-2 text-main">Eslatmalar</h6>
          <div class="mb-3 small text-secondary">
            <i class="bi bi-info-circle me-2 text-primary"></i>
            Ko'rik-tanlovlarda olingan o'rin sertifikat yoki diplomda aniq
            ko'rinishi shart.
          </div>
          <div class="mb-3 small text-secondary">
            <i class="bi bi-calendar-check me-2 text-success"></i>
            Barcha hujjatlar joriy o'quv yili davomida olingan bo'lishi kerak.
          </div>
          <hr />
          <div class="alert alert-info border-0 small mb-0 fw-medium">
            <i class="bi bi-shield-lock-fill me-1"></i>
            Ma'lumotlar xavfsizligi va shaffofligi tyutorlar tomonidan nazorat
            qilinadi.
          </div>
        </div>
      </div>
    </div>

    <Teleport to="body">
      <div class="modal fade" id="socialModal" tabindex="-1" ref="modalRef">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-0 rounded-4 shadow-lg">
          <div class="modal-header border-0 pb-0 pt-4 px-4 bg-transparent">
            <h5 class="fw-bold">{{ activeCategory.title }}</h5>
            <button type="button" class="btn-close shadow-none" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body p-4 text-main">
            <div class="mb-4 position-relative" v-if="activeCategory.subCategories">
              <label class="form-label small fw-bold">Yo'nalish / Daraja</label>
              <div class="custom-select-wrap">
                <div class="custom-trigger-box border-2 rounded-3" @click.stop="subCatOpen = !subCatOpen">
                  <span class="select-text">{{ selectedSubCatName }}</span>
                  <i class="bi bi-chevron-down select-arrow" :class="{ 'rotate': subCatOpen }"></i>
                </div>
                
                <Transition name="fade-down">
                  <div v-if="subCatOpen" class="custom-dropdown-menu shadow-lg border border-light-subtle rounded-3 overflow-hidden">
                    <div class="custom-dropdown-item py-2 px-3 small border-bottom border-light-subtle" 
                         v-for="sub in activeCategory.subCategories" 
                         :key="sub.id"
                         :class="{ 'active': form.subCategory === sub.id }"
                         @click="selectSubCat(sub.id)">
                      {{ sub.name }}
                    </div>
                  </div>
                </Transition>
              </div>
            </div>

            <div class="mb-3" v-if="activeCategory.id === 5">
              <label class="form-label small fw-bold">Egallangan o'rin</label>
              <div class="d-flex gap-2">
                <button v-for="r in [1, 2, 3]" :key="r" class="btn flex-grow-1 border-2 fw-bold" :class="form.rank === r
                  ? 'btn-custom'
                  : 'btn-outline-secondary opacity-50'
                  " @click="form.rank = r">
                  {{ r }}-o'rin
                </button>
              </div>
            </div>


            <div class="mb-3">
              <label class="form-label small fw-bold">{{ activeCategory.formLabel || "Tadbir/Harakat tavsifi (Sana, joy, batafsil)" }}</label>
              <textarea class="form-control border-2 rounded-3 shadow-none" v-model="form.description" rows="3"
                :placeholder="activeCategory.formPlaceholder || 'Masalan: 12-fevral kuni Toshkent shahrida o\'tkazilgan...'"></textarea>
            </div>

            <div class="mb-3">
              <label class="form-label small fw-bold">Isbotlovchi hujjat ({{
                activeCategory.isImage ? "Rasm" : "PDF/Sertifikat"
              }})</label>
              <div class="upload-area border-2 border-dashed rounded-3 p-3 text-center"
                @click="$refs.fileInput.click()">
                <i class="bi bi-cloud-upload fs-2 text-muted"></i>
                <p class="small text-muted mb-0">
                  {{ form.fileName || "Faylni tanlang" }}
                </p>
                <input type="file" ref="fileInput" class="d-none" @change="onFileChange" />
              </div>
            </div>
          </div>
          <div class="modal-footer border-0 p-4 pt-0">
            <div v-if="activeCategory.validCount >= 2" class="alert alert-warning small py-2 mb-3 rounded-3">
              <i class="bi bi-exclamation-triangle me-2"></i>
              Ushbu kategoriya uchun maksimal 2 ta hujjat yuklash imkoniyatidan foydalanib bo'lgansiz.
            </div>
            <button class="btn btn-custom w-100 rounded-3 py-2 fw-bold" @click="submitData" :disabled="loading || activeCategory.validCount >= 2">
              <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
              {{ activeCategory.validCount >= 2 ? "Limit tugagan" : "Tasdiqqa yuborish" }}
            </button>
          </div>
        </div>
      </div>
    </div>
    </Teleport>

    <!-- TOAST -->
    <div class="toast-container position-fixed bottom-0 end-0 p-4">
      <div ref="toastRef" class="toast align-items-center text-white border-0" :class="toast.type" role="alert">
        <div class="d-flex">
          <div class="toast-body">
            {{ toast.message }}
          </div>
          <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import useAuth from "@/composables/useAuth";
import useApi from "@/composables/useApi";

/* ================= AUTH ================= */
const auth = useAuth();
const api = useApi();

/* ================= STATE ================= */
const activeTab = ref("talaba");
const groupOpen = ref(false)
const subCatOpen = ref(false)

const selectedSubCatName = computed(() => {
  if (!form.value.subCategory) return "Tanlang..."
  const found = activeCategory.value.subCategories?.find(s => s.id === form.value.subCategory)
  return found ? found.name : "Tanlang..."
})

function selectSubCat(id) {
  form.value.subCategory = id
  subCatOpen.value = false
}

const loading = ref(false);
const modalRef = ref(null);
let bsModal = null;

/* ================= TOAST ================= */
const toastRef = ref(null);
let bsToast = null;

const toast = ref({
  message: "",
  type: "bg-success",
});

const showToast = (message, type = "bg-success") => {
  toast.value.message = message;
  toast.value.type = type;
  if (bsToast) bsToast.show();
};

/* ================= FORM ================= */
const form = ref({
  subCategory: "",
  rank: null,
  description: "",
  file: null,
  fileName: "",
});

/* ================= ACTIVE CATEGORY ================= */
const activeCategory = ref({});

/* ================= CATEGORIES ================= */
const indexCategories = ref([
  {
    id: 1,
    title: "Kitobxonlik madaniyati",
    maxPoints: 20,
    currentScore: 0,
    color: "#3b82f6",
    icon: "📚",
    formLabel: "Mutolaa qilingan kitoblar ro'yxati va isboti",
    formPlaceholder: "Masalan: O'quv yili davomida 10-12 ta badiiy adabiyot o'qib, test topshirdim...",
    description: "Mutolaa ilovasi testlari va o'qilgan kitoblar soni asosida.",
    subCategories: [
      { id: 101, name: "10-12 ta badiiy adabiyot (Maks: 20 ball)" },
      { id: 102, name: "7-9 ta badiiy adabiyot (Maks: 15 ball)" },
      { id: 103, name: "4-6 ta badiiy adabiyot (Maks: 10 ball)" },
    ],
    evidences: [],
    isImage: false,
    group: "talaba",
  },
  {
    id: 2,
    title: "5 muhim tashabbus to'garaklari",
    maxPoints: 20,
    currentScore: 0,
    color: "#ec4899",
    icon: "🎨",
    formLabel: "To'garak nomi va undagi faoliyatingiz",
    formPlaceholder: "Masalan: 'Rassomchilik' to'garagida faol ishtirok etmoqdaman...",
    subCategories: [
      { id: 201, name: "OTMda tashkil etilgan to'garakdagi faol ishtirok (10 ball)" },
      { id: 202, name: "Madaniyat va san'at to'garaklarida ishtirok (10 ball)" },
      { id: 203, name: "Sport yo'nalishida seksiyalarda ishtirok (10 ball)" },
      { id: 204, name: "Axborot texnologiyalari yo'nalishida to'garaklarda ishtirok (10 ball)" },
      { id: 205, name: "Kitobxonlik va adabiyot to'garaklarida ishtirok (10 ball)" },
      { id: 206, name: "Bandlik yo'nalishida to'garaklarda ishtirok (10 ball)" },
      { id: 207, name: "To'garak tashkil etish va samarali faoliyat (20 ball)" },
    ],
    description: "OTMda to'garaklardagi faollik yoki ularni tashkil etish.",
    evidences: [],
    isImage: true,
    group: "talaba",
  },
  {
    id: 3,
    title: "Akademik o'zlashtirish (GPA)",
    maxPoints: 10,
    currentScore: 0,
    color: "#8b5cf6",
    icon: "🎓",
    integration: "HEMIS",
    description: "GPA ko'rsatkichi bo'yicha ball (5.0 GPA = 10 ball).",
    evidences: [],
    group: "tizim",
  },
  {
    id: 4,
    title: "Odob-axloq va dress-kod",
    maxPoints: 5,
    currentScore: 0,
    color: "#10b981",
    icon: "👔",
    integration: "TUTOR",
    formLabel: "Xulqi, kiyinish madaniyati va odob-axloq tahlili",
    formPlaceholder: "Masalan: Aprel oyi uchun odob-axloq va dress-kod qoidalariga to'liq amal qilindi...",
    description: "Dress-kod va odob-axloq bo'yicha oylik tasdiqlar.",
    evidences: [],
    group: "tutor",
  },
  {
    id: 5,
    title: "Ko'rik-tanlov va olimpiadalar",
    maxPoints: 10,
    currentScore: 0,
    color: "#f59e0b",
    icon: "🏆",
    formLabel: "Tanlov nomi va erishilgan natija",
    formPlaceholder: "Masalan: 'Yil talabasi' tanlovining OTM bosqichida 1-o'rinni egalladim...",
    subCategories: [
      { id: 7, name: "Xalqaro miqyosda" },
      { id: 8, name: "Respublika miqyosida" },
      { id: 9, name: "Viloyat/Hududiy miqyosda" },
      { id: 10, name: "OTM ichki bosqichida" },
    ],
    description: "Diplom va olingan o'rinlar bo'yicha natijalar.",
    evidences: [],
    isImage: false,
    group: "talaba",
  },
  {
    id: 6,
    title: "Darslardagi qatnashish (Davomat)",
    maxPoints: 5,
    currentScore: 0,
    color: "#ef4444",
    icon: "⏰",
    integration: "HEMIS",
    description: "Semestr davomida qoldirilgan soatlar tahlili.",
    evidences: [],
    group: "tizim",
  },
  {
    id: 7,
    title: "Ma'rifat darslaridagi faollik",
    maxPoints: 10,
    currentScore: 0,
    color: "#06b6d4",
    icon: "💡",
    integration: "HEMIS",
    description: "Ma'rifat darslaridagi davomat va baholar.",
    evidences: [],
    group: "tutor",
  },
  {
    id: 8,
    title: "Jamoat ishlari va volontyorlik",
    maxPoints: 5,
    currentScore: 0,
    color: "#f97316",
    icon: "🤝",
    formLabel: "Tadbir nomi va volontyorlik faoliyati",
    formPlaceholder: "Masalan: 'Yashil makon' aksiyasida ko'ngilli sifatida 20 ta daraxt ekishda qatnashdim...",
    description: "Ko'ngilli sifatida amalga oshirilgan jamoat ishlari.",
    evidences: [],
    isImage: true,
    group: "tutor",
  },
  {
    id: 9,
    title: "Madaniy tashriflar",
    maxPoints: 5,
    currentScore: 0,
    color: "#14b8a6",
    icon: "🎭",
    formLabel: "Muassasa nomi va tashrif maqsadi",
    formPlaceholder: "Masalan: Temuriylar tarixi davlat muzeyiga guruh bilan madaniy tashrif buyurildi...",
    subCategories: [
      { id: 901, name: "Har oyda kamida bir marotaba (5 ball)" },
      { id: 902, name: "Har ikki oyda kamida bir marotaba (3 ball)" },
      { id: 903, name: "Semestrda kamida bir marotaba (1 ball)" },
    ],
    description: "Teatr, muzey va tarixiy joylarga oylik tashriflar.",
    evidences: [],
    isImage: true,
    group: "talaba",
  },
  {
    id: 10,
    title: "Sport va sog'lom turmush",
    maxPoints: 5,
    currentScore: 0,
    color: "#ef4444",
    icon: "⚽",
    formLabel: "Sport turi va erishilgan natija",
    formPlaceholder: "Masalan: Shaxmat bo'yicha fakultetlararo musobaqada 2-o'rinni oldim...",
    subCategories: [
      { id: 11, name: "OTM terma jamoasi a'zosi (5 ball)" },
      { id: 12, name: "Sport seksiya/to'garak (3 ball)" },
      { id: 13, name: "Sport musobaqasi ishtirokchisi (1 ball)" },
    ],
    description: "Sport klublari va sog'lom turmush tarzi ko'rsatkichi.",
    evidences: [],
    isImage: true,
    group: "talaba",
  },
  {
    id: 11,
    title: "Boshqa ma'naviy faollik",
    maxPoints: 5,
    currentScore: 0,
    color: "#6366f1",
    icon: "📱",
    formLabel: "Tadbir nomi va bajarilgan ish",
    formPlaceholder: "Masalan: Adiblar xiyobonida o'tkazilgan she'rxonlik kechasida faol ishtirok etdim...",
    description: "Targ'ibot ishlari va ijtimoiy tarmoqlardagi faollik.",
    evidences: [],
    isImage: true,
    group: "tutor",
  },
]);

/* ================= MODAL ================= */
const openModal = (cat) => {
  activeCategory.value = cat;
  form.value = {
    subCategory: "",
    rank: null,
    description: "",
    file: null,
    fileName: "",
  };
  if (bsModal) bsModal.show();
};

/* ================= FILE ================= */
const onFileChange = (e) => {
  const file = e.target.files[0];
  if (file) {
    form.value.file = file;
    form.value.fileName = file.name;
  }
};

/* ================= SUBMIT ================= */
const submitData = async () => {
  if (!form.value.file) {
    showToast("Iltimos, isbotlovchi hujjatni yuklang!", "bg-danger");
    return;
  }

  loading.value = true;

  const fd = new FormData();
  fd.append("category", activeCategory.value.id);
  fd.append("sub_category", form.value.subCategory);
  fd.append("rank", form.value.rank || "");
  fd.append("date", new Date().toISOString().split('T')[0]); // Auto-date
  fd.append("description", form.value.description);
  fd.append("proof_file", form.value.file);
  

  try {
    const resp = await api.post("/social-achievements/", fd);
    if (resp.status === 201) {
      showToast("Muvaffaqiyatli yuborildi. Admin tasdiqlashini kuting.");
      await fetchUserAchievements();
      if (bsModal) bsModal.hide();
    }
  } catch (err) {
    showToast("Xatolik yuz berdi. Qayta urinib ko'ring.", "bg-danger");
  } finally {
    loading.value = false;
  }
};

/* ================= FETCH ================= */
const fetchUserAchievements = async () => {
  try {
    const resp = await api.get("/social-achievements/");
    const allData = resp.data;

    const currentUserId = auth.user?.value?.id;
    const userData = allData.filter(
      (item) => String(item.user) === String(currentUserId)
    );

    indexCategories.value.forEach((cat) => {
      cat.currentScore = 0;
      cat.evidences = userData.filter((item) => item.category === cat.id);

      // SINGLETON LOGIC: Faqat oxirgi tasdiqlangan hujjatning bali hisoblanadi
      const approvedList = cat.evidences.filter((ev) => ev.status === "approved");
      if (approvedList.length > 0) {
        // Oxirgi yuklangan (eng baland ID yoki oxirgi element) tanlanadi
        const latest = approvedList[approvedList.length - 1];
        cat.currentScore = parseFloat(latest.score || 0);
      }
      
      // Limit logic: Faqat kutilayotgan va tasdiqlanganlar limitga hisoblanadi
      cat.validCount = cat.evidences.filter(ev => ev.status !== 'rejected').length;
    });
  } catch (err) {
    console.error("Xatolik:", err);
  }
};
/* ================= DELETE ================= */
const deleteItem = async (catId, itemId) => {
  const ok = window.confirm("Ushbu yutuqni o'chirishni tasdiqlaysizmi?");
  if (!ok) return;

  try {
    await api.delete(`/social-achievements/${itemId}/`);
    showToast("Yutuq muvaffaqiyatli o'chirildi", "bg-warning");
    await fetchUserAchievements();
  } catch {
    showToast("O'chirishda xatolik yuz berdi", "bg-danger");
  }
};

/* ================= COMPUTED ================= */
const filteredCategories = computed(() => {
  return indexCategories.value.filter((cat) => cat.group === activeTab.value);
});

const totalScore = computed(() => {
  const sum = indexCategories.value.reduce(
    (acc, curr) => acc + curr.currentScore,
    0
  );
  return parseFloat(sum.toFixed(1));
});

const statusClass = (s) => ({
  "bg-warning-subtle text-warning border-warning-subtle": s === "pending",
  "bg-success-subtle text-success border-success-subtle": s === "approved",
  "bg-danger-subtle text-danger border-danger-subtle": s === "rejected",
});

const statusLabel = (s) =>
({
  pending: "Tekshirilmoqda",
  approved: "Tasdiqlandi",
  rejected: "Rad etildi",
}[s]);

/* ================= INIT ================= */
onMounted(async () => {
  const { Modal, Toast } = await import("bootstrap");
  if (modalRef.value) bsModal = new Modal(modalRef.value);
  if (toastRef.value) bsToast = new Toast(toastRef.value, { delay: 3500 });
  await fetchUserAchievements();

  if (process.client) {
    window.addEventListener('click', () => {
      subCatOpen.value = false;
    });
  }
});
</script>

<style scoped>
.bg-glass {
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(10px);
}

.nav-segmented {
  background: #f1f5f9;
}

.nav-segmented .btn {
  font-size: 0.85rem;
  letter-spacing: 0.3px;
}

.transition-base {
  transition: all 0.3s ease;
}

/* List Transitions */
.page-list-enter-active,
.page-list-leave-active {
  transition: all 0.4s ease;
}
.page-list-enter-from {
  opacity: 0;
  transform: translateY(20px);
}
.page-list-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}
.page-list-move {
  transition: transform 0.4s ease;
}

.shadow-hover:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08) !important;
  transition: all 0.3s ease;
}

.criterion-card {
  transition: all 0.3s ease;
}

.btn-custom {
  background: var(--primary);
  color: #fff;
  border: none;
}
.btn-custom:hover {
  background: var(--primary-light);
  color: #fff;
  transform: translateY(-1px);
}

/* CUSTOM DROPDOWN IN MODAL */
.custom-select-wrap {
    position: relative;
    cursor: pointer;
}

.custom-trigger-box {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 15px;
    background: #fff;
    transition: all 0.2s;
}

.custom-trigger-box:hover {
    border-color: var(--primary) !important;
}

.select-arrow {
    transition: transform 0.3s;
}

.select-arrow.rotate {
    transform: rotate(180deg);
}

.custom-dropdown-menu {
    position: absolute;
    top: calc(100% + 5px);
    left: 0;
    right: 0;
    background: #fff;
    z-index: 1050;
}

.custom-dropdown-item {
    transition: all 0.2s;
}

.custom-dropdown-item:hover {
    background: #e8f1fa;
    color: var(--primary);
}

.custom-dropdown-item.active {
    background: var(--primary);
    color: #fff;
}

.fade-down-enter-active,
.fade-down-leave-active {
    transition: all 0.2s ease;
}

.fade-down-enter-from,
.fade-down-leave-to {
    opacity: 0;
    transform: translateY(-10px);
}
</style>
