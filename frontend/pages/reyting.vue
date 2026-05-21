<template>
  <section class="leaderboard-page">
    <div class="card mb-4 shadow-sm border-0 rounded-4">
      <div class="card-body p-4">
        <div class="row g-3 align-items-end">
          <div class="col-md-3">
            <label class="form-label fw-bold small text-secondary">Universitet</label>
            <div class="filter-static border-2">Barchasi</div>
          </div>

          <div class="col-md-3">
            <label class="form-label fw-bold small text-secondary">Fakultet</label>
            <div class="custom-select">
              <div class="custom-trigger" @click.stop="toggleDropdown('faculty')">
                <span class="select-text">{{ selectedFacultyName }}</span>
                <i class="bi bi-chevron-down select-arrow"></i>
              </div>

              <div v-if="openDropdown === 'faculty'" class="custom-menu" @click.stop>
                <div class="custom-item" :class="{ active: !filters.faculty }" @click="selectFaculty('')">
                  Barchasi
                </div>

                <div v-for="f in availableFaculties" :key="f.id" class="custom-item"
                  :class="{ active: filters.faculty === f.id }" @click="selectFaculty(f.id)">
                  {{ f.name }}
                </div>
              </div>
            </div>
          </div>

          <div class="col-md-2">
            <label class="form-label fw-bold small text-secondary">Yo‘nalish</label>
            <div class="custom-select">
              <div class="custom-trigger" @click.stop="toggleDropdown('major')">
                <span class="select-text">{{ selectedMajorName }}</span>
                <i class="bi bi-chevron-down select-arrow"></i>
              </div>

              <div v-if="openDropdown === 'major'" class="custom-menu" @click.stop>
                <div class="custom-item" :class="{ active: !filters.major }" @click="selectMajor('')">
                  Barchasi
                </div>

                <div v-for="m in availableMajors" :key="m.id" class="custom-item"
                  :class="{ active: filters.major === m.id }" @click="selectMajor(m.id)">
                  {{ m.name }}
                </div>
              </div>
            </div>
          </div>

          <div class="col-md-2">
            <label class="form-label fw-bold small text-secondary">Bosqich</label>
            <div class="custom-select">
              <div class="custom-trigger" @click.stop="toggleDropdown('course')">
                <span class="select-text">{{ selectedCourseName }}</span>
                <i class="bi bi-chevron-down select-arrow"></i>
              </div>

              <div v-if="openDropdown === 'course'" class="custom-menu" @click.stop>
                <div class="custom-item" :class="{ active: !filters.course }" @click="selectCourse('')">
                  Barchasi
                </div>

                <div v-for="c in availableCourses" :key="c" class="custom-item"
                  :class="{ active: filters.course === c }" @click="selectCourse(c)">
                  {{ c }}-bosqich
                </div>
              </div>
            </div>
          </div>

          <div class="col-md-2">
            <label class="form-label fw-bold small text-secondary">Guruh</label>
            <div class="custom-select">
              <div class="custom-trigger" @click.stop="toggleDropdown('group')">
                <span class="select-text">{{ selectedGroupName }}</span>
                <i class="bi bi-chevron-down select-arrow"></i>
              </div>

              <div v-if="openDropdown === 'group'" class="custom-menu" @click.stop>
                <div class="custom-item" :class="{ active: !filters.group }" @click="selectGroup('')">
                  Barchasi
                </div>

                <div v-for="g in availableGroups" :key="g" class="custom-item" :class="{ active: filters.group === g }"
                  @click="selectGroup(g)">
                  {{ g }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="hero-card mb-4 shadow border-0 position-relative theme-hero-card">
      <div class="hero-inner position-relative z-1">
        <h1 class="hero-title">Hujjatlar Reytingi</h1>
        <p class="hero-sub">
          Talabalarning taqdim etgan akademik va ilmiy hujjatlari (100 ballik tizim) bo'yicha
          o'rinlari
        </p>

        <div class="top-strip">
          <div v-for="(t, i) in visuallyTop3" :key="i" class="top-avatar-wrap" :class="{ 'is-first': i === 0 }">
            <div class="ava-outer">
              <div class="ava-mask shadow">
                <img v-if="t.avatar" :src="t.avatar" class="ava-img" alt="avatar" />
                <div v-else class="ava-initials">{{ t.initials }}</div>
              </div>
              <div v-if="t.badge" class="ava-badge">{{ t.badge }}</div>
            </div>

            <NuxtLink :to="`/users/${t.user_id}`" class="text-decoration-none text-white">
              <div class="ava-name mt-2 fs-5">{{ t.displayName }}</div>
            </NuxtLink>

            <div class="ava-meta">
              <span class="xp-pill">⚡ {{ t.socialScore }} ball</span>
            </div>
          </div>
        </div>
      </div>
      <div class="hero-decoration position-absolute top-0 end-0 h-100 p-4 opacity-100">
        <!-- <i class="bi bi-trophy-fill display-1 text-white"></i> -->
        <img src="public/images/trophy.png" class="trophy-img" alt="trophy"
          style="position: absolute; top: 0.2rem; right: 2rem" />
      </div>
    </div>

    <div class="card shadow-sm border-0 rounded-4 overflow-hidden">
      <div class="card-header bg-transparent py-3 border-0">
        <h5 class="mb-0 fw-bold">Barcha talabalar reytingi</h5>
      </div>
      <ul class="list-group list-group-flush">
        <li v-for="(u, idx) in paginatedRest" :key="u.user_id"
          class="list-group-item py-3 d-flex justify-content-between align-items-center border-bottom border-light shadow-hover">
          <div class="d-flex align-items-center gap-3">
            <div class="rank-num shadow-sm">#{{ globalRankForRow(idx) }}</div>

            <div class="ava small shadow-sm border-2">
              <img v-if="u.avatar" :src="u.avatar" class="ava-img" />
              <span v-else>{{ u.initials }}</span>
            </div>

            <div>
              <NuxtLink :to="`/users/${u.user_id}`" class="text-decoration-none text-main">
                <div class="fw-bold fs-6">{{ u.displayName }}</div>
                <div class="small text-secondary">
                  {{ u.faculty_name }} • {{ u.major_name }}
                </div>
              </NuxtLink>
            </div>
          </div>

          <div class="d-flex gap-3 align-items-center">
            <div class="text-end">
              <div class="ava-meta me-3">
                <!-- <span class="xp-pill">⚡ {{ formatNumber(t.xp) }}</span> -->
                <span class="level-pill text-warning">⚡{{ u.socialScore }} ball</span>
              </div>
            </div>
          </div>
        </li>
      </ul>

      <div class="card-footer bg-transparent border-0 py-4 d-flex justify-content-center">
        <nav v-if="restProfiles.length > PAGE_SIZE">
          <ul class="pagination pagination-sm gap-2 border-0">
            <li class="page-item" :class="{ disabled: currentPage === 1 }">
              <button class="page-link rounded-pill border-0 shadow-sm px-3" @click="currentPage--">
                Oldingi
              </button>
            </li>
            <li class="page-item" :class="{
              disabled: currentPage * PAGE_SIZE >= restProfiles.length,
            }">
              <button class="page-link rounded-pill border-0 shadow-sm px-3" @click="currentPage++">
                Keyingi
              </button>
            </li>
          </ul>
        </nav>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import useAuth from "@/composables/useAuth";
