<template>
  <section class="premium-messenger-app">
    <div class="messenger-container">
      <div class="row g-0 h-100">
        
        <!-- LEFT: User Context / Notifications / Search -->
        <div class="col-lg-4 col-xl-3 border-end contact-sidebar-wrap d-flex flex-column h-100">
          <div class="contact-sidebar">
            <div class="sidebar-header">
              <h4 class="mb-3 fw-bold">Xabarlar</h4>
              <div class="premium-search-box">
                <i class="bi bi-search search-icon"></i>
                <input
                  v-model="q"
                  type="text"
                  class="search-input"
                  placeholder="Ism yoki email..."
                  @keyup.enter="applySearch"
                />
              </div>
            </div>

            <div class="contact-list custom-scrollbar">
              <div v-if="loadingUsers" class="p-4 text-center">
                <div class="spinner-border spinner-border-sm text-primary" role="status"></div>
                <div class="small mt-2 text-muted">Yuklanmoqda...</div>
              </div>

              <button
                v-for="u in users"
                :key="u.user_id"
                class="contact-item"
                :class="{ active: selectedUser && selectedUser.user_id === u.user_id }"
                @click="openChatWith(u)"
              >
                <div class="avatar-box">
                  <img v-if="u.avatar_url" :src="u.avatar_url" class="avatar-img" />
                  <div v-else class="initials-circle">{{ initials(u.fullname || u.email) }}</div>
                  <div v-if="u.is_online" class="online-status"></div>
                </div>
                
                <div class="contact-info">
                  <div class="d-flex justify-content-between align-items-center mb-1">
                    <span class="name text-truncate">{{ u.fullname || u.email }}</span>
                    <span class="time">{{ formatLastMsgTime(u.last_message_at) }}</span>
                  </div>
                  <div class="d-flex justify-content-between align-items-center">
                    <span class="last-text text-truncate">{{ u.email }}</span>
                    <span v-if="unreadMap[u.user_id] > 0" class="unread-badge">
                      {{ unreadMap[u.user_id] }}
                    </span>
                  </div>
                </div>
              </button>

              <div v-if="!loadingUsers && users.length === 0" class="p-4 text-center text-muted">
                Foydalanuvchi topilmadi.
              </div>
            </div>
          </div>
        </div>

        <!-- RIGHT: Chat Window -->
        <div class="col-lg-8 col-xl-9 chat-window-wrap d-flex flex-column h-100">
          <div v-if="!selectedUser" class="chat-empty-state">
            <div class="empty-illustration">
              <i class="bi bi-chat-heart"></i>
              <h3>Suhbatni boshlang</h3>
              <p>Muloqot qilish uchun chap tomondan foydalanuvchini tanlang.</p>
            </div>
          </div>

          <div v-else class="chat-window">
            <!-- Chat Header -->
            <div class="chat-header">
              <div class="d-flex align-items-center gap-3">
                <div class="avatar-box lg">
                  <img v-if="selectedUser?.avatar_url" :src="selectedUser.avatar_url" class="avatar-img" />
                  <div v-else class="initials-circle lg">{{ initials(selectedUser.fullname || selectedUser.email) }}</div>
                </div>
                <div>
                  <div class="chat-name">{{ selectedUser.fullname }}</div>
                  <div v-if="selectedUser.is_online" class="chat-status">
                    <span class="status-dot"></span> Online
                  </div>
                </div>
              </div>
              <div class="header-actions">
                <button class="action-btn" title="Qidiruv" @click="focusSearch"><i class="bi bi-search"></i></button>
                <button class="action-btn" title="Ma'lumot"><i class="bi bi-info-circle"></i></button>
              </div>
            </div>

            <!-- Chat Body -->
            <div class="chat-body custom-scrollbar" ref="chatBody">
              <div class="messages-container">
                <div
                  v-for="m in messages"
                  :key="m.id"
                  class="message-row"
                  :class="m.from_id === meId ? 'me' : 'them'"
                >
                  <div class="bubble">
                    <div class="bubble-content">{{ m.text }}</div>
                    <div class="bubble-meta">
                      {{ formatTime(m.created_at) }}
                      <i v-if="m.from_id === meId" class="bi" :class="m.read ? 'bi-check2-all' : 'bi-check2'"></i>
                    </div>
                  </div>
                </div>

                <div v-if="typing" class="message-row them">
                  <div class="bubble typing-bubble">
                    <div class="typing-indicator">
                      <span></span><span></span><span></span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Chat Input -->
            <div class="chat-input-area">
              <div class="input-pill">
                <button class="input-action"><i class="bi bi-plus-circle"></i></button>
                <input
                  v-model="draft"
                  @keyup.enter="send"
                  type="text"
                  placeholder="Xabaringizni yozing..."
                  :disabled="sending"
                />
                <button class="input-action"><i class="bi bi-emoji-smile"></i></button>
                <button 
                  class="send-btn" 
                  @click="send" 
                  :disabled="!draft.trim() || sending"
                >
                  <i v-if="!sending" class="bi bi-send-fill"></i>
                  <span v-else class="spinner-border spinner-border-sm"></span>
                </button>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from "vue";
