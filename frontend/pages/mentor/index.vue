<template>
  <div class="mentor-page p-3 p-md-4">
    <div class="container-fluid max-w-1400">
      <div class="row g-4">

        <!-- CHAT QISMI -->
        <div class="col-lg-8">
          <div class="card border-0 shadow-lg chat-card glass-morph overflow-hidden">
            <!-- Sarlavha -->
            <div class="card-header bg-white border-0 py-3 px-4 d-flex align-items-center justify-content-between">
              <div class="d-flex align-items-center">
                <div class="mentor-avatar me-3"><i class="bi bi-mortarboard-fill"></i></div>
                <div>
                  <h5 class="fw-bold m-0 text-dark">AI Mentor</h5>
                  <span class="d-flex align-items-center" style="font-size:0.75rem;color:#22c55e">
                    <span class="status-dot me-1"></span> Online
                  </span>
                </div>
              </div>
              <button @click="resetSession" class="btn btn-sm btn-outline-secondary rounded-pill">
                <i class="bi bi-arrow-counterclockwise"></i> Qayta boshlash
              </button>
            </div>

            <!-- Xabarlar -->
            <div class="card-body chat-body p-4" ref="chatContainer">
              <div v-if="messages.length === 0" class="text-center text-muted py-5">
                <i class="bi bi-mortarboard" style="font-size:3rem;color:#cbd5e1"></i>
                <p class="mt-3">AI Mentor bilan suhbatni boshlang.<br>U sizning maqsadlaringizga mos reja tuzib beradi.</p>
              </div>

              <div
                v-for="msg in messages"
                :key="msg.id"
                :class="['chat-bubble-wrapper', msg.is_user ? 'user-msg' : 'ai-msg']"
              >
                <div class="chat-bubble shadow-sm">
                  <div v-html="renderMarkdown(msg.text)"></div>
                  <div class="msg-time text-end mt-1">{{ formatTime(msg.created_at) }}</div>
                </div>
              </div>

              <div v-if="isLoading" class="ai-typing ms-2">
                <span class="dot"></span><span class="dot"></span><span class="dot"></span>
              </div>
            </div>

            <!-- Input -->
            <div class="card-footer bg-white border-0 p-3">
              <form @submit.prevent="sendMessage" class="input-group">
                <input
                  v-model="userInput"
                  type="text"
                  class="form-control rounded-pill-start border-light-subtle px-4"
                  placeholder="Maqsadingiz yoki savolingizni yozing..."
                  :disabled="isLoading"
                />
                <button class="btn btn-primary rounded-pill-end px-4" type="submit" :disabled="!userInput.trim() || isLoading">
                  <i class="bi bi-send"></i>
                </button>
              </form>
            </div>
          </div>
        </div>

        <!-- YO'L XARITASI -->
        <div class="col-lg-4">
          <div class="card border-0 shadow-lg glass-morph p-4 h-100">
            <h5 class="fw-bold mb-4">
              <i class="bi bi-geo-alt-fill text-warning me-2"></i> Yo'l xaritasi
            </h5>

            <div v-if="messages.length === 0" class="text-center py-4">
              <p class="text-muted small">Mentor bilan suhbatlashishni boshlang. Rejangiz shu yerda paydo bo'bali.</p>
            </div>

            <div v-else>
              <div class="alert border-0 rounded-4 p-3 small" style="background:#fffbeb;color:#92400e">
                <i class="bi bi-info-circle-fill me-1"></i>
                Mentor siz bergan savollarga qarab individual reja tuzib beradi.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue';

const api = useApi();

const userInput = ref('');
const messages = ref([]);
const isLoading = ref(false);
const chatContainer = ref(null);

const scrollToBottom = async () => {
  await nextTick();
  if (chatContainer.value) chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
};

onMounted(async () => {
  try {
    const res = await api.get('/mentorship-chat/');
    messages.value = res.data.results || res.data;
    scrollToBottom();
  } catch (e) { 
    console.error("Error fetching mentorship history:", e);
  }
});

const sendMessage = async () => {
  if (!userInput.value.trim() || isLoading.value) return;
  const text = userInput.value;
  userInput.value = '';
  isLoading.value = true;
  messages.value.push({ id: Date.now(), is_user: true, text, created_at: new Date().toISOString() });
  scrollToBottom();

  try {
    const res = await api.post('/mentorship-chat/', { text });
    messages.value.push(res.data);
    scrollToBottom();
  } catch (e) {
    console.error("Error sending mentor message:", e);
  } finally {
    isLoading.value = false;
  }
};

const resetSession = () => {
  if (confirm("Mentor bilan yangidan boshlamoqchimisiz?")) messages.value = [];
};

const formatTime = (iso) => {
  if (!iso) return '';
  const d = new Date(iso);
  return `${d.getHours().toString().padStart(2,'0')}:${d.getMinutes().toString().padStart(2,'0')}`;
};

const renderMarkdown = (text) => {
  if (!text) return '';
  return text
    .replace(/^# (.*$)/gim, '<h4 class="fw-bold">$1</h4>')
    .replace(/^## (.*$)/gim, '<h5 class="fw-bold">$1</h5>')
    .replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>')
    .replace(/\n/g, '<br/>');
};
</script>
