<template>
  <div class="profile-wrap" v-if="!loading">
    <!-- HERO -->
    <section class="hero">
      <div class="hero-card">
        <!-- MESSAGE BUTTON -->
        <button class="message-btn" @click="goToChat" title="Xabar yuborish">
          <i class="bi bi-chat-dots-fill"></i>
        </button>

        <div class="avatar">
          <img v-if="user.avatar" :src="user.avatar" />
          <span v-else>{{ initials }}</span>
        </div>

        <div class="info">
          <h2>{{ user.fullname || "Ism yo‘q" }}</h2>

          <p class="muted">
            <span v-if="user.universityFull">
               {{ user.universityFull }} •
            </span>
            <span v-else-if="user.universityShort">
               {{ user.universityShort }} •
            </span>
            <span v-if="user.major">{{ user.major }} • </span>
            <span v-if="user.course">  {{ user.course }}-kurs </span>



          </p>

          <div class="stats">
            <div style="display: flex;">
              <strong class="mt-0" style="font-size: 1rem;">Ijtimoiy faollik indeksi:</strong>
              <span class="ms-2">{{ socialScore }} / 100</span>
            </div>
          </div>

          <!-- XP Bar removed -->
        </div>
      </div>
    </section>

    <!-- ACADEMIC DOCUMENTS & ACHIEVEMENTS -->
    <section v-if="documents.length > 0" class="badges-section mt-5">
      <div class="section-header mb-4">
        <h3 class="fw-bold">Yutuqlar va Akademik Hujjatlar</h3>
        <p class="text-muted">Talaba tomonidan yuklangan va tasdiqlangan rasmiy yutuqlar</p>
      </div>

      <div v-for="cat in categories" :key="cat.key" class="achievement-group mb-5">
          <div v-if="getDocsByCategory(cat.key).length > 0">
              <div class="d-flex align-items-center gap-3 mb-4">
                  <div class="cat-icon-wrap">
                    <i :class="getCatIcon(cat.key)"></i>
                  </div>
                  <h5 class="cat-title mb-0">
                      {{ cat.label }}
                      <span class="badge-count">{{ getDocsByCategory(cat.key).length }}</span>
                  </h5>
              </div>
              
              <div class="badge-grid">
                  <div v-for="doc in getDocsByCategory(cat.key)" :key="doc.id" class="glass-card">
                      <div class="card-glow"></div>
                      <div class="card-content">
                        <div class="doc-icon mb-3">
                          <i class="bi bi-file-earmark-richtext"></i>
                        </div>
                        <h6 class="doc-name text-truncate" :title="doc.label">
                          {{ doc.label || cat.label }}
                        </h6>
                        <div class="doc-meta-info">
                           <div v-if="doc.meta?.journal" class="meta-item">
                               <i class="bi bi-journal-bookmark"></i>
                               <span>{{ doc.meta.journal }}</span>
                           </div>
                           <div v-if="doc.meta?.level" class="meta-item">
                               <i class="bi bi-award"></i>
                               <span>{{ doc.meta.level }} ({{ doc.meta.score || '' }})</span>
                           </div>
                        </div>
                        <div class="mt-4">
                          <a :href="doc.fileUrl" target="_blank" class="btn-premium-view">
                            <i class="bi bi-eye"></i>
                            Hujjatni ko'rish
                          </a>
                        </div>
                      </div>
                  </div>
              </div>
          </div>
      </div>
    </section>

    <!-- SOCIAL ACHIEVEMENTS -->
    <section class="badges">
      <h3>Ijtimoiy faollik: {{ badges.length }}</h3>

      <div class="badge-grid">
        <div v-for="b in badges" :key="b.id" class="badge-item">
          <div class="icon">🏅</div>
          <div class="title">{{ b.title }}</div>
          <div class="xp">+{{ fmt(b.score) }} ball</div>
        </div>
      </div>

      <div v-if="badges.length === 0" class="muted">
        Hozircha ijtimoiy faollik yo‘q
      </div>
    </section>

    <!-- TOAST -->
    <div v-if="toast.show" class="toast-box" :class="toast.type">
      {{ toast.message }}
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from "vue";
import { useRoute, useRouter } from "#app";
import useAuth from "@/composables/useAuth";
import useApi from "@/composables/useApi";