import { useRouter, useRoute } from "#app";
import useAuth from "@/composables/useAuth";
import useApi from "@/composables/useApi";

const route = useRoute();
const auth = useAuth();
const api = useApi();
const router = useRouter();
const config = useRuntimeConfig();
const API_BASE_URL = config.public.apiUrl.replace(/\/api$/, "");

/* ---------- STATE ---------- */
const q = ref("");
const allUsers = ref([]);
const users = ref([]);
const loadingUsers = ref(false);
const selectedUser = ref(null);
const messages = ref([]);
const allMessages = ref([]);
const meId = ref(null);
const draft = ref("");
const sending = ref(false);
const typing = ref(false);
const chatBody = ref(null);
const unreadMap = ref({});

let pollTimer = null;

const totalUnread = computed(() =>
  Object.values(unreadMap.value).reduce((s, v) => s + (v || 0), 0)
);

/* ---------- HELPERS ---------- */
function initials(text = "") {
  if (!text) return "--";
  return text.split(" ").map(w => w[0] || "").slice(0, 2).join("").toUpperCase();
}

function formatTime(ts) {
  if (!ts) return "";
  return new Date(ts).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function formatLastMsgTime(ts) {
  if (!ts) return "";
  const d = new Date(ts);
  const now = new Date();
  if (d.toDateString() === now.toDateString()) {
    return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  }
  return d.toLocaleDateString([], { month: "short", day: "numeric" });
}

function focusSearch() {
  const el = document.querySelector(".search-input");
  if (el) el.focus();
}

async function ensureAuth() {
  const uid = auth?.user?.value?.id;
  if (!uid) {
    router.push("/signin");
    return false;
  }
  meId.value = uid;
  return true;
}

/* ---------- DATA LOADERS ---------- */
async function loadUsersAndMessages() {
  if (!(await ensureAuth())) return;
  loadingUsers.value = true;
  try {
    const [profResp, msgResp] = await Promise.all([
      api.get("/profiles/"),
      api.get("/messages/"),
    ]);

    const profData = Array.isArray(profResp.data) ? profResp.data : profResp.data.results ?? [];
    allUsers.value = profData
      .filter(p => (p.user?.id ?? p.user_id) !== meId.value)
      .map(p => {
        const u = p.user || {};
        let av = p.avatar_url || p.avatar || null;
        if (av && !av.startsWith("http")) av = API_BASE_URL + av;
        return {
          user_id: u.id,
          fullname: p.full_name || p.fullname || u.username || u.email || "Foydalanuvchi",
          email: u.email || "",
          avatar_url: av,
          last_message_at: null,
          is_online: false, // Default to offline until backend support
        };
      });

    setMessagesFromResponse(msgResp.data);
  } catch (e) {
    console.error("loadUsersAndMessages error:", e);
  } finally {
    loadingUsers.value = false;
  }
}

async function loadMessagesOnly() {
  if (!(await ensureAuth())) return;
  try {
    const msgResp = await api.get("/messages/");
    setMessagesFromResponse(msgResp.data);
    if (selectedUser.value) {
      loadMessagesWith(selectedUser.value.user_id);
    }
  } catch (e) {
    console.error("loadMessagesOnly error:", e);
  }
}

function setMessagesFromResponse(raw) {
  const msgData = Array.isArray(raw) ? raw : raw.results ?? [];
  allMessages.value = msgData.map(m => ({
    id: m.id,
    from_id: m.from_user?.id ?? m.from_user,
    to_id: m.to_user_detail?.id ?? m.to_user ?? null,
    text: m.text ?? m.body ?? "",
    created_at: m.created_at,
    read: m.read ?? m.seen ?? false,
  }));
  recomputeMetaAndList();
}

function recomputeMetaAndList() {
  const lastMap = {};
  const unread = {};
  allMessages.value.forEach(m => {
    const peerId = m.from_id === meId.value ? m.to_id : m.from_id;
    if (!peerId) return;
    if (!lastMap[peerId] || m.created_at > lastMap[peerId]) lastMap[peerId] = m.created_at;
    if (m.to_id === meId.value && !m.read) unread[m.from_id] = (unread[m.from_id] || 0) + 1;
  });
  unreadMap.value = unread;
  
  const term = q.value.trim().toLowerCase();
  users.value = allUsers.value
    .map(u => ({ ...u, last_message_at: lastMap[u.user_id] || null }))
    .filter(u => !term || u.fullname.toLowerCase().includes(term) || u.email.toLowerCase().includes(term))
    .sort((a, b) => (new Date(b.last_message_at || 0) - new Date(a.last_message_at || 0)));
  
  if (route.query.user && !selectedUser.value) openChatFromQuery();
}

function openChatFromQuery() {
  const qUserId = route.query.user;
  if (!qUserId) return;
  const target = users.value.find(u => String(u.user_id) === String(qUserId));
  if (target) openChatWith(target);
}

function applySearch() { recomputeMetaAndList(); }

async function openChatWith(profile) {
  if (!(await ensureAuth())) return;
  selectedUser.value = profile;
  loadMessagesWith(profile.user_id);
  await markMessagesReadFrom(profile.user_id);
  nextTick(scrollToBottom);
}

function loadMessagesWith(peerId) {
  messages.value = allMessages.value.filter(m => (m.from_id === meId.value && m.to_id === peerId) || (m.from_id === peerId && m.to_id === meId.value));
}

async function markMessagesReadFrom(peerId) {
  if (!allMessages.value.some(m => m.from_id === peerId && m.to_id === meId.value && !m.read)) return;
  try {
    await api.post("/messages/mark-read/", { with: peerId });
    allMessages.value = allMessages.value.map(m => (m.from_id === peerId && m.to_id === meId.value) ? { ...m, read: true } : m);
    unreadMap.value[peerId] = 0;
    recomputeMetaAndList();
  } catch (e) { console.error(e); }
}

async function send() {
  if (!selectedUser.value || !draft.value.trim() || sending.value) return;
  sending.value = true;
  try {
    const resp = await api.post("/messages/", { to_user: selectedUser.value.user_id, text: draft.value.trim() });
    const m = resp.data;
    allMessages.value.push({
      id: m.id,
      from_id: m.from_user?.id ?? m.from_user,
      to_id: m.to_user_detail?.id ?? m.to_user ?? null,
      text: m.text ?? m.body ?? "",
      created_at: m.created_at,
      read: false
    });
    draft.value = "";
    loadMessagesWith(selectedUser.value.user_id);
    recomputeMetaAndList();
    nextTick(scrollToBottom);
  } catch (e) { console.error(e); }
  finally { sending.value = false; }
}

function scrollToBottom() {
  const el = chatBody.value;
  if (el) el.scrollTop = el.scrollHeight;
}

function startPolling() {
  pollTimer = setInterval(loadMessagesOnly, 5000);
}

onMounted(async () => {
  if (await ensureAuth()) {
    await loadUsersAndMessages();
    startPolling();
  }
});

onUnmounted(() => { if (pollTimer) clearInterval(pollTimer); });
</script>
