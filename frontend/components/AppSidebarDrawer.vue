<template>
  <aside class="sidebar-drawer shadow-lg" role="dialog" aria-label="Yon menyu">
    <ul class="nav flex-column px-3 mt-3">
      <li class="nav-item">
        <NuxtLink
          class="nav-link sdw-link"
          :class="{ active: route.path === '/' }"
          to="/"
          @click="$emit('close')"
        >
          <i class="bi bi-house"></i> Bosh sahifa
        </NuxtLink>
      </li>
      <li class="nav-item">
        <NuxtLink
          class="nav-link sdw-link"
          :class="{ active: route.path.startsWith('/profile') }"
          to="/profile"
          @click="$emit('close')"
        >
          <i class="bi bi-person"></i> Profil
        </NuxtLink>
      </li>
      <li class="nav-item">
        <NuxtLink
          class="nav-link sdw-link"
          :class="{ active: route.path.startsWith('/scholarship') }"
          to="/scholarship"
          @click="$emit('close')"
        >
          <i class="bi bi-book"></i> Akademik o`zlashtirish
        </NuxtLink>
      </li>
      <!-- <li class="nav-item">
        <NuxtLink
          class="nav-link sdw-link"
          :class="{ active: route.path.startsWith('/social') }"
          to="/social"
          @click="$emit('close')"
        >
          <i class="bi bi-person-workspace"></i> Ijtimoiy faollik
        </NuxtLink>
      </li> -->

      <li class="nav-item">
        <NuxtLink
          class="nav-link sdw-link"
          :class="{ active: route.path.startsWith('/reyting') }"
          to="/reyting"
          @click="$emit('close')"
          ><i class="bi bi-trophy"></i> Reyting
        </NuxtLink>
      </li>
      <li class="nav-item">
        <NuxtLink
          class="nav-link sdw-link d-flex align-items-center justify-content-between"
          :class="{ active: route.path.startsWith('/messenger') }"
          to="/messenger"
          @click="$emit('close')"
        >
          <span><i class="bi bi-messenger"></i> Messenger</span>
          <span v-if="unreadCount > 0" class="badge bg-danger rounded-pill">{{ unreadCount }}</span>
        </NuxtLink>
      </li>
      <li class="nav-item">
        <NuxtLink
          class="nav-link sdw-link"
          :class="{ active: route.path.startsWith('/announcement') }"
          to="/announcement"
          @click="$emit('close')"
          ><i class="bi bi-megaphone"></i> E'lonlar</NuxtLink
        >
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


