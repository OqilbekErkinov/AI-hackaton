<template>
  <div class="navprofile-container" ref="wrap">
    <!-- Unauthenticated State -->
    <div v-if="!isAuthenticated" class="auth-group">
      <NuxtLink to="/signin" class="nav-btn-outline me-2">Kirish</NuxtLink>
      <NuxtLink to="/signup" class="nav-btn-primary">Ro'yxatdan o'tish</NuxtLink>
    </div>

    <!-- Authenticated State -->
    <div v-else class="authenticated-zone">
      <button
        class="profile-bubble"
        @click="toggle"
        ref="btn"
        :class="{ active: open }"
      >
        <img :src="profile.avatar || defaultAvatar" alt="avatar" class="bubble-img" />
        <div class="online-status"></div>
      </button>

      <transition name="panel-pop">
        <div v-if="open" class="premium-panel shadow-lg" ref="panel">
          <!-- Glassmorphism Header -->
          <div class="panel-hero">
            <div class="hero-bg"></div>
            <button class="btn-close-minimal" @click="open = false">
              <i class="bi bi-x-lg"></i>
            </button>
            
            <div class="user-meta">
              <div class="avatar-giant">
                <img :src="profile.avatar || defaultAvatar" alt="avatar" />
              </div>
              <div class="user-info">
                <h3 class="name">{{ profile.fullname || "Talaba" }}</h3>
                <p class="email">{{ userEmail }}</p>
                <div class="phone" v-if="profile.phoneDisplay">
                  <i class="bi bi-phone"></i> {{ profile.phoneDisplay }}
                </div>
              </div>
            </div>
          </div>

          <!-- Content Area -->
          <div class="panel-main">
            <!-- Universal Navigation -->
            <div class="nav-segmented">
              <button :class="{ active: tab === 'settings' }" @click="tab = 'settings'">
                <i class="bi bi-sliders2"></i> <span>Sozlamalar</span>
              </button>
              <button :class="{ active: tab === 'theme' }" @click="tab = 'theme'">
                <i class="bi bi-moon-stars"></i> <span>Mavzu</span>
              </button>
              <button :class="{ active: tab === 'lang' }" @click="tab = 'lang'">
                <i class="bi bi-translate"></i> <span>Til</span>
              </button>
            </div>

            <div class="scroll-content">
              <!-- Settings Section -->
              <div v-if="tab === 'settings'" class="section-fade">
                <form @submit.prevent="saveProfile" class="modern-form">
                  <div class="input-card">
                    <label>To'liq ism</label>
                    <input v-model="form.fullname" placeholder="F.I.SH" />
                  </div>
                  <div class="input-card">
                    <label>Telefon</label>
                    <input v-model="form.phone" placeholder="+998" />
                  </div>
                  <div class="input-card disabled">
                    <label>Email (O'zgartirib bo'lmaydi)</label>
                    <input v-model="form.email" disabled />
                  </div>
                  <div class="file-upload-card">
                    <input type="file" id="p-avatar" class="d-none" @change="onAvatarSelected" accept="image/*" />
                    <label for="p-avatar" class="upload-area">
                      <i class="bi bi-camera"></i>
                      <span>Rasm yuklash</span>
                    </label>
                    <button v-if="profile.avatar" type="button" class="btn-del" @click="resetProfileImage">
                      <i class="bi bi-trash"></i>
                    </button>
                  </div>
                  <button type="submit" class="btn-save" :disabled="loading">
                    <span v-if="!loading">O'zgarishlarni saqlash</span>
                    <span v-else class="spinner-border spinner-border-sm"></span>
                  </button>
                </form>
              </div>

              <!-- Theme Section -->
              <div v-if="tab === 'theme'" class="section-fade">
                <p class="section-desc">Interfeys ko'rinishini boshqarish</p>
                <div class="theme-grid">
                  <button class="tg-item" :class="{ active: mode === 'light' }" @click="setTheme('light')">
                    <div class="tg-preview light">
                      <div class="dot accent"></div>
                    </div>
                    <span>Yorug'</span>
                    <i class="bi bi-check-circle-fill icon-check"></i>
                  </button>
                  <button class="tg-item" :class="{ active: mode === 'dark' }" @click="setTheme('dark')">
                    <div class="tg-preview dark">
                      <div class="dot accent"></div>
                    </div>
                    <span>Qorong'u</span>
                    <i class="bi bi-check-circle-fill icon-check"></i>
                  </button>
                  <button class="tg-item" :class="{ active: mode === 'auto' }" @click="setTheme('auto')">
                    <div class="tg-preview auto"></div>
                    <span>Tizim</span>
                    <i class="bi bi-check-circle-fill icon-check"></i>
                  </button>
                </div>
              </div>

              <!-- Language Section -->
              <div v-if="tab === 'lang'" class="section-fade">
                <p class="section-desc">Platforma tilini tanlang</p>
                <div class="lang-grid">
                  <button v-for="l in ['uz', 'ru', 'en']" :key="l" 
                    class="lg-item" :class="{ active: lang === l }" @click="lang = l">
                    <span class="flag-icon">{{ l === 'uz' ? '🇺🇿' : l === 'ru' ? '🇷🇺' : '🇺🇸' }}</span>
                    <span class="lang-name">{{ l === 'uz' ? 'O\'zbekcha' : l === 'ru' ? 'Русский' : 'English' }}</span>
                    <i class="bi bi-check2"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Bottom Actions -->
          <div class="panel-foot">
            <NuxtLink to="/profile" class="foot-btn" @click="open = false">
              <i class="bi bi-person-bounding-box"></i>
              <span>Mening profilim</span>
            </NuxtLink>
            <button class="foot-btn logout" @click="logoutHandler">
              <i class="bi bi-power"></i>
              <span>Chiqish</span>
            </button>
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onBeforeUnmount, watch, computed } from "vue";
import { useRouter } from "vue-router";
import useAuth from "@/composables/useAuth";
import useUserProfile from "@/composables/useUserProfile";
import useColorTheme from "@/composables/useColorTheme";

