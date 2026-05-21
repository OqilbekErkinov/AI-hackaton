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

async function onSubmit() {
  err.value = null;
  message.value = null;
  loading.value = true;
  try {
    // yuborishda AVATAR fayl mavjud bo'lsa faylni yuboramiz,
    // mavjud bo'lmasa avarPreview (dataURL)ni yuboramiz (backend formdata qabul qiladi)
    const res = await auth.register({
      fullname: fullname.value,
      email: email.value,
      phone: phone.value,
      password: password.value,
      avatarFile: avatarFile.value,
      avatarDataUrl: !avatarFile.value ? avatarPreview.value : null,
    });

    if (res && (res.data || res.data?.user)) {
      // muvaffaqiyat
      message.value = "Roʻyxatdan oʻtish muvaffaqiyatli.";
      // agar token qaytilgan bo'lsa yoki session bo'lsa, redirect qilamiz
      if (res.data?.access || res.data?.token || auth.user.value) {
        router.push("/profile");
      }
    } else if (res && res.error) {
      // handle axios response error object
      err.value =
        res.error?.detail ||
        res.error?.message ||
        JSON.stringify(res.error) ||
        "Roʻyxatdan oʻtishda xato";
    } else {
      err.value = "Roʻyxatdan oʻtishda noma'lum xato yuz berdi";
    }
  } catch (e: any) {
    // e.response?.data ni ko'rib chiqamiz
    const r = e?.response?.data;
    if (r) {
      if (typeof r === "string") err.value = r;
      else if (r?.detail) err.value = r.detail;
      else err.value = JSON.stringify(r);
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
