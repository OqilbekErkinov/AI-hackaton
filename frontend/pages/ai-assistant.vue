<template>
  <div class="ai-assistant-container p-3 p-md-4" :class="activeMode">
    <div class="row g-4 h-100">

      <!-- CHAT QISMI -->
      <div class="col-lg-8 d-flex flex-column h-100">
        <div class="card chat-card border-0 shadow-sm flex-grow-1 overflow-hidden">
          <!-- Sarlavha -->
          <div class="card-header bg-white border-bottom py-3 d-flex align-items-center justify-content-between flex-wrap gap-2">
            <div class="d-flex align-items-center">
              <div class="ai-avatar me-3" :class="activeMode">
                <i class="bi" :class="activeMode === 'law' ? 'bi-journal-bookmark-fill' : 'bi-robot'"></i>
              </div>
              <div>
                <h5 class="mb-0 fw-bold header-title">
                  {{ activeMode === 'law' ? 'Adliya & Nizomlar AI' : 'AI Yordamchi (Mentor)' }}
                </h5>
                <small class="text-success">
                  <i class="bi bi-circle-fill me-1" style="font-size:0.5rem"></i> Onlayn
                </small>
              </div>
            </div>

            <!-- Rejim almashtirgich (Tabs) -->
            <div class="mode-tabs bg-light p-1 rounded-3 d-flex align-items-center shadow-2xs">
              <button 
                class="btn btn-sm px-3 rounded-2 fw-bold transition-all"
                :class="activeMode === 'mentor' ? 'btn-primary shadow-sm text-white' : 'btn-link text-muted text-decoration-none'"
                @click="switchMode('mentor')"
              >
                <i class="bi bi-person-fill-gear me-1"></i> Mentor
              </button>
              <button 
                class="btn btn-sm px-3 rounded-2 fw-bold transition-all"
                :class="activeMode === 'law' ? 'btn-teal shadow-sm text-white' : 'btn-link text-muted text-decoration-none'"
                @click="switchMode('law')"
              >
                <i class="bi bi-shield-fill-check me-1"></i> Qonunchilik (RAG)
              </button>
            </div>

            <button class="btn btn-light btn-sm text-danger" @click="clearChat" title="Tarixni tozalash">
              <i class="bi bi-trash"></i>
            </button>
          </div>

          <!-- Xabarlar ro'yxati -->
          <div class="card-body chat-body p-0 overflow-y-auto" ref="chatBody">
            <div v-if="loadingHistory" class="p-4 text-center">
              <div class="spinner-border spinner-border-sm text-primary" :class="activeMode === 'law' ? 'text-teal-color' : ''"></div>
            </div>

            <div v-else-if="messages.length === 0" class="empty-chat p-5 text-center">
              <div class="empty-icon mb-3" :class="activeMode">
                <i class="bi" :class="activeMode === 'law' ? 'bi-journal-bookmark-fill' : 'bi-chat-dots'"></i>
              </div>
              <h6 class="fw-bold text-muted">
                {{ activeMode === 'law' ? 'Oliy ta\'lim qonunchiligi bo\'yicha savolingiz bormi?' : 'Salom! Qanday yordam bera olaman?' }}
              </h6>
              <p class="text-muted small px-3">
                {{ activeMode === 'law' ? 'O\'qishni ko\'chirish, stipendiya ballari, ECTS kreditlar yoki dress-kod qoidalari haqida so\'rang.' : 'Masalan: "Menga mos stipendiyalar bormi?" deb so\'rang.' }}
              </p>
            </div>

            <div v-else class="p-3 p-md-4">
              <div
                v-for="(msg, idx) in messages"
                :key="idx"
                class="message-wrapper mb-4"
                :class="msg.is_user ? 'user-message' : 'ai-message'"
              >
                <div class="message-bubble shadow-sm p-3 position-relative" :class="[msg.is_user ? 'user-bubble' : 'ai-bubble', activeMode]">
                  <div class="message-text" v-html="formatText(msg.text)"></div>
                  
                  <div class="d-flex align-items-center justify-content-between mt-2 flex-wrap gap-2 border-top pt-2 opacity-75" style="font-size: 0.75rem;">
                    <span>{{ formatTime(msg.created_at) }}</span>
                    
                    <!-- TTS Ovozli eshitish tugmasi -->
                    <button 
                      v-if="!msg.is_user && msg.audio_url" 
                      class="btn btn-xs btn-outline-light-hover rounded-pill px-2 py-0.5 d-flex align-items-center gap-1 text-decoration-none text-muted"
                      @click="playAudio(msg.audio_url)"
                    >
                      <i class="bi" :class="currentlyPlaying === msg.audio_url ? 'bi-volume-mute-fill text-danger' : 'bi-volume-up-fill text-success'"></i>
                      <span>{{ currentlyPlaying === msg.audio_url ? 'To\'xtatish' : 'Tinglash' }}</span>
                    </button>
                  </div>
                </div>
              </div>

              <!-- Yozmoqda animatsiyasi -->
              <div v-if="sending" class="message-wrapper ai-message mb-4">
                <div class="message-bubble shadow-sm p-3 typing-bubble" :class="activeMode">
                  <span class="dot"></span><span class="dot"></span><span class="dot"></span>
                </div>
              </div>
            </div>
          </div>

          <!-- Input -->
          <div class="card-footer bg-white border-top p-3">
            <!-- Ovoz yozilayotgan paytdagi to'lqinsimon premium interfeys -->
            <div v-if="isRecording" class="recording-panel d-flex align-items-center justify-content-between p-2 mb-2 bg-danger-subtle rounded-3 border border-danger-subtle animate-pulse">
              <div class="d-flex align-items-center gap-2">
                <span class="recording-indicator"></span>
                <span class="text-danger fw-bold small">Ovoz yozilmoqda... ({{ recordingDuration }}s)</span>
              </div>
              <div class="d-flex gap-2">
                <button type="button" class="btn btn-sm btn-danger px-3 rounded-2 fw-bold" @click="stopRecording">
                  <i class="bi bi-stop-fill me-1"></i> Yuborish
                </button>
                <button type="button" class="btn btn-sm btn-light px-2 rounded-2" @click="cancelRecording">
                  Bekor qilish
                </button>
              </div>
            </div>

            <form @submit.prevent="sendMessage" class="d-flex gap-2 align-items-center" v-if="!isRecording">
              <!-- Ovoz yozish tugmasi (Microphone) -->
              <button 
                type="button" 
                class="btn mic-btn shadow-2xs rounded-3 border"
                :class="activeMode === 'law' ? 'btn-outline-teal' : 'btn-outline-primary'"
                @click="startRecording"
                title="Ovozli savol yo'llash"
              >
                <i class="bi bi-mic-fill"></i>
              </button>

              <input
                v-model="userInput"
                type="text"
                class="form-control chat-input border-0 bg-light py-2 px-3 rounded-3"
                :placeholder="activeMode === 'law' ? 'Oliy ta\'lim nizomi bo\'yicha savolingizni yozing...' : 'Mentorga savol yozing...'"
                :disabled="sending"
              />
              
              <button 
                type="submit" 
                class="btn send-btn px-4 py-2 rounded-3 text-white" 
                :class="activeMode === 'law' ? 'btn-teal' : 'btn-primary'"
                :disabled="sending || !userInput.trim()"
              >
                <i class="bi bi-send-fill" v-if="!sending"></i>
                <div v-else class="spinner-border spinner-border-sm"></div>
              </button>
            </form>
          </div>
        </div>
      </div>

      <!-- YON PANEL -->
      <div class="col-lg-4">
        <!-- Rejimga mos premium RAG yo'riqnomasi -->
        <div v-if="activeMode === 'law'" class="card border-0 shadow-sm mb-4 bg-teal-subtle text-teal-dark">
          <div class="card-body">
            <h6 class="fw-bold mb-3 d-flex align-items-center">
              <i class="bi bi-shield-fill-check me-2 fs-5"></i> RAG Adliya Tizimi Haqida
            </h6>
            <p class="small mb-3" style="line-height:1.5">
              Ushbu rejim oliy ta'limga oid rasmiy me'yoriy-huquqiy hujjatlarga asoslangan:
            </p>
            <ul class="small ps-3 mb-0" style="line-height:1.6">
              <li>Stipendiya tayinlash va toifa ballari;</li>
              <li>O'qishni ko'chirish va qayta tiklash;</li>
              <li>ECTS GPA baholash qoidalari;</li>
              <li>Odob-axloq va ichki tartib normalari.</li>
            </ul>
            <div class="mt-3 p-2 bg-white rounded-3 border small">
              <strong>Eslatma:</strong> AI faqat tasdiqlangan nizomlar doirasida javob beradi va yolg'on ma'lumot to'qimaydi.
            </div>
          </div>
        </div>

        <div class="card border-0 shadow-sm mb-4" v-else>
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

        <div class="card border-0 bg-primary-subtle shadow-sm text-primary-dark">
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

