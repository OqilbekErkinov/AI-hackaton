<template>
  <aside class="sidebar-mini shadow-sm">
    <ul class="nav flex-column align-items-center py-3">
      <li class="nav-item">
        <NuxtLink
          class="smini-link"
          :class="{ active: route.path === '/' }"
          to="/"
          title="Bosh sahifa"
        >
          <i class="bi bi-house"></i>
        </NuxtLink>
      </li>
      <li class="nav-item">
        <NuxtLink
          class="smini-link"
          :class="{ active: route.path.startsWith('/profile') }"
          to="/profile"
          title="Profil"
        >
          <i class="bi bi-person"></i>
        </NuxtLink>
      </li>

      <li class="nav-item">
        <NuxtLink
          class="smini-link"
          :class="{ active: route.path.startsWith('/scholarship') }"
          to="/scholarship"
          @click="$emit('close')"
        >
          <i class="bi bi-book"></i>
        </NuxtLink>
      </li>
      <li class="nav-item">
        <NuxtLink
          class="smini-link"
          :class="{ active: route.path.startsWith('/social') }"
          to="/social"
          @click="$emit('close')"
        >
          <i class="bi bi-person-workspace"></i>
        </NuxtLink>
      </li>

      <li class="nav-item">
        <NuxtLink
          class="smini-link"
          :class="{ active: route.path.startsWith('/reyting') }"
          to="/reyting"
          @click="$emit('close')"
          ><i class="bi bi-trophy"></i>
        </NuxtLink>
      </li>
      <li class="nav-item">
        <NuxtLink
          class="smini-link position-relative"
          :class="{ active: route.path.startsWith('/messenger') }"
          to="/messenger"
          @click="$emit('close')"
        >
          <i class="bi bi-messenger"></i>
          <span v-if="unreadCount > 0" class="badge-mini rounded-pill">{{ unreadCount }}</span>
        </NuxtLink>
      </li>
      <li class="nav-item">
        <NuxtLink
          class="smini-link"
          :class="{ active: route.path.startsWith('/announcement') }"
          to="/announcement"
          @click="$emit('close')"
          ><i class="bi bi-megaphone"></i
        ></NuxtLink>
      </li>
    </ul>
  </aside>
</template>

<script setup>
import { useRoute } from "vue-router";
const route = useRoute();
import useMessages from "@/composables/useMessages";
const { unreadCount } = useMessages();
</script>


