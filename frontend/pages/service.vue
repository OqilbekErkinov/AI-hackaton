<template>
  <div class="service-page min-vh-100">
    <!-- MESH GRADIENT BACKGROUND -->
    <div class="mesh-gradient"></div>

    <section class="container py-5 position-relative z-1">
      <!-- HERO HEADER -->
      <div class="header-section text-center mb-5 animate-header">
        <h1 class="display-4 fw-bold mb-3 text-gradient">Xizmatlar Markazi</h1>
        <p class="lead text-muted mx-auto" style="max-width: 600px">
          Sizning muvaffaqiyatli talabalik davringiz uchun barcha kerakli vositalar va ko'maklar bir joyda jamlangan.
        </p>
      </div>

      <!-- SEARCH & FILTER BAR -->
      <div class="glass-bar p-3 mb-5 d-flex flex-wrap align-items-center gap-3 animate-bar">
        <div class="search-input flex-grow-1">
          <i class="bi bi-search ms-3 text-muted position-absolute mt-2 mt-md-3"></i>
          <input 
            v-model="searchQuery" 
            type="text" 
            class="form-control ps-5 py-2 py-md-3 border-0 shadow-none bg-transparent" 
            placeholder="Xizmat nomini yozing..."
          />
        </div>
        <div class="categories d-flex gap-2">
          <button 
            v-for="cat in categories" 
            :key="cat.id" 
            class="btn filter-btn px-4 rounded-pill"
            :class="activeCategory === cat.id ? 'active shadow-sm' : 'text-muted'"
            @click="activeCategory = cat.id"
          >
            {{ cat.label }}
          </button>
        </div>
      </div>

      <!-- SERVICES GRID -->
      <div class="row g-4 overflow-hidden">
        <div 
          v-for="(s, index) in filteredServices" 
          :key="s.id" 
          class="col-md-6 col-lg-4 animate-card"
          ref="cardRefs"
        >
          <div class="service-card h-100 border-0 overflow-hidden">
            <div class="card-glass-body p-4 d-flex flex-column h-100">
              <div class="service-icon-box mb-4" :class="s.colorClass">
                <i :class="[s.icon, 'fs-3']"></i>
              </div>
              <div class="service-meta mb-3">
                <span class="badge rounded-pill" :class="s.typeColor">{{ s.type }}</span>
              </div>
              <h3 class="h5 fw-bold mb-2">{{ s.title }}</h3>
              <p class="text-muted small flex-grow-1">{{ s.description }}</p>
              
              <div class="mt-4 pt-3 border-top border-light d-flex align-items-center justify-content-between">
                <span v-if="s.price === 'Free'" class="text-success small fw-bold">Bepul</span>
                <span v-else class="text-primary small fw-semibold">{{ s.price }}</span>
                <button 
                  class="btn btn-sm btn-link-arrow p-0 text-decoration-none fw-bold"
                  @click="openServiceAction(s)"
                >
                  {{ s.cta }} <i class="bi bi-arrow-right ms-1"></i>
                </button>
              </div>
            </div>
            <!-- Decorative circle -->
            <div class="card-deco"></div>
          </div>
        </div>

        <!-- EMPTY STATE -->
        <div v-if="filteredServices.length === 0" class="col-12 text-center py-5">
          <div class="empty-state glass-card p-5 border-0">
            <i class="bi bi-search fs-1 text-muted mb-3 d-block"></i>
            <h4>Hech narsa topilmadi</h4>
            <p class="text-muted">Boshqa kalit so'zlar bilan qidirib ko'ring yoki boshqa toifani tanlang.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- SERVICE MODALS -->
    <div 
      ref="serviceModal" 
      class="modal fade glass-modal" 
      tabindex="-1" 
      aria-hidden="true"
    >
      <div class="modal-dialog modal-dialog-centered modal-lg">
        <div class="modal-content border-0 bg-transparent shadow-lg text-white">
          <div class="modal-body p-0 rounded-4 overflow-hidden position-relative">
            <!-- Modal Background -->
            <div class="modal-bg-deco" :class="activeService?.colorClass"></div>
            
            <div class="p-4 p-md-5 position-relative z-1">
              <div class="d-flex justify-content-between align-items-start mb-4">
                <div class="d-flex align-items-center gap-3">
                  <div class="modal-icon-wrap" :class="activeService?.colorClass">
                    <i :class="activeService?.icon"></i>
                  </div>
                  <div>
                    <h2 class="h4 mb-1 fw-bold">{{ activeService?.title }}</h2>
                    <span class="badge bg-white text-dark rounded-pill opacity-75">{{ activeService?.type }}</span>
                  </div>
                </div>
                <button type="button" class="btn-close btn-close-white shadow-none" data-bs-dismiss="modal" aria-label="Close"></button>
              </div>

              <div class="modal-info-grid mb-5">
                <p class="lead opacity-75">{{ activeService?.longDescription || activeService?.description }}</p>
              </div>

              <div class="modal-actions d-flex gap-3">
                <button 
                  class="btn btn-white-glass px-5 py-3 rounded-pill fw-bold flex-grow-1 flex-md-grow-0"
                  @click="executeService(activeService)"
                  :disabled="isProcessing"
                >
                  {{ isProcessing ? 'Ishlanmoqda...' : 'Xizmatdan foydalanish' }}
                </button>
                <button 
                  class="btn btn-outline-light rounded-pill px-4"
                  data-bs-dismiss="modal"
                >
                  Yopish
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- TOAST NOTIFICATIONS -->
    <div class="toast-container position-fixed bottom-0 end-0 p-3">
      <div 
        v-for="t in toasts" 
        :key="t.id" 
        class="toast show align-items-center border-0 mb-2 glass-toast"
        role="alert" 
        aria-live="assertive" 
        aria-atomic="true"
      >
        <div class="d-flex">
          <div class="toast-body p-3">
            <i class="bi bi-info-circle me-2"></i> {{ t.message }}
          </div>
          <button type="button" class="btn-close me-2 m-auto shadow-none" @click="removeToast(t.id)"></button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import useApi from '@/composables/useApi';