// Rejim holati (mentor yoki law)
const activeMode = ref('mentor');

// Ovoz yozish holatlari (STT)
const isRecording = ref(false);
const recordingDuration = ref(0);
let mediaRecorder = null;
let audioChunks = [];
let durationInterval = null;
let streamRef = null;

// Ovozli javob ijro etish holatlasi (TTS)
const currentlyPlaying = ref(null);
let audioPlayer = null;

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

// Rejimni almashtirish
const switchMode = async (mode) => {
  if (activeMode.value === mode) return;
  
  // Eshitilayotgan audioni to'xtatish
  if (audioPlayer) {
    audioPlayer.pause();
    currentlyPlaying.value = null;
  }
  
  activeMode.value = mode;
  messages.value = [];
  await fetchHistory();
};

const fetchHistory = async () => {
  loadingHistory.value = true;
  try {
    const res = await api.get('/ai-chat/', {
      params: { mode: activeMode.value }
    });
    messages.value = res.data.results || res.data;
    scrollToBottom();
  } catch (e) {
    console.error("Error fetching chat history:", e);
  } finally {
    loadingHistory.value = false;
  }
};

const sendMessage = async () => {
  if (!userInput.value.trim() || sending.value) return;
  const text = userInput.value;
  userInput.value = '';
  const now = new Date().toISOString();
  
  // Xabarni vaqtincha push qilish
  messages.value.push({ text, is_user: true, created_at: now, mode: activeMode.value });
  scrollToBottom();
  
  sending.value = true;
  try {
    // Law rejimida ovozli javobni default yoqamiz
    const voiceSynthesize = activeMode.value === 'law';
    
    const res = await api.post('/ai-chat/', { 
      text,
      mode: activeMode.value,
      voice_synthesize
    });
    
    messages.value.push(res.data);
    scrollToBottom();

    // Avtomatik audio ijro
    if (res.data.audio_url) {
      playAudio(res.data.audio_url);
    }
  } catch (e) {
    messages.value.push({ 
      text: "Uzr, tizimda xatolik yuz berdi.", 
      is_user: false, 
      created_at: new Date().toISOString(),
      mode: activeMode.value
    });
  } finally {
    sending.value = false;
  }
};

