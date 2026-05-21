<template>
  <div class="auth-card" style="color: #112d4e;">
    <h3>Roʻyxatdan oʻtish</h3>
    <form @submit.prevent="onSubmit">
      <input
        v-model="fullname"
        placeholder="To'liq ism"
        class="form-control mb-2"
      />
      <input v-model="phone" placeholder="Telefon" class="form-control mb-2" />
      <input v-model="email" placeholder="Email" class="form-control mb-2" />
      <input
        v-model="password"
        type="password"
        placeholder="Parol"
        class="form-control mb-2"
      />
      <!-- <div class="mb-2">
        <input style="border-radius: 5px;" type="file" @change="onAvatar" />
        <div v-if="avatarPreview" class="mt-2">
          <img
            :src="avatarPreview"
            style="width: 80px; height: 80px; border-radius: 50%"
          />
        </div>
      </div> -->

      <div class="d-flex gap-2">
        <button class="btn btn-bg" :disabled="loading">
          Roʻyxatdan oʻtish
        </button>
        <button
          class="btn btn-bg2"
          type="button"
          @click="goToSignin"
        >
          Sign in
        </button>
      </div>

      <div v-if="err" class="text-danger mt-2">{{ err }}</div>
      <div v-if="message" class="text-success mt-2">{{ message }}</div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import useAuth from "~/composables/useAuth";
import { useRouter } from "vue-router";

const auth = useAuth();
const router = useRouter();

const fullname = ref("");
const email = ref("");
const phone = ref("");
const password = ref("");
const avatarFile = ref<File | null>(null);
const avatarPreview = ref<string | null>(null);
const loading = ref(false);
const err = ref<string | null>(null);
const message = ref<string | null>(null);

onMounted(async () => {
  await auth.init();
  // agar allaqachon login bo'lsa
  if (auth.user.value) router.push("/");
});

function onAvatar(e: Event) {
  const f = (e.target as HTMLInputElement).files?.[0] ?? null;
  if (!f) {
    avatarFile.value = null;
    avatarPreview.value = null;
    return;
  }
  avatarFile.value = f;
  const reader = new FileReader();
  reader.onload = () => (avatarPreview.value = reader.result as string);
  reader.readAsDataURL(f);
}

function translateError(msg: string): string {
  let text = msg;
  if (text.includes("This password is too common")) {
    text = "Bu parol juda oddiy va keng tarqalgan. Iltimos, murakkabroq parol tanlang.";
  } else if (text.includes("too similar to the username")) {
    text = "Parol foydalanuvchi nomiga (email boshlang'ich qismiga) juda o'xshash bo'lmasligi kerak.";
  } else if (text.includes("too short")) {
    text = "Parol juda qisqa. Kamida 8 ta belgidan iborat bo'lishi kerak.";
  } else if (text.includes("entirely numeric")) {
    text = "Parol faqat raqamlardan iborat bo'lmasligi kerak.";
  } else if (text.includes("user with this username already exists")) {
    text = "Ushbu elektron pochta egasi allaqachon ro'yxatdan o'tgan.";
  }
  return text;
}

function formatValidationError(data: any): string {
  if (!data) return "Noma'lum xatolik yuz berdi";
  if (typeof data === "string") return data;
  if (data.detail) return data.detail;
  if (data.message) return data.message;

  const errors: string[] = [];
  for (const [key, value] of Object.entries(data)) {
    let fieldName = key;
    if (key === "fullname") fieldName = "To'liq ism";
    else if (key === "email") fieldName = "Elektron pochta";
    else if (key === "phone") fieldName = "Telefon raqami";
    else if (key === "password") fieldName = "Parol";

    if (Array.isArray(value)) {
      const translatedVals = value.map(val => translateError(String(val)));
      errors.push(`${fieldName}: ${translatedVals.join(", ")}`);
    } else {
      errors.push(`${fieldName}: ${translateError(String(value))}`);
    }
  }

  if (errors.length > 0) {
    return errors.join(" | ");
  }
  return JSON.stringify(data);
}

async function onSubmit() {
  err.value = null;
  message.value = null;
  loading.value = true;
  try {
    const res = await auth.register({
      fullname: fullname.value,
      email: email.value,
      phone: phone.value,
      password: password.value,
      avatarFile: avatarFile.value,
      avatarDataUrl: !avatarFile.value ? avatarPreview.value : null,
    });

    if (res && (res.data || res.data?.user)) {
      message.value = "Roʻyxatdan oʻtish muvaffaqiyatli.";
      if (res.data?.access || res.data?.token || auth.user.value) {
        router.push("/profile");
      }
    } else if (res && res.error) {
      err.value = formatValidationError(res.error);
    } else {
      err.value = "Roʻyxatdan oʻtishda noma'lum xato yuz berdi";
    }
  } catch (e: any) {
    const r = e?.response?.data;
    if (r) {
      err.value = formatValidationError(r);
    } else {
      err.value = e?.message || String(e);
    }
  } finally {
    loading.value = false;
  }
}

function goToSignin() {
  router.push("/signin");
}
</script>
