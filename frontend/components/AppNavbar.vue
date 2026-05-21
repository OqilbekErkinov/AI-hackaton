<template>
  <nav class="navbar navbar-expand sticky-top">
    <div class="container-fluid px-3">
      <!-- Left: burger + breadcrumb -->
      <div class="d-flex align-items-center gap-2">
        <button
          class="btn btn-outline-secondary d-flex align-items-center justify-content-center"
          type="button"
          aria-label="Sidebar"
          @click="$emit('toggle-sidebar')"
        >
          <i class="bi bi-list fs-5"></i>
        </button>

        <nav aria-label="breadcrumb">
          <ol class="breadcrumb mb-0">
            <li class="breadcrumb-item">
              <NuxtLink to="/" class="text-decoration-none fw-semibold brand d-flex align-items-center gap-2">
              <!-- <img src="/images/logo.png" alt="Nexora" style="height: 32px; width: auto;" /> -->
              <span>Nexora</span>
            </NuxtLink>
            </li>
            <li class="breadcrumb-item active" aria-current="page">
              {{ routeName }}
            </li>
          </ol>
        </nav>
      </div>

      <!-- Right: icons + profile -->
      <!-- Right: AI Tools + profile -->
      <div class="d-flex align-items-center gap-2">
        <!-- AI Assistant -->
        <NuxtLink 
          to="/ai-assistant" 
          class="icon-btn" 
          active-class="active"
          aria-label="AI Yordamchi" 
          title="AI Yordamchi"
        >
          <i class="bi bi-robot"></i>
        </NuxtLink>

        <!-- AI Mentor -->
        <NuxtLink 
          to="/mentor" 
          class="icon-btn" 
          active-class="active"
          aria-label="AI Mentor" 
          title="AI Mentor"
        >
          <i class="bi bi-mortarboard-fill"></i>
        </NuxtLink>

        <!-- AI CV Generator -->
        <NuxtLink 
          to="/cv-generator" 
          class="icon-btn" 
          active-class="active"
          aria-label="AI CV Generator" 
          title="AI CV Generator"
        >
          <i class="bi bi-file-earmark-person"></i>
        </NuxtLink>

        <!-- <div class="vr mx-1 opacity-25" style="height: 24px;"></div> -->

        <!-- NavProfile component -->
        <NavProfile />
      </div>
    </div>
  </nav>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import NavProfile from "./NavProfile.vue";
import useAuth from "@/composables/useAuth";
import useMessages from "@/composables/useMessages";

const route = useRoute();
const router = useRouter();
const routeName = computed(() => {
  const seg = route.path.split("/").filter(Boolean)[0] || "";
  if (seg === "profile") return "Profil";
  if (!seg) return "Asosiy sahifa";
  return seg.charAt(0).toUpperCase() + seg.slice(1);
});

const auth = useAuth();
const { startPolling, stopPolling } = useMessages();

onMounted(() => {
  if (auth.user?.value?.id) {
    startPolling();
  }
});

onBeforeUnmount(() => {
  stopPolling();
});

watch(() => auth.user?.value?.id, (newId) => {
  if (newId) startPolling();
  else stopPolling();
});
</script>

<style scoped>
/* Navbar Styles */
.navbar {
  background-color: var(--bg-card) !important;
  border-bottom: 1px solid var(--border-color);
  box-shadow: var(--shadow-sm) !important;
  transition: var(--transition-base);
}

.navbar .brand {
  color: var(--primary);
  font-weight: 700;
  font-size: 1.25rem;
}

.navbar .brand span {
  color: var(--text-main);
}

.navbar .breadcrumb-item.active {
  color: var(--text-muted);
  align-items: center;
  display: flex;
}

.icon-btn {
  border: 1px solid var(--border-color);
  background-color: var(--bg-card);
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--text-main);
  transition: var(--transition-base);
  font-size: 20px;
}

.icon-btn:hover {
  background-color: var(--bg-app);
  color: var(--primary);
  border-color: var(--primary-light);
}

.icon-btn.active {
  background-color: var(--primary);
  color: white !important;
  border-color: var(--primary);
  box-shadow: 0 0 10px rgba(var(--primary-rgb), 0.3);
}

/* small badge styles for messages */
.badge-notif {
  position: absolute;
  top: -6px;
  right: -6px;
  background-color: var(--error);
  color: #fff;
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 999px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

</style>