// Ovoz yozishni boshlash (STT)
const startRecording = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    streamRef = stream;
    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];
    recordingDuration.value = 0;
    
    mediaRecorder.ondataavailable = (event) => {
      audioChunks.push(event.data);
    };

    mediaRecorder.onstop = async () => {
      const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
      await sendVoiceMessage(audioBlob);
      // Mikrofonni yopish
      if (streamRef) {
        streamRef.getTracks().forEach(track => track.stop());
      }
    };

    mediaRecorder.start();
    isRecording.value = true;
    durationInterval = setInterval(() => {
      recordingDuration.value++;
    }, 1000);
  } catch (err) {
    console.error("Microphone error:", err);
    alert("Mikrofon ruxsati berilmadi yoki qurilmangizda xatolik mavjud.");
  }
};

// Ovoz yozishni yakunlash va yuborish
const stopRecording = () => {
  if (mediaRecorder && isRecording.value) {
    mediaRecorder.stop();
    isRecording.value = false;
    clearInterval(durationInterval);
  }
};

// Ovoz yozishni bekor qilish
const cancelRecording = () => {
  if (mediaRecorder && isRecording.value) {
    mediaRecorder.onstop = null; // Yubormaslik uchun hodisani tozalaymiz
    mediaRecorder.stop();
    isRecording.value = false;
    clearInterval(durationInterval);
    if (streamRef) {
      streamRef.getTracks().forEach(track => track.stop());
    }
  }
};

