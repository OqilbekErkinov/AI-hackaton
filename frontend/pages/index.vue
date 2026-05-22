<template>
  <div class="home-container">
    <section>
      <Hero style="" />
    </section>

        <!-- ✨ SECTION 2: WHY NEXORA? (INDIVIDUAL GLASS CARDS) -->
    <section class="h-section h-features" style="margin-top: -6rem; z-index: 100;">
      <div class="container">
        <h2 class="h-section-title mb-5">Nega bizni tanlashadi?</h2>
        
        <div class="feature-grid">
          <!-- Card 1 -->
          <div class="feature-card-premium glass-card theme-card">
            <div class="feature-icon-box">
              <i class="bi bi-robot"></i>
            </div>
            <h4>AI Yordamchi</h4>
            <p>Talabalar uchun maxsus ishlab chiqilgan sun'iy intellekt orqali barcha savollarga tezkor javob oling.</p>
          </div>

          <!-- Card 2 -->
          <div class="feature-card-premium glass-card theme-card">
            <div class="feature-icon-box">
              <i class="bi bi-graph-up-arrow"></i>
            </div>
            <h4>Jonli Reyting</h4>
            <p>Sizning natijalaringiz real vaqt rejimida yangilanadi va shaffof reyting tizimi orqali ko'rsatiladi.</p>
          </div>

          <!-- Card 3 -->
          <div class="feature-card-premium glass-card theme-card">
            <div class="feature-icon-box">
              <i class="bi bi-trophy"></i>
            </div>
            <h4>Ijtimoiy Faollik</h4>
            <p>Faqat baholar emas, balki jamoat ishlari va volontyorlik orqali ham ball to'plang.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 🎓 SECTION 3: TOP SCHOLARSHIPS -->
    <section v-if="scholarships.length" class="h-section h-scholarships">
      <div class="container">
        <div class="d-flex justify-content-between align-items-end mb-5">
          <h2 class="h-section-title mb-0">🎓 Mashhur stipendiyalar</h2>
          <NuxtLink to="/scholarship" class="text-primary fw-bold text-decoration-none h5 mb-2">
            Hammasini ko'rish <i class="bi bi-arrow-right"></i>
          </NuxtLink>
        </div>

        <div class="sch-grid">
          <div v-for="s in scholarships.slice(0, 3)" :key="s.id" class="sch-card-premium glass-card theme-card">
            <div class="sch-meta">
              <span class="sch-deadline">⏳ {{ new Date(s.deadline).toLocaleDateString() }}</span>
              <span class="sch-amount">💰 {{ s.amount || 'Noma\'lum' }}</span>
            </div>
            <h3 class="sch-title-premium">{{ s.title }}</h3>
            <p class="sch-desc-premium">{{ s.short_description || s.brief }}</p>
            
            <NuxtLink :to="`/scholarship/${s.id}`" class="h-btn-premium mt-auto">
              O'rganish
            </NuxtLink>
          </div>
        </div>
      </div>
    </section>

        <!-- 🔥 SECTION 1: TOP ANNOUNCEMENTS (MULTI-CARD SLIDER) -->
    <section v-if="topAnnouncements.length" class="h-section h-announcements">
      <div class="container container-wide">
        <div class="d-flex justify-content-between align-items-end mb-5">
           <h2 class="h-section-title mb-0">🔥 Muhim e'lonlar</h2>
           <div class="carousel-nav-btns d-none d-md-flex">
              <button @click="prevSlide" class="nav-btn"><i class="bi bi-chevron-left"></i></button>
              <button @click="nextSlide" class="nav-btn"><i class="bi bi-chevron-right"></i></button>
           </div>
        </div>
        
        <div class="carousel-viewport">
          <div 
            class="carousel-track" 
            :style="{ transform: `translateX(-${currentIdx * (100 / visibleCards)}%)` }"
          >
            <div 
              v-for="item in topAnnouncements" 
              :key="item.id" 
              class="carousel-card-wrapper"
              :style="{ flex: `0 0 ${100 / visibleCards}%` }"
            >
              <div class="ann-card glass-card theme-card">
                 <div class="ann-img-box">
                    <img v-if="item.image" :src="item.image" class="ann-image" alt="announcement" />
                    <div v-else class="ann-image-stub">
                       <i class="bi bi-megaphone"></i>
                    </div>
                    <span class="ann-tag-pill">{{ item.type || 'E\'lon' }}</span>
                 </div>
                 <div class="ann-body">
                    <h4 class="ann-title">{{ item.title }}</h4>
                    <p class="ann-text">{{ item.short || item.description }}</p>
                    <NuxtLink :to="`/announcement`" class="ann-link">
                      Batafsil <i class="bi bi-arrow-right"></i>
                    </NuxtLink>
                 </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from "vue";
import Hero from "./hero.vue";

definePageMeta({ layout: "default" });

const api = useApi();
const config = useRuntimeConfig();
const API_BASE_URL = config.public.apiUrl.replace(/\/api$/, "");

const topAnnouncements = ref([]);
const scholarships = ref([]);
const currentIdx = ref(0);
let carouselTimer = null;

// Responsive cards visible count
const screenWidth = ref(1200);
const visibleCards = computed(() => {
  if (screenWidth.value < 768) return 1;
  if (screenWidth.value < 1024) return 2;
  return 3;
});

async function fetchData() {
  try {
    const [annRes, schRes] = await Promise.all([
      api.get("/announcements/"),
      api.get("/scholarships/")
    ]);

    topAnnouncements.value = annRes.data.slice(0, 8).map(item => ({
      ...item,
      image: item.image ? (item.image.startsWith('http') ? item.image : API_BASE_URL + item.image) : null
    }));

    scholarships.value = schRes.data;
  } catch (err) {
    console.error("Home page fetch error:", err);
  }
}

function nextSlide() {
  const maxIdx = topAnnouncements.value.length - visibleCards.value;
  if (currentIdx.value < maxIdx) {
    currentIdx.value++;
  } else {
    currentIdx.value = 0;
  }
}

function prevSlide() {
  if (currentIdx.value > 0) {
    currentIdx.value--;
  } else {
    currentIdx.value = Math.max(0, topAnnouncements.value.length - visibleCards.value);
  }
}

function startCarousel() {
  carouselTimer = setInterval(nextSlide, 7000);
}

function updateWidth() {
  if (typeof window !== 'undefined') {
    screenWidth.value = window.innerWidth;
  }
}

onMounted(async () => {
  updateWidth();
  window.addEventListener('resize', updateWidth);
  await fetchData();
  startCarousel();
});

onUnmounted(() => {
  window.removeEventListener('resize', updateWidth);
  if (carouselTimer) clearInterval(carouselTimer);
});
</script>

<style scoped>
.home-container {
  overflow-x: hidden;
  margin-top: -24px !important;
}
.container-wide {
  max-width: 1400px;
}
</style>
