// router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import SignIn from '~/pages/signin.vue'
import SignUp from '~/pages/signup.vue'
import Home from '@/pages/Home.vue'
import Profile from '@/pages/Profile.vue'
import { useAuth } from '~/composables/useAuth'

const routes = [
  { path: '/signin', component: SignIn, meta: { guest: true } },
  { path: '/signup', component: SignUp, meta: { guest: true } },
  { path: '/', component: Home, meta: { requiresAuth: true } },
  { path: '/profile', component: Profile, meta: { requiresAuth: true } },
  // ... boshqa yo‘llar ...
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to, from, next) => {
  const auth = useAuth()
  //  auth.state.value.ready bo'lsa sessiya yuklangan
  const ready = auth.state.value.ready
  const user = auth.state.value.user

  // Agar hali state.ready bo'lmasa, kutish uchun minimal mexanizm:
  if (!ready) {
    // kichik kutish: bu kod synchronous bo'lgani uchun oddiy yo'l - setTimeout bir necha ms kutib qayta chaqirish
    return setTimeout(() => { router.push(to.fullPath) }, 10)
  }

  if (to.meta.requiresAuth && !user) {
    return next('/signin')
  }
  if (to.meta.guest && user) {
    // agar login sahifini ko'rsatmaslik kerak bo'lsa va foydalanuvchi allaqachon login bo'lsa
    return next('/')
  }
  next()
})

export default router
