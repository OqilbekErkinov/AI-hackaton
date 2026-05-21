<template>
  <div class="ai-assistant-container p-3 p-md-4">
    <div class="row g-4 h-100">

      <!-- CHAT QISMI -->
      <div class="col-lg-8 d-flex flex-column h-100">
        <div class="card chat-card border-0 shadow-sm flex-grow-1 overflow-hidden">
          <!-- Sarlavha -->
          <div class="card-header bg-white border-bottom py-3 d-flex align-items-center justify-content-between">
            <div class="d-flex align-items-center">
              <div class="ai-avatar me-3"><i class="bi bi-robot"></i></div>
              <div>
                <h5 class="mb-0 fw-bold">AI Yordamchi</h5>
                <small class="text-success">
                  <i class="bi bi-circle-fill me-1" style="font-size:0.5rem"></i> Onlayn
                </small>
              </div>
            </div>
            <button class="btn btn-light btn-sm" @click="clearChat">
              <i class="bi bi-trash"></i>
            </button>
          </div>

          <!-- Xabarlar ro'yxati -->
          <div class="card-body chat-body p-0 overflow-y-auto" ref="chatBody">
            <div v-if="loadingHistory" class="p-4 text-center">
              <div class="spinner-border spinner-border-sm text-primary"></div>
            </div>

            <div v-else-if="messages.length === 0" class="empty-chat p-5 text-center">
              <div class="empty-icon mb-3"><i class="bi bi-chat-dots"></i></div>
              <h6 class="text-muted">Salom! Qanday yordam bera olaman?</h6>
              <p class="text-muted small">Masalan: "Menga mos stipendiyalar bormi?" deb so'rang.</p>
            </div>

            <div v-else class="p-3 p-md-4">
              <div
                v-for="(msg, idx) in messages"
                :key="idx"
                class="message-wrapper mb-4"
                :class="msg.is_user ? 'user-message' : 'ai-message'"
              >
                <div class="message-bubble shadow-sm p-3">
                  <div v-html="formatText(msg.text)"></div>
                  <div class="message-time mt-1">{{ formatTime(msg.created_at) }}</div>
                </div>
              </div>

              <!-- Yozmoqda animatsiyasi -->
              <div v-if="sending" class="message-wrapper ai-message mb-4">
                <div class="message-bubble shadow-sm p-3 typing-bubble">
                  <span class="dot"></span><span class="dot"></span><span class="dot"></span>
                </div>
              </div>
            </div>
          </div>

          <!-- Input -->
          <div class="card-footer bg-white border-top p-3">
            <form @submit.prevent="sendMessage" class="d-flex gap-2">
              <input
                v-model="userInput"
                type="text"
                class="form-control chat-input border-0 bg-light py-2"
                placeholder="Savolingizni yozing..."
                :disabled="sending"
              />
              <button type="submit" class="btn btn-primary send-btn px-4" :disabled="sending || !userInput.trim()">
                <i class="bi bi-send-fill" v-if="!sending"></i>
                <div v-else class="spinner-border spinner-border-sm"></div>
              </button>
            </form>
          </div>
        </div>
      </div>

      <!-- YON PANEL -->
      <div class="col-lg-4">
        <div class="card border-0 shadow-sm mb-4">
          <div class="card-body">
            <h6 class="fw-bold mb-3">
              <i class="bi bi-stars text-warning me-2"></i> Qiziqishlarim
            </h6>
            <p class="text-muted small">AI sizga mos takliflar berishi uchun qiziqishlaringizni kiriting.</p>

            <div class="d-flex gap-2 mb-3">
              <input
                v-model="newInterest"
                type="text"
                class="form-control form-control-sm border-0 bg-light"
                placeholder="Masalan: Sport"
                @keypress.enter.prevent="addInterest"
              />
              <button class="btn btn-primary btn-sm px-3" @click="addInterest">
                <i class="bi bi-plus-lg"></i>
              </button>
            </div>

            <div class="d-flex flex-wrap gap-2">
              <span v-for="(item, i) in interests" :key="i" class="badge interest-chip">
                {{ item }}
                <i class="bi bi-x ms-2" style="cursor:pointer" @click="removeInterest(i)"></i>
              </span>
              <span v-if="!interests.length" class="text-muted small">Hali qiziqish kiritilmagan</span>
            </div>

            <hr class="my-3 opacity-50">

            <h6 class="fw-bold mb-2 small text-uppercase text-muted">Men haqimda</h6>
            <textarea
              v-model="userAbout"
              class="form-control form-control-sm border-0 bg-light"
              rows="4"
              placeholder="O'zingiz haqida qisqacha ma'lumot..."
              @blur="saveAbout"
            ></textarea>
            <small class="text-muted d-block text-end" style="font-size:0.7rem">Avtomatik saqlanadi</small>
          </div>
        </div>

        <div class="card border-0 bg-primary-subtle shadow-sm">
          <div class="card-body">
            <h6 class="fw-bold mb-2 small"><i class="bi bi-info-circle me-1"></i> Maslahat</h6>
            <p class="mb-0 small" style="line-height:1.4">
              AI yordamchiga istalgan savolingizni bering.
              U sizning yutuqlaringiz, XP ballaringiz va qiziqishlaringizni biladi!
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue';

