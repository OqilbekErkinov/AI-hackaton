// /middleware/auth.global.ts
export default defineNuxtRouteMiddleware(async (to, from) => {
  const publicPaths = ['/signin', '/signup', '/forgot', '/auth'];
  const path = to.path || '';

  const auth = useAuth();
  
  // Agar token cookie'da mavjud bo'lsa va user ma'lumotlari hali yo'q bo'lsa - init() qilamiz
  // Bu serverda ham, clientda ham ishlaydi
  if (auth.token.value && !auth.user.value) {
    await auth.init();
  }

  const uid = auth.user.value?.id;

  // 1. Agar foydalanuvchi login qilmagan bo'lsa va sahifa himoyalangan bo'lsa
  if (!uid && !publicPaths.includes(path)) {
    return navigateTo('/signin');
  }

  // 2. Agar foydalanuvchi tizimga kirgan bo'lsa va auth sahifalariga kirmoqchi bo'lsa
  if (uid && (path === '/signin' || path === '/signup')) {
    return navigateTo('/');
  }
});