import useApi from "@/composables/useApi";

const PAGE_SIZE = 10;
const auth = useAuth();
const api = useApi();
const config = useRuntimeConfig();
const API_BASE_URL = config.public.apiUrl.replace(/\/api$/, "");

const profiles = ref([]);
const achievements = ref([]);
const filters = ref({
  faculty: "",
  major: "",
  course: "",
  group: "",
});

const facultiesList = ref([]);
const majorsList = ref([]);

async function loadInitialData() {
  try {
    // 1. Fakultetlar va Yo'nalishlarni yuklash (Filterlar uchun)
    const [facs, majs, profs, achs] = await Promise.all([
      api.get("/faculties/"),
      api.get("/majors/"),
      api.get("/profiles/"),
      api.get("/social-achievements/"), // Barcha tasdiqlangan yutuqlarni olamiz
    ]);

    facultiesList.value = facs.data;
    majorsList.value = majs.data;
    achievements.value = achs.data;

    // 2. Profillarni qayta ishlash
    profiles.value = profs.data.map((p) => {
      const name = p.full_name || p.user?.username || "Foydalanuvchi";

      let av = p.avatar_url || p.avatar || "";
      if (av && !av.startsWith("http")) {
        av = API_BASE_URL + av;
      }

      return {
        user_id: p.user?.id,
        displayName: name,
        socialScore: parseFloat(p.xp || 0), // Backenddan tayyor hisoblangan XP ni olamiz
        avatar: av,
        faculty: p.faculty,
        faculty_name: p.faculty_name,
        major: p.major,
        major_name: p.major_name,
        course: p.course,
        group: p.group,
        initials: name
          .split(" ")
          .map((w) => w[0])
          .slice(0, 2)
          .join("")
          .toUpperCase(),
      };
    });
  } catch (err) {
    console.error("Ma'lumotlarni yuklashda xato:", err);
  }
}