const defaultAvatar = "/images/default-avatar.png";
const open = ref(false);
const tab = ref("settings");
const lang = ref("uz");
const wrap = ref(null);
const loading = ref(false);

const auth = useAuth();
const router = useRouter();
const { profile, loadProfile, updateProfile, clearProfile } = useUserProfile();
const { mode, setTheme } = useColorTheme();

/* form */
const form = reactive({ fullname: "", phone: "", email: "", avatarFile: null });

/* computed */
const isAuthenticated = computed(() => !!auth.user?.value?.id);
const userEmail = computed(() => auth.user?.value?.email || "");

watch(() => profile, () => {
  form.fullname = profile.fullname || "";
  form.phone = profile.phone || "";
  form.email = profile.email || auth.user?.value?.email || "";
}, { deep: true, immediate: true });

function toggle() { if (!isAuthenticated.value) return; open.value = !open.value; }
function onDocClick(e) { if (!open.value) return; if (wrap.value && !wrap.value.contains(e.target)) open.value = false; }
function onAvatarSelected(e) { const f = e.target.files?.[0]; if (f) { form.avatarFile = f; saveProfile(); } }

async function saveProfile() {
  loading.value = true;
  try {
    await updateProfile({ fullname: form.fullname, phone: form.phone, email: form.email, avatarFile: form.avatarFile });
    form.avatarFile = null;
  } finally { loading.value = false; }
}

async function resetProfileImage() { if (confirm("O'chirishni tasdiqlaysizmi?")) await updateProfile({ removeAvatar: true }); }
async function logoutHandler() { open.value = false; await auth.logout(); clearProfile(); router.push("/signin"); }

onMounted(async () => {
  document.addEventListener("click", onDocClick);
  if (auth.user?.value?.id) await loadProfile();
});
onBeforeUnmount(() => document.removeEventListener("click", onDocClick));
</script>

<style scoped>
.navprofile-container { 
  display: flex; 
  align-items: center; 
  font-family: 'Outfit', sans-serif;
  user-select: none;
}