import useAuth from '@/composables/useAuth';

// LIBRARIES
let gsap;
let Modal;

const router = useRouter();
const api = useApi();
const auth = useAuth();

// STATE
const searchQuery = ref('');
const activeCategory = ref('all');
const activeService = ref(null);
const isProcessing = ref(false);
const toasts = ref([]);
const serviceModal = ref(null);
let bsModal = null;

const categories = [
  { id: 'all', label: 'Barchasi' },
  { id: 'ai', label: 'AI Smart Tools' },
  { id: 'life', label: 'Talabalar Hayoti' },
  { id: 'admin', label: 'Ma\'muriyat' },
];

const services = ref([
  {
    id: 'ai-mentor',
    catId: 'ai',
    title: 'AI Akademik Mentor',
    description: `Sizning shaxsiy o'quv rejangizni tuzish va akademik maqsadlaringizga erishishda yordam beradi.`,
    longDescription: `DeepMind texnologiyalariga asoslangan AI Mentor sizning baholaringiz, qiziqishlaringiz va bo'sh vaqtingizni tahlil qilib, eng optimal o'quv strategiyasini taklif qiladi.`,
    icon: 'bi bi-robot',
    type: 'AI Tool',
    typeColor: 'bg-soft-purple',
    colorClass: 'service-purple',
    price: 'Free',
    cta: 'Suhbatni boshlash',
    action: () => router.push('/ai-assistant')
  },
  {
    id: 'scholarship-matcher',
    catId: 'ai',
    title: 'Grant & Stipendiya Bot',
    description: `Sizning profilingizga mos keladigan barcha milliy va xalqaro grantlarni avtomatik qidirib topadi.`,
    longDescription: `Yuzlab grant manbalarini skanerlash orqali siz loyiq bo'lgan va murojaat qilishingiz mumkin bo'lgan moliyaviy yordamlarni saralab beradi.`,
    icon: 'bi bi-award',
    type: 'AI Agent',
    typeColor: 'bg-soft-gold',
    colorClass: 'service-gold',
    price: 'Free',
    cta: 'Grantlarni ko\'rish',
    action: () => router.push('/scholarship')
  },
  {
    id: 'exam-prep',
    catId: 'ai',
    title: 'AI Exam Grader',
    description: `IELTS/SAT insholaringizni tekshirib, ball qo'yadi va xatolaringizni tushuntiradi.`,
    longDescription: `Sun'iy intellekt xuddi haqiqiy imtihon oluvchidek sizning ishingizni baholaydi va qaysi jihatlarni yaxshilash kerakligini ko'rsatib beradi.`,
    icon: 'bi bi-pencil-square',
    type: 'Learning',
    typeColor: 'bg-soft-blue',
    colorClass: 'service-blue',
    price: 'Premium',
    cta: 'Tekshirishni boshlash',
    action: 'modal'
  },
  {
    id: 'housing-explorer',
    catId: 'life',
    title: 'Turar-joy (Housing)',
    description: `Universitetga yaqin va arzon ijara uylar hamda yotoqxonalar katalogi.`,
    longDescription: `Talabalar uchun maxsus saralangan va tekshirilgan turar-joy ob'ektlari. Narxlar, sharoitlar va manzil bo'yicha qulay qidiruv.`,
    icon: 'bi bi-houses',
    type: 'Living',
    typeColor: 'bg-soft-green',
    colorClass: 'service-green',
    price: 'Info',
    cta: 'Uylarni ko\'rish',
    action: 'modal'
  },
  {
    id: 'campus-events',
    catId: 'life',
    title: 'Klublar & Tadbirlar',
    description: `Xakatolar, konferensiyalar va sport tadbirlari haqida batafsil ma'lumot.`,
    longDescription: `Talabalik hayotingizni yorqinroq qiling. Eng so'nggi tadbirlar, to'garaklar va jamoat ishlaridan xabardor bo'ling.`,
    icon: 'bi bi-calendar-event',
    type: 'Community',
    typeColor: 'bg-soft-red',
    colorClass: 'service-red',
    price: 'Join',
    cta: 'Sahifaga o\'tish',
    action: () => router.push('/announcement')
  },
  {
    id: 'student-discounts',
    catId: 'life',
    title: 'Talabalar uchun Chegirmalar',
    description: `Kafe, do'konlar va onlayn xizmatlarda talabalar uchun eksklyuziv takliflar.`,
    longDescription: `Nexora qatnashchisi bo'lganingiz uchun maxsus promo-kodlar va chegirmalardan foydalaning.`,
    icon: 'bi bi-percent',
    type: 'Benefits',
    typeColor: 'bg-soft-cyan',
    colorClass: 'service-cyan',
    price: 'Save',
    cta: 'Hamkorlarni ko\'rish',
    action: 'modal'
  },
  {
    id: 'study-buddy',
    catId: 'life',
    title: 'Study Buddy Matching',
    description: `Bir xil mutaxassislikdagi yoki qiziqishdagi tengdoshlar bilan guruh bo'lib o'qish uchun topishish.`,
    longDescription: `Birgalikda o'rganish har doim osonroq. O'z jamoangizni toping va loyihalarni birga amalga oshiring.`,
    icon: 'bi bi-people',
    type: 'Social',
    typeColor: 'bg-soft-indigo',
    colorClass: 'service-indigo',
    price: 'Connect',
    cta: 'Buddy topish',
    action: 'modal'
  },
  {
    id: 'document-hub',
    catId: 'admin',
    title: 'Ma\'lumotnomalar Markazi',
    description: `O'qish joyidan ma'lumotnoma va boshqa rasmiy hujjatlar uchun elektron so'rov.`,
    longDescription: `Navbatlarsiz va kutilishlarsiz. Hujjatlaringizni onlayn buyurtma qiling va PDF shaklda yuklab oling.`,
    icon: 'bi bi-file-earmark-check',
    type: 'Admin',
    typeColor: 'bg-soft-gray',
    colorClass: 'service-gray',
    price: 'Utility',
    cta: 'So\'rov yuborish',
    action: 'modal'
  }
]);