const filteredProfiles = computed(() => {
  return profiles.value
    .filter((p) => {
      return (
        (!filters.value.faculty || p.faculty === filters.value.faculty) &&
        (!filters.value.major || p.major === filters.value.major) &&
        (!filters.value.course ||
          String(p.course) === String(filters.value.course)) &&
        (!filters.value.group || p.group === filters.value.group)
      );
    })
    .sort((a, b) => b.socialScore - a.socialScore); // Reyting asosi: Ijtimoiy ball
});

const visuallyTop3 = computed(() => {
  const top = filteredProfiles.value.slice(0, 3);
  // Shohsupa tartibi: [2-o'rin, 1-o'rin, 3-o'rin]
  const ordered = [];
  if (top[0]) ordered.push({ ...top[0], badge: "🥇" });
  if (top[1]) ordered.push({ ...top[1], badge: "🥈" });
  if (top[2]) ordered.push({ ...top[2], badge: "🥉" });
  return ordered;
});

const restProfiles = computed(() => filteredProfiles.value.slice(3));
const currentPage = ref(1);
const paginatedRest = computed(() =>
  restProfiles.value.slice(
    (currentPage.value - 1) * PAGE_SIZE,
    currentPage.value * PAGE_SIZE
  )
);

function globalRankForRow(idx) {
  return 3 + (currentPage.value - 1) * PAGE_SIZE + idx + 1;
}

// FILTERS DYNAMICS
const availableFaculties = computed(() => facultiesList.value);
const availableMajors = computed(() => {
  if (!filters.value.faculty) return majorsList.value;
  return majorsList.value.filter((m) => m.faculty === filters.value.faculty);
});
const availableCourses = computed(() => [
  ...new Set(
    profiles.value
      .filter(
        (p) =>
          (!filters.value.faculty || p.faculty === filters.value.faculty) &&
          (!filters.value.major || p.major === filters.value.major)
      )
      .map((p) => p.course)
      .filter(Boolean)
  ),
]);
const availableGroups = computed(() => [
  ...new Set(
    profiles.value
      .filter(
        (p) =>
          (!filters.value.faculty || p.faculty === filters.value.faculty) &&
          (!filters.value.major || p.major === filters.value.major) &&
          (!filters.value.course ||
            String(p.course) === String(filters.value.course))
      )
      .map((p) => p.group)
      .filter(Boolean)
  ),
]);

onMounted(() => {
  loadInitialData()
  if (process.client) {
    window.addEventListener('click', () => {
      openDropdown.value = null
    })
  }
});

const openDropdown = ref(null)

function toggleDropdown(name) {
  if (openDropdown.value === name) {
    openDropdown.value = null
  } else {
    openDropdown.value = name
  }
}


const selectedFacultyName = computed(() => {
  if (!filters.value.faculty) return "Barchasi"

  const f = facultiesList.value.find(
    (x) => x.id === filters.value.faculty
  )

  return f ? f.name : "Barchasi"
})

const selectedMajorName = computed(() => {
  if (!filters.value.major) return "Barchasi"
  const m = majorsList.value.find(x => x.id === filters.value.major)
  return m ? m.name : "Barchasi"
})

const selectedCourseName = computed(() => {
  if (!filters.value.course) return "Barchasi"
  return filters.value.course + "-bosqich"
})

const selectedGroupName = computed(() => {
  if (!filters.value.group) return "Barchasi"
  return filters.value.group
})

function selectFaculty(id) {
  filters.value.faculty = id
  openDropdown.value = null
}

function selectMajor(id) {
  filters.value.major = id
  openDropdown.value = null
}

function selectCourse(c) {
  filters.value.course = c
  openDropdown.value = null
}

function selectGroup(g) {
  filters.value.group = g
  openDropdown.value = null
}
</script>
