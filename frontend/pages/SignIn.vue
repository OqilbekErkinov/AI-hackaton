<template>
  <div class="auth-card">
    <h3 style="color: #112d4e">Kirish</h3>
    <form @submit.prevent="onSubmit">
      <input v-model="email" placeholder="Email" class="form-control mb-2" />
      <input
        v-model="password"
        type="password"
        placeholder="Parol"
        class="form-control mb-2"
      />
      <div class="d-flex gap-2">
        <button class="btn-bg" :disabled="loading">Kirish</button>
        <button
          class="btn btn-outline-secondary"
          type="button"
          @click="goToSignup"
        >
          Roʻyxatdan oʻtish
        </button>
      </div>
      <div v-if="err" class="text-danger mt-2">{{ err }}</div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import useAuth from "~/composables/useAuth";
import { useRouter } from "vue-router";

const auth = useAuth();
const router = useRouter();

const email = ref("");
const password = ref("");
const loading = ref(false);
const err = ref<string | null>(null);

onMounted(async () => {
  await auth.init();
  // agar foydalanuvchi allaqachon kirgan bo'lsa, indexga yubor
  if (auth.user.value) {
    router.push("/");
  }
});

function formatSigninError(e: any): string {
  if (e?.message === "Network Error" || e?.code === "ERR_NETWORK" || e?.message?.includes("Network Error")) {
    return "Server bilan aloqa bog'lab bo'lmadi. Iltimos, server ishlayotganligini yoki internet aloqangizni tekshiring.";
  }
  const r = e?.response?.data;
  if (r) {
    if (typeof r === "string") return r;
    if (r.detail) {
      if (r.detail.includes("No active account found") || r.detail.includes("credentials")) {
        return "Email yoki parol noto'g'ri. Iltimos, tekshirib qaytadan urinib ko'ring.";
      }
      return r.detail;
    }
    return JSON.stringify(r);
  }
  return e?.message || "Tizimga kirishda kutilmagan xatolik yuz berdi.";
}

async function onSubmit() {
  err.value = null;
  loading.value = true;
  try {
    const { data } = await auth.login({ email: email.value, password: password.value });
    // agar muvaffaqiyat bo'lsa
    if (data) {
      router.push("/");
    }
  } catch (e: any) {
    err.value = formatSigninError(e);
  } finally {
    loading.value = false;
  }
}


function goToSignup() {
  router.push("/signup");
}
</script>