const api = useApi();

const messages = ref([]);
const userInput = ref('');
const sending = ref(false);
const loadingHistory = ref(true);
const chatBody = ref(null);
const newInterest = ref('');
const interests = ref([]);
const userAbout = ref('');

onMounted(async () => {
  await fetchHistory();
  try {
    const res = await api.get('/profiles/me/');
    interests.value = res.data.interests || [];
    userAbout.value = res.data.about || '';
  } catch (e) {
    console.error("Error fetching profile:", e);
  }
});

const fetchHistory = async () => {
  loadingHistory.value = true;
  try {
    const res = await api.get('/ai-chat/');
    messages.value = res.data.results || res.data;
    scrollToBottom();
  } catch (e) {
    console.error(e);
  } finally {
    loadingHistory.value = false;
  }
};

const sendMessage = async () => {
  if (!userInput.value.trim() || sending.value) return;
  const text = userInput.value;
  userInput.value = '';
  const now = new Date().toISOString();
  messages.value.push({ text, is_user: true, created_at: now });
  scrollToBottom();
  sending.value = true;
  try {
    const res = await api.post('/ai-chat/', { text });
    messages.value.push(res.data);
    scrollToBottom();
  } catch (e) {
    messages.value.push({ text: "Uzr, tizimda xatolik yuz berdi.", is_user: false, created_at: new Date().toISOString() });
  } finally {
    sending.value = false;
  }
};

const clearChat = () => {
  if (confirm("Chat tarixini o'chirmoqchimisiz?")) messages.value = [];
};

const addInterest = async () => {
  const val = newInterest.value.trim();
  if (!val || interests.value.includes(val)) return;
  interests.value.push(val);
  newInterest.value = '';
  try {
    await api.patch('/profiles/update_me/', { interests: interests.value });
  } catch (e) {
    console.error("Error updating interests:", e);
  }
};

const removeInterest = async (i) => {
  interests.value.splice(i, 1);
  try {
    await api.patch('/profiles/update_me/', { interests: interests.value });
  } catch (e) {
    console.error("Error removing interest:", e);
  }
};

const saveAbout = async () => {
  try {
    await api.patch('/profiles/update_me/', { about: userAbout.value });
  } catch (e) {
    console.error("Error saving 'about':", e);
  }
};

const scrollToBottom = () => nextTick(() => {
  if (chatBody.value) chatBody.value.scrollTop = chatBody.value.scrollHeight;
});

const formatText = (text) => text ? text.replace(/\n/g, '<br/>') : '';
const formatTime = (d) => {
  if (!d) return '';
  return new Date(d).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};
</script>