// Ovozli xabarni yuborish servisi
const sendVoiceMessage = async (audioBlob) => {
  sending.value = true;
  const formData = new FormData();
  formData.append("audio", audioBlob, "recording.webm");
  formData.append("mode", activeMode.value);
  formData.append("voice_synthesize", "true"); // Ovozli so'rovda doimo javob ovozli bo'ladi

  const now = new Date().toISOString();
  // Transkripsiya kutish vaqtida placeholder
  const placeholderIndex = messages.value.push({ 
    text: "🎤 Ovoz yozildi, matnga o'girilmoqda...", 
    is_user: true, 
    created_at: now,
    mode: activeMode.value 
  }) - 1;
  
  scrollToBottom();

  try {
    const res = await api.post('/ai-chat/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    
    // User xabari o'rniga Whisper qaytargan transkripsiyani qo'yamiz
    if (res.data.user_transcription) {
      messages.value[placeholderIndex].text = res.data.user_transcription;
    } else {
      messages.value[placeholderIndex].text = "Ovozli xabar yuborildi.";
    }
    
    messages.value.push(res.data);
    scrollToBottom();

    // Avtomatik audio ijro
    if (res.data.audio_url) {
      playAudio(res.data.audio_url);
    }
  } catch (e) {
    console.error("STT network error:", e);
    messages.value[placeholderIndex].text = "🎤 Ovozli xabarni yuborishda muammo yuz berdi.";
  } finally {
    sending.value = false;
  }
};

// TTS Ovozli eshitish funksiyasi
const playAudio = (url) => {
  if (audioPlayer) {
    audioPlayer.pause();
  }
  
  if (currentlyPlaying.value === url) {
    currentlyPlaying.value = null;
    return;
  }

  currentlyPlaying.value = url;
  
  // Backend bazaviy URL ulash
  const absoluteUrl = url.startsWith('http') ? url : `http://127.0.0.1:8000${url}`;
  audioPlayer = new Audio(absoluteUrl);
  audioPlayer.play().catch(err => {
    console.error("Audio play error:", err);
    currentlyPlaying.value = null;
  });
  
  audioPlayer.onended = () => {
    currentlyPlaying.value = null;
  };
  
  audioPlayer.onerror = () => {
    currentlyPlaying.value = null;
  };
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

<style scoped>
.btn-teal {
  background-color: #0d9488 !important;
  color: #fff !important;
  border-color: #0d9488 !important;
}
.btn-teal:hover {
  background-color: #0f766e !important;
  border-color: #0f766e !important;
}

.text-teal-color {
  color: #0d9488 !important;
}

.bg-teal-subtle {
  background-color: #f0fdfa !important;
  border: 1px solid #ccfbf1 !important;
}

.text-teal-dark {
  color: #115e59 !important;
}

/* AI Avatar styles */
.ai-avatar {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  background-color: var(--primary-light);
  color: var(--primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  transition: all 0.3s ease;
}

.ai-avatar.law {
  background-color: #ccfbf1 !important;
  color: #0d9488 !important;
}

/* Chat bubble styling overrides */
.ai-bubble.law {
  border-left: 4px solid #0d9488 !important;
}

.interest-chip {
  background-color: var(--primary-light);
  color: var(--primary);
  font-weight: 600;
  padding: 6px 12px;
  border-radius: 20px;
}

.transition-all {
  transition: all 0.25s ease-in-out;
}

.mic-btn {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  font-size: 18px;
  transition: all 0.2s ease;
}

.btn-outline-teal {
  color: #0d9488;
  border-color: #ccfbf1;
  background-color: #f0fdfa;
}

.btn-outline-teal:hover {
  background-color: #0d9488;
  color: #fff;
  border-color: #0d9488;
}

/* Waveform recording animation */
.animate-pulse {
  animation: pulse 1.8s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: .6;
  }
}

.recording-indicator {
  width: 10px;
  height: 10px;
  background-color: #ef4444;
  border-radius: 50%;
  display: inline-block;
  animation: blink 1s infinite;
}

@keyframes blink {
  50% {
    opacity: 0;
  }
}

.btn-outline-light-hover {
  background-color: rgba(0, 0, 0, 0.03);
  border: 1px solid rgba(0, 0, 0, 0.08);
  transition: all 0.15s ease;
}

.btn-outline-light-hover:hover {
  background-color: rgba(0, 0, 0, 0.06);
}

.pulsing-icon {
  animation: pulse-icon 1s infinite alternate;
}

@keyframes pulse-icon {
  from {
    transform: scale(1);
  }
  to {
    transform: scale(1.15);
  }
}
</style>