/* Bubble Trigger */
.profile-bubble {
  width: 44px; height: 44px;
  border-radius: 50%;
  padding: 3px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  position: relative;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
.profile-bubble:hover, .profile-bubble.active {
  border-color: var(--primary);
  transform: scale(1.05);
  box-shadow: 0 0 15px rgba(var(--primary-rgb), 0.2);
}
.bubble-img { width: 100%; height: 100%; object-fit: cover; border-radius: 50%; }
.online-status {
  position: absolute; bottom: 0; right: 0;
  width: 12px; height: 12px;
  background: #10b981;
  border: 2px solid var(--bg-card);
  border-radius: 50%;
}

/* Premium Panel */
.premium-panel {
  position: absolute; right: -5px; top: 60px;
  width: 380px;
  max-height: 520px;
  background: var(--bg-glass);
  backdrop-filter: var(--glass-blur);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  overflow-y: auto;
  z-index: 10000;
  display: flex; flex-direction: column;
}

/* Premium Panel Scrollbar */
.premium-panel::-webkit-scrollbar {
  width: 4px;
}
.premium-panel::-webkit-scrollbar-track {
  background: transparent;
}
.premium-panel::-webkit-scrollbar-thumb {
  background: var(--divider-color);
  border-radius: 10px;
}
.premium-panel::-webkit-scrollbar-thumb:hover {
  background: var(--primary-light);
}

/* Panel Hero Header */
.panel-hero {
  height: 180px; position: relative;
  padding: 24px;
  display: flex; align-items: flex-end;
  border-bottom: 1px solid var(--divider-color);
}
.hero-bg {
  position: absolute; inset: 0;
  background: linear-gradient(135deg, var(--primary), var(--primary-light));
  opacity: 0.85;
  clip-path: polygon(0 0, 100% 0, 100% 85%, 0 100%);
}
.btn-close-minimal {
  position: absolute; top: 15px; right: 15px;
  background: rgba(255, 255, 255, 0.2);
  border: none; color: #fff;
  width: 34px; height: 34px;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  z-index: 10; cursor: pointer;
  transition: 0.3s;
}
.btn-close-minimal:hover { background: rgba(225, 29, 72, 0.8); }

.user-meta { display: flex; align-items: center; gap: 15px; z-index: 5; }
.avatar-giant {
  width: 72px; height: 72px;
  border-radius: var(--radius-md);
  padding: 4px; background: #fff;
  box-shadow: var(--shadow-md);
}
.avatar-giant img { width: 100%; height: 100%; border-radius: calc(var(--radius-md) - 4px); object-fit: cover; }

.user-info .name { font-size: 1.15rem; font-weight: 700; color: #fff; margin: 0; }
.user-info .email { font-size: 0.8rem; color: rgba(255, 255, 255, 0.8); margin: 2px 0; }
.user-info .phone { font-size: 0.75rem; color: #fff; font-weight: 600; opacity: 0.9; }

/* Navigation Tab Bar */
.nav-segmented {
  display: flex; background: var(--bg-app);
  margin: 15px 24px; padding: 5px;
  border-radius: var(--radius-md);
  gap: 5px;
}
.nav-segmented button {
  flex: 1; border: none; background: transparent;
  padding: 10px; border-radius: calc(var(--radius-md) - 4px);
  display: flex; align-items: center; justify-content: center; gap: 8px;
  font-size: 0.85rem; font-weight: 600; color: var(--text-secondary);
  transition: 0.3s;
}
.nav-segmented button.active {
  background: var(--bg-card);
  color: var(--text-main);
  box-shadow: var(--shadow-sm);
}

/* Content Area */
.panel-main { 
  flex: 1; 
}
.scroll-content { 
  padding: 0 24px 20px; 
}

.section-fade { animation: fadeIn 0.4s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

/* Forms & Inputs */
.modern-form { display: flex; flex-direction: column; gap: 12px; }
.input-card { background: var(--bg-app); padding: 10px 15px; border-radius: var(--radius-md); }
.input-card label { display: block; font-size: 0.75rem; color: var(--text-muted); font-weight: 700; margin-bottom: 2px; }
.input-card input { width: 100%; border: none; background: transparent; font-size: 0.9rem; color: var(--text-main); font-weight: 600; outline: none; }
.input-card.disabled { opacity: 0.6; }

.file-upload-card { display: flex; gap: 10px; }
.upload-area {
  flex: 1; background: var(--bg-app); border: 2px dashed var(--border-color);
  padding: 12px; border-radius: var(--radius-md);
  display: flex; align-items: center; justify-content: center; gap: 10px;
  cursor: pointer; color: var(--text-secondary); transition: 0.3s;
}
.upload-area:hover { border-color: var(--primary); color: var(--primary); }
.btn-del {
  width: 46px; border-radius: var(--radius-md); border: none;
  background: rgba(var(--error), 0.1); color: var(--error);
}

.btn-save {
  margin-top: 10px; padding: 14px; border-radius: var(--radius-md);
  background: var(--primary); color: #fff; font-weight: 700; border: none;
  transition: 0.3s;
}
.btn-save:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(var(--primary-rgb), 0.3); }

/* Theme Grid */
.section-desc { font-size: 0.8rem; color: var(--text-muted); margin-bottom: 15px; }
.theme-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; }
.tg-item {
  border: 1px solid var(--border-color); background: var(--bg-card);
  border-radius: var(--radius-md); padding: 12px;
  display: flex; flex-direction: column; align-items: center; gap: 10px;
  transition: 0.3s; position: relative; cursor: pointer;
}
.tg-item.active { border-color: var(--primary); box-shadow: var(--shadow-sm); }
.tg-preview { width: 44px; height: 44px; border-radius: 50%; position: relative; border: 1px solid var(--border-color); }
.tg-preview.light { background: #fff; }
.tg-preview.dark { background: #0f172a; }
.tg-preview.auto { background: linear-gradient(135deg, #fff 50%, #0f172a 50%); }
.dot { position: absolute; inset: 10px; border-radius: 50%; display: none; }
.tg-item.active .dot { display: block; border: 3px solid var(--primary); }

.tg-item span { font-size: 0.8rem; font-weight: 600; color: var(--text-main); }
.icon-check { position: absolute; top: 6px; right: 6px; color: var(--primary); font-size: 0.9rem; opacity: 0; }
.tg-item.active .icon-check { opacity: 1; }

/* Language Grid */
.lang-grid { display: flex; flex-direction: column; gap: 8px; }
.lg-item {
  display: flex; align-items: center; gap: 12px; padding: 14px 18px;
  background: var(--bg-app); border: 1px solid transparent; border-radius: var(--radius-md);
  transition: 0.3s; cursor: pointer;
}
.lg-item:hover { border-color: var(--primary); }
.lg-item.active { background: var(--bg-card); border-color: var(--primary); }
.flag-icon { font-size: 1.2rem; }
.lang-name { flex: 1; text-align: left; font-size: 0.9rem; font-weight: 600; color: var(--text-main); }
.lg-item i { opacity: 0; color: var(--primary); }
.lg-item.active i { opacity: 1; }

/* Footer Actions */
.panel-foot {
  padding: 15px 24px 24px; background: var(--bg-app);
  display: flex; flex-direction: column; gap: 10px;
}
.foot-btn {
  display: flex; align-items: center; gap: 12px;
  padding: 14px; border-radius: var(--radius-md);
  background: var(--bg-card); color: var(--text-main);
  text-decoration: none; font-size: 0.9rem; font-weight: 600;
  transition: 0.3s; border: none;
}
.foot-btn:hover { background: var(--primary); color: #fff; transform: translateX(5px); }
.foot-btn.logout { background: rgba(225, 29, 72, 0.05); color: var(--error); }
.foot-btn.logout:hover { background: var(--error); color: #fff; }

/* Transitions */
.panel-pop-enter-active, .panel-pop-leave-active { transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1); }
.panel-pop-enter-from, .panel-pop-leave-to { opacity: 0; transform: translateY(20px) scale(0.95); }

/* Auth Toggle */
.nav-btn-outline {
  padding: 8px 18px; border-radius: var(--radius-md); border: 1.5px solid var(--primary);
  color: var(--primary); font-weight: 700; text-decoration: none; transition: 0.3s;
}
.nav-btn-primary {
  padding: 8px 18px; border-radius: var(--radius-md); background: var(--primary);
  color: #fff; font-weight: 700; text-decoration: none; transition: 0.3s;
}
</style>