const route = useRoute();
const router = useRouter();
const auth = useAuth();
const api = useApi();
const config = useRuntimeConfig();
const API_BASE_URL = config.public.apiUrl.replace(/\/api$/, "");

/* ---------------- TOAST ---------------- */
const toast = reactive({
  show: false,
  message: "",
  type: "info",
});

function showToast(msg, type = "info", timeout = 3000) {
  toast.message = msg;
  toast.type = type;
  toast.show = true;

  setTimeout(() => {
    toast.show = false;
  }, timeout);
}

/* ---------------- STATE ---------------- */
const user = reactive({
  id: null,
  fullname: "",
  universityShort: "",
  universityFull: "",
  major: "",
  course: "",
  avatar: null,
});

const badges = ref([]);
const documents = ref([]);
const loading = ref(true);

const categories = [
    { key: "transcript", label: "Baholar (Transcript)" },
    { key: "article", label: "Ilmiy maqola" },
    { key: "thesis", label: "Tezis" },
    { key: "publication", label: "Boshqa nashr ishlari" },
    { key: "language_cert", label: "Til sertifikati" },
    { key: "ict_cert", label: "IT sertifikati" },
    { key: "history_cert", label: "Tarix fanidan natija" },
    { key: "conference", label: "Konferensiya" },
    { key: "recommendation", label: "Tavsiyanoma" },
];

function getDocsByCategory(catKey) {
  return documents.value.filter(d => d.type === catKey);
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

/* ---------------- COMPUTED ---------------- */

const socialScore = computed(() => {
  return badges.value.reduce((sum, b) => sum + Number(b.score || 0), 0);
});

const progressPercent = computed(() => {
  return Math.min((socialScore.value / 100) * 100, 100);
});

const initials = computed(() =>
  user.fullname
    ? user.fullname
      .split(" ")
      .map((w) => w[0])
      .slice(0, 2)
      .join("")
      .toUpperCase()
    : "?"
);

const fmt = (n) => Number(n || 0).toLocaleString();

/* ---------------- ACTIONS ---------------- */
function goToChat() {
  const userId = route.params.id;
  const myId = auth.user?.value?.id;

  if (!userId || !myId) return;

  if (String(userId) === String(myId)) {
    showToast("O‘zingizga xabar yubora olmaysiz 🙂", "error");
    return;
  }

  router.push({
    path: "/messenger",
    query: { user: userId },
  });
}

/* ---------------- API ---------------- */

async function loadProfile(userId) {
  loading.value = true;

  try {
    const res = await api.get(`/profiles/?user_id=${userId}`);
    const p = Array.isArray(res.data) ? res.data[0] : res.data;

    if (!p) return;

    user.id = p.user?.id || p.user_id || userId;
    user.fullname = p.full_name || "";
    user.universityShort = p.university_short || "";
    user.universityFull = p.university_full || "";
    user.major = p.major_name || p.major || "";
    user.course = p.course || "";
    
    let av = p.avatar || p.avatar_url || null;
    if (av && !av.startsWith("http")) {
      av = API_BASE_URL + av;
    }
    user.avatar = av;
  } catch (err) {
    console.error("loadProfile error", err);
  } finally {
    loading.value = false;
  }
}

async function loadBadges(userId) {
  try {
    const res = await api.get(`/social-achievements/`);
    badges.value = res.data
      .filter(
        (a) => String(a.user) === String(userId) && a.status === "approved"
      )
      .map((a) => ({
        id: a.id,
        title: a.sub_category || "Ijtimoiy faollik",
        score: Number(a.score || 0),
      }));
  } catch (err) {
    console.error("loadBadges error", err);
  }
}

async function loadDocuments(userId) {
  try {
     // Backendda documents filter by user bormi? Ha, /api/documents/?user_id=...
     const res = await api.get(`/documents/?user_id=${userId}`);
     documents.value = res.data.map(d => ({
        id: d.id,
        type: d.doc_type,
        label: d.meta?.title || "",
        meta: d.meta,
        fileUrl: d.file_url || d.file
     }));
  } catch (err) {
    console.error("loadDocuments error", err);
  }
}

/* ---------------- LIFECYCLE ---------------- */

onMounted(async () => {
  const uid = route.params.id;

  if (uid) {
    await loadProfile(uid);
    await loadBadges(uid);
    await loadDocuments(uid);
  }
});
</script>