// COMPUTED
const filteredServices = computed(() => {
  let list = services.value;
  
  if (activeCategory.value !== 'all') {
    list = list.filter(item => item.catId === activeCategory.value);
  }
  
  if (searchQuery.value.length > 0) {
    const q = searchQuery.value.toLowerCase();
    list = list.filter(item => 
      item.title.toLowerCase().includes(q) || 
      item.description.toLowerCase().includes(q)
    );
  }
  
  return list;
});

// METHODS
const openServiceAction = (s) => {
  if (typeof s.action === 'function') {
    s.action();
  } else {
    activeService.value = s;
    if (bsModal) bsModal.show();
  }
};

const executeService = (s) => {
  isProcessing.value = true;
  
  // Generic simulation
  setTimeout(() => {
    isProcessing.value = false;
    addToast(`${s.title} bo'yicha so'rovingiz qabul qilindi. Tez orada javob beramiz.`);
    if (bsModal) bsModal.hide();
  }, 1500);
};

const addToast = (message) => {
  const id = Date.now();
  toasts.value.push({ id, message });
  setTimeout(() => removeToast(id), 5000);
};

const removeToast = (id) => {
  toasts.value = toasts.value.filter(t => t.id !== id);
};

// LIFECYCLE
onMounted(async () => {
  // Wait for heavy components
  try {
    const bootstrap = await import('bootstrap');
    Modal = bootstrap.Modal;
    bsModal = new Modal(serviceModal.value);
  } catch (e) {
    console.error('Modal init failed');
  }

  // ANIMATIONS
  try {
    const gsapModule = await import('gsap');
    gsap = gsapModule.default;
    
    gsap.from('.animate-header', {
      y: -50,
      opacity: 0,
      duration: 1,
      ease: 'power3.out'
    });

    gsap.from('.animate-bar', {
      scale: 0.9,
      opacity: 0,
      duration: 0.8,
      delay: 0.3,
      ease: 'back.out(1.7)'
    });

    gsap.from('.animate-card', {
      y: 100,
      opacity: 0,
      stagger: 0.1,
      duration: 0.8,
      delay: 0.5,
      ease: 'power2.out'
    });
  } catch (e) {
    console.warn('GSAP animation skipped');
  }
});
</script>
