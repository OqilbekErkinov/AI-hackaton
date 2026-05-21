<template>
  <div class="rankedu">
    <!-- NAVBAR -->
    <AppNavbar @toggle-sidebar="toggleSidebar" />
    <div class="app-body">
      <!-- MINI SIDEBAR (doimiy) -->
      <AppSidebarMini />
      <!-- DRAWER SIDEBAR (toggle bilan ochiladi) -->
      <transition name="drawer">
        <AppSidebarDrawer v-if="isSidebarOpen" @close="isSidebarOpen=false" />
      </transition>
      <transition name="fade">
        <div v-if="isSidebarOpen" class="backdrop" @click="isSidebarOpen=false"></div>
      </transition>
      <!-- KONTENT ZONASI: faqat shu qism sahifa bo‘yicha o‘zgaradi -->
      <main class="content" :class="{ 'chat-mode': isChatPage }">
        <slot />
      </main>
    </div>
    <AppFooter @toggle-sidebar="toggleSidebar" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import AppNavbar from '~/components/AppNavbar.vue'
import AppFooter from '~/components/AppFooter.vue'
import AppSidebarMini from '~/components/AppSidebarMini.vue'
import AppSidebarDrawer from '~/components/AppSidebarDrawer.vue'

const route = useRoute()
const isSidebarOpen = ref(false)
const toggleSidebar = () => { isSidebarOpen.value = !isSidebarOpen.value }
const isChatPage = computed(() => route.path.includes('/messenger'))
</script>
