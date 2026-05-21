<template>
  <div class="profile-page min-vh-100">
    <div class="row g-3">

      
      <div class="col-lg-3">
        <div class="glass-card card border-0 shadow-sm h-100 p-3 theme-card">
          <div class="d-flex align-items-center gap-3">
            <div :class="['ava-circle', 'sm']">
              <img v-if="profile.avatar" :src="profile.avatar" alt="avatar" class="mini-avatar" />
              <span v-else class="initials">{{ initials }}</span>
            </div>
            <div class="flex-grow-1">
              <div class="fw-semibold profile-texts">{{ profile.fullname }}</div>
              <div class="small profile-texts">{{ profile.university_short }}</div>
            </div>
          </div>

          <!-- XP and Level removed -->

          <div class="mt-3 d-grid">
            <button class="btn btn-outline-danger" @click="removeAvatar">
              Profil rasmini o'chirish
            </button>
          </div>
        </div>
      </div>


      <div class="col-lg-9">
        <div class="glass-card card border-0 shadow-sm p-4 position-relative theme-card">
          <button class="btn-bg position-absolute top-3 end-3 rounded-3" style="right: 1.4rem" @click="openEditProfile">
            Profilni tahrirlash
          </button>

          <div class="d-flex align-items-center gap-4">
            <div class="ava-circle xl">
              <img v-if="profile.avatar" :src="profile.avatar" alt="avatar" class="profilavatar" />
              <span v-else class="initials">{{ initials }}</span>
            </div>

            <div class="flex-grow-1">
                <h1 class="mb-1 profile-texts fw-bold">{{ profile.fullname }}</h1>
                <div class="profile-texts text-secondary mb-2">
                {{ profile.university_full }} <span class="mx-1">•</span>
                {{ profile.faculty_name }} <span class="mx-1">•</span> 
                {{ profile.major_name }} <span class="mx-1">•</span> <i class="bi bi-mortarboard"></i> {{ profile.course }}-kurs
              </div>
              <div class="d-flex flex-wrap align-items-center gap-4 mt-3">
                <!-- XP stats removed -->
              </div>
            </div>
          </div>
        </div>


      </div>
    </div>


    <Teleport to="body">
    <div class="modal fade" id="editProfileModal" tabindex="-1" aria-hidden="true" ref="editProfileModalRef">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Profilni tahrirlash</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Yopish"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">To'liq ism familiya</label>
              <input v-model="editProfileForm.fullname" type="text" class="form-control" />
            </div>

            <div class="mb-3">
              <label class="form-label">Universitet (Qisqa)</label>
              <input v-model="editProfileForm.universityShort" type="text" class="form-control" />
            </div>

            <div class="mb-3">
              <label class="form-label">Universitet (To'liq)</label>
              <input v-model="editProfileForm.universityFull" type="text" class="form-control" />
            </div>

            <div class="mb-3">
              <label class="form-label">Fakultet</label>

              <div class="custom-select">
                <div class="custom-select-trigger" @click="toggleDropdown('faculty')">
                  {{ editProfileForm.faculty_name || "Fakultetni tanlang" }}
                  <span class="arrow">▾</span>
                </div>

                <div v-if="openDropdown === 'faculty'" class="custom-select-menu">
                  <div v-for="f in faculties" :key="f.id" class="custom-option" @click="selectOption('faculty', f)">
                    {{ f.name }}
                  </div>
                </div>
              </div>
            </div>

            <div class="mb-3">
              <label class="form-label">Yo‘nalish</label>

              <div class="custom-select">
                <div class="custom-select-trigger" @click="toggleDropdown('major')">
                  {{ editProfileForm.major_name || "Yo‘nalishni tanlang" }}
                  <span class="arrow">▾</span>
                </div>

                <div v-if="openDropdown === 'major'" class="custom-select-menu">
                  <div v-for="m in availableMajors" :key="m.id" class="custom-option" @click="selectOption('major', m)">
                    {{ m.name }}
                  </div>

                  <div v-if="availableMajors.length === 0" class="custom-option text-muted">
                    Avval fakultetni tanlang
                  </div>
                </div>
              </div>
            </div>

            <div class="mb-3">
              <label class="form-label">Bosqich (kurs)</label>

              <div class="custom-select">
                <div class="custom-select-trigger" @click="toggleDropdown('course')">
                  {{
                    editProfileForm.course
                      ? editProfileForm.course + "-kurs"
                      : "Bosqichni tanlang"
                  }}
                  <span class="arrow">▾</span>
                </div>

                <div v-if="openDropdown === 'course'" class="custom-select-menu">
                  <div v-for="c in courses" :key="c" class="custom-option" @click="selectOption('course', c)">
                    {{ c }}-kurs
                  </div>
                </div>
              </div>
            </div>

            <div class="mb-3">
              <label class="form-label">Guruh</label>
              <input v-model="editProfileForm.group" type="text" class="form-control" placeholder="Masalan: 23-05" />
            </div>

            <div class="mb-3">
              <label class="form-label">Profil rasm (jpg/png)</label>
              <input type="file" class="form-control" accept="image/*" @change="onAvatarSelected" />
            </div>

            <div v-if="profile.avatar" class="text-center mb-3">
              <img :src="profile.avatar" alt="preview" class="preview-avatar" />
              <div class="mt-2">
                <button class="btn btn-sm btn-danger" @click="removeAvatar">
                  O'chirish
                </button>
              </div>
            </div>
          </div>

          <div class="modal-footer border-0">
            <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">
              Bekor qilish
            </button>
            <button type="button" class="btn btn-yutuq" @click="saveProfile">
              Saqlash
            </button>
          </div>
        </div>
      </div>
    </div>
    </Teleport>


    <Achievements />
  </div>
</template>

<script setup>

import { ref, reactive, computed, onMounted, watch } from "vue";
import { useRouter, useRoute } from "#app";
import useAuth from "@/composables/useAuth";
import useApi from "@/composables/useApi";
import Achievements from "@/components/achievements.vue";

const XP_PER_LEVEL = 100;
const MAX_LEVEL = 100;
const MAX_TOTAL_XP = XP_PER_LEVEL * MAX_LEVEL;
const auth = useAuth();
const api = useApi();
const router = useRouter();
const route = useRoute();
const config = useRuntimeConfig();
const API_BASE_URL = config.public.apiUrl.replace(/\/api$/, "");

const { profile, loadProfile, updateProfile } = useUserProfile();

const openDropdown = ref(null);

function toggleDropdown(name) {
  openDropdown.value = openDropdown.value === name ? null : name;
}

function selectOption(name, item) {
  if (name === "faculty") {
    editProfileForm.faculty = item.id;
    editProfileForm.faculty_name = item.name;
    editProfileForm.major = null;
    editProfileForm.major_name = "";
    fetchMajors(item.id);
  } else if (name === "major") {
    editProfileForm.major = item.id;
    editProfileForm.major_name = item.name;
  } else {
    editProfileForm[name] = item;
  }
  openDropdown.value = null;
}

const initials = computed(() =>
  (profile.fullname || "")
    .split(" ")
    .map((w) => w[0] || "")
    .slice(0, 2)
    .join("")
    .toUpperCase()
);

const faculties = ref([]);
const availableMajors = ref([]);

async function fetchFaculties() {
  try {
    const resp = await api.get("/faculties/");
    faculties.value = resp.data;
  } catch (err) {
    console.error("Fakultetlarni yuklashda xato:", err);
  }
}

async function fetchMajors(facultyId) {
  if (!facultyId) {
    availableMajors.value = [];
    return;
  }
  try {
    const resp = await api.get(`/majors/?faculty_id=${facultyId}`);
    availableMajors.value = resp.data;
  } catch (err) {
    console.error("Yo'nalishlarni yuklashda xato:", err);
  }
}

const courses = [1, 2, 3, 4, 5];

const editProfileModalRef = ref(null);
let bsEditModal = null;
const editProfileForm = reactive({
  fullname: "",
  universityShort: "",
  universityFull: "",
  major: "",
  faculty: "",
  faculty_name: "",
  major_name: "",
  course: "",
  group: "",
  avatarFile: null,
  resetAvatar: false,
});

function openEditProfile() {
  editProfileForm.fullname = profile.fullname || "";
  editProfileForm.universityShort = profile.university_short || "";
  editProfileForm.universityFull = profile.university_full || "";
  editProfileForm.faculty = profile.faculty_id;
  editProfileForm.faculty_name = profile.faculty_name;
  editProfileForm.major = profile.major_id;
  editProfileForm.major_name = profile.major_name;
  if (profile.faculty_id) {
    fetchMajors(profile.faculty_id);
  }
  editProfileForm.course = profile.course || "";
  editProfileForm.group = profile.group || "";
  editProfileForm.avatarFile = null;
  editProfileForm.resetAvatar = false;
  if (bsEditModal) bsEditModal.show();
}

function onAvatarSelected(e) {
  const f = e.target.files && e.target.files[0];
  if (!f) return;
  editProfileForm.avatarFile = f;
}

async function removeAvatar() {
  if (!confirm("Profil rasmini o'chirishni tasdiqlaysizmi?")) return;
  await updateProfile({ removeAvatar: true });
}

async function saveProfile() {
  if (!editProfileForm.fullname || !editProfileForm.fullname.trim()) {
    alert("To'liq ism kiriting");
    return;
  }

  try {
    await updateProfile({
      fullname: editProfileForm.fullname,
      university_short: editProfileForm.universityShort,
      university_full: editProfileForm.universityFull,
      faculty: editProfileForm.faculty,
      major: editProfileForm.major,
      course: editProfileForm.course,
      group: editProfileForm.group,
      avatarFile: editProfileForm.avatarFile,
    });
    
    if (bsEditModal) bsEditModal.hide();
  } catch (e) {
    console.error("saveProfile exception:", e);
    alert("Profilni saqlashda xato");
  }
}

watch(
  () => editProfileForm.faculty,
  () => {
    // Only reset major if we are explicitly changing faculty in form
  }
);

onMounted(async () => {
  if (typeof window === "undefined") return;
  const { Modal } = await import("bootstrap");
  if (editProfileModalRef.value)
    bsEditModal = new Modal(editProfileModalRef.value);

  if (auth.user?.value?.id) {
    await loadProfile();
  }
  await fetchFaculties();
});

watch(
  () => auth.user?.value?.id,
  async (id) => {
    if (id) {
      await loadProfile();
    }
  }
);

</script>
