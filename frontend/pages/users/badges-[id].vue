<template>
    <div class="profile-wrap" v-if="!loading">
        <!-- HERO -->
        <section class="hero">
            <div class="hero-card">
                <!-- MESSAGE BUTTON -->
                <button class="message-btn" @click="goToChat" title="Xabar yuborish">
                    <i class="bi bi-chat-dots-fill"></i>
                </button>

                <div class="avatar">
                    <img v-if="user.avatar" :src="user.avatar" />
                    <span v-else>{{ initials }}</span>
                </div>

                <div class="info">
                    <h2>{{ user.fullname || "Ism yo‘q" }}</h2>
                    <p class="muted">
                        <span v-if="user.universityFull">
                            {{ user.universityFull }} •
                        </span>
                        <span v-else-if="user.universityShort">
                            {{ user.universityShort }} •
                        </span>
                        <span v-if="user.major">{{ user.major }} • </span>
                        <span v-if="user.course"> {{ user.course }}-kurs </span>



                    </p>

                    <div class="stats">
                        <div>
                            <strong>Level</strong>
                            <span>{{ level }}</span>
                        </div>
                        <div>
                            <strong>XP</strong>
                            <span>{{ fmt(user.xp) }}</span>
                        </div>
                        <div>
                            <strong>Rank</strong>
                            <span>#{{ user.globalRank || "-" }}</span>
                        </div>
                    </div>

                    <div class="xp-bar">
                        <div class="xp-fill" :style="{ width: xpPercent + '%' }"></div>
                    </div>
                </div>
            </div>
        </section>

        <!-- BADGES -->
        <section class="badges">
            <h3>Yutuqlar: {{ badges.length }}</h3>

            <div class="badge-grid">
                <div v-for="b in badges" :key="b.id" class="badge-item">
                    <div class="icon">🏅</div>
                    <div class="title">{{ b.title }}</div>
                    <div class="xp">+{{ fmt(b.xp_count) }} XP</div>
                </div>
            </div>

            <div v-if="badges.length === 0" class="muted">Hozircha yutuqlar yo‘q</div>
        </section>

        <!-- TOAST -->
        <div v-if="toast.show" class="toast-box" :class="toast.type">
            {{ toast.message }}
        </div>
    </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from "vue";
import { useRoute, useRouter } from "#app";
import useAuth from "@/composables/useAuth";
import useApi from "@/composables/useApi";

/* ---------------- CORE ---------------- */
const route = useRoute();
const router = useRouter();
const auth = useAuth();
const api = useApi();
const config = useRuntimeConfig();
const API_BASE_URL = config.public.apiUrl.replace(/\/api$/, "");

/* ---------------- TOAST ---------------- */
const toast = reactive({
    show: false,
    message: "",
    type: "info", // info | error | success
});

function showToast(msg, type = "info", timeout = 3000) {
    toast.message = msg;
    toast.type = type;
    toast.show = true;

    setTimeout(() => {
        toast.show = false;
    }, timeout);
}

/* ---------------- CONFIG ---------------- */
const XP_PER_LEVEL = 100;
const MAX_XP = 10000;

/* ---------------- STATE ---------------- */
const user = reactive({
    id: null,
    fullname: "",
    universityShort: "",
    universityFull: "",
    major: "",
    course: "",
    xp: 0,
    avatar: null,
    globalRank: null,
});

const badges = ref([]);
const loading = ref(true);

/* ---------------- COMPUTED ---------------- */
const level = computed(() => Math.floor(user.xp / XP_PER_LEVEL));
const xpPercent = computed(() => {
    const percent = (user.xp / MAX_XP) * 100
    return Math.min(percent, 100)
})

const initials = computed(() =>
    user.fullname
        ? user.fullname
            .split(" ")
            .map((w) => w[0])
            .slice(0, 2)
            .join("")
            .toUpperCase()
        : "?"
);

const fmt = (n) => Number(n || 0).toLocaleString();

/* ---------------- ACTIONS ---------------- */
function goToChat() {
    const userId = route.params.id;
    const myId = auth.user?.value?.id;

    if (!userId || !myId) return;

    if (String(userId) === String(myId)) {
        showToast("O‘zingizga xabar yubora olmaysiz 🙂", "error");
        return;
    }

    router.push({
        path: "/messenger",
        query: { user: userId },
    });
}

/* ---------------- API ---------------- */
async function loadProfile(userId) {
    loading.value = true;
    try {
        const res = await api.get(`/profiles/?user_id=${userId}`);
        const p = Array.isArray(res.data) ? res.data[0] : res.data;

        if (!p) return;

        user.id = p.user?.id || p.user_id || userId;
        user.fullname = p.full_name || p.fullname || "";
        user.universityShort = p.university_short || "";
        user.universityFull = p.university_full || "";
        user.major = p.major_name || p.major || "";   // 🔥 MUHIM TUZATISH
        user.course = p.course || "";
        user.xp = p.xp || 0;
        
        let av = p.avatar_url || p.avatar || null;
        if (av && !av.startsWith("http")) {
            av = API_BASE_URL + av;
        }
        user.avatar = av;
        user.globalRank = p.global_rank || null;

    } catch (err) {
        console.error("loadProfile error", err);
    } finally {
        loading.value = false;
    }
}
async function loadBadges(userId) {
    try {
        const res = await api.get(`/badges/?user_id=${userId}`);
        badges.value = Array.isArray(res.data) ? res.data : [];
    } catch (err) {
        console.error("loadBadges error", err);
    }
}

/* ---------------- LIFECYCLE ---------------- */
onMounted(async () => {
    const rawId = route.params.id
    const uid = String(rawId).split("-")[0]

    if (uid) {
        await loadProfile(uid)
        await loadBadges(uid)
    }
})
</script>




