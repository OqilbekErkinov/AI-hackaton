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
                <div class="message-bubble shadow-sm position-relative" :class="[msg.is_user ? 'user-bubble' : 'ai-bubble', activeMode, msg.is_voice ? 'voice-bubble' : 'p-3']">
                  
                  <!-- 🎤 OVOZLI XABAR (Telegram uslubida) -->
                  <div v-if="msg.is_voice" class="voice-message-player d-flex align-items-center gap-2">
                    <button
                      class="voice-play-btn"
                      :class="currentlyPlaying === (msg.local_audio_url || msg.audio_url) ? 'playing' : ''"
                      @click="playVoiceMsg(msg)"
                    >
                      <i class="bi" :class="currentlyPlaying === (msg.local_audio_url || msg.audio_url) ? 'bi-pause-fill' : 'bi-play-fill'"></i>
                    </button>
                    <div class="voice-waveform flex-grow-1">
                      <span v-for="n in 20" :key="n" class="waveform-bar" :style="{ height: (Math.sin(n * 0.8) * 50 + 55) + '%', animationDelay: (n * 0.05) + 's' }"></span>
                    </div>
                    <span class="voice-duration small fw-semibold">{{ msg.duration || '0:00' }}</span>
                  </div>

                  <!-- 💬 MATN XABAR -->
                  <div v-else class="message-text" v-html="formatText(msg.text)"></div>
                  
                  <!-- Vaqt + Tinglash (faqat AI ovozli javoblar uchun) -->
                  <div class="d-flex align-items-center justify-content-between mt-2 flex-wrap gap-2 border-top pt-2 opacity-75" :class="msg.is_voice ? 'px-1' : ''" style="font-size: 0.75rem;">
                    <span>{{ formatTime(msg.created_at) }}</span>
                    <!-- "Tinglash" faqat ovozli AI javoblar uchun (is_voice && !is_user && audio_url) -->
                    <button 
                      v-if="!msg.is_user && msg.is_voice && msg.audio_url" 
                      class="btn btn-xs btn-outline-light-hover rounded-pill px-2 py-0 d-flex align-items-center gap-1 text-muted"
                      @click="playAudio(msg.audio_url)"
                    >
                      <i class="bi" :class="currentlyPlaying === msg.audio_url ? 'bi-pause-fill text-danger' : 'bi-play-fill text-success'"></i>
                      <span>{{ currentlyPlaying === msg.audio_url ? 'To\'xtatish' : 'Ijro' }}</span>
                    </button>
                  </div>
                </div>
              </div>

              <!-- Yuborilmoqda animatsiyasi -->
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
const config = useRuntimeConfig();
// API baza manzilidan media URL ni olish (masalan: http://127.0.0.1:9000)
const API_MEDIA_BASE = (config.public.apiUrl || 'http://127.0.0.1:9000/api').replace('/api', '');

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
    // Matn yuborilsa: audio sintez qilinmaydi (faqat ovozli so'rov bo'lganda audio keladi)
    const res = await api.post('/ai-chat/', { 
      text,
      mode: activeMode.value,
      voice_synthesize: false  // Matn so'rovida audio kerak emas
    });
    
    messages.value.push(res.data);
    scrollToBottom();

    // Matn so'rovda audio AVTOMATIK ijro bo'lmaydi
    // Foydalanuvchi xohlasa "Tinglash" tugmasini bosadi
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
  // Bo'sh audio bo'lsa yubormaymiz
  if (!audioBlob || audioBlob.size < 1000) {
    messages.value.push({
      text: '🎤 Ovoz juda qisqa. Iltimos qayta urinib ko\'ring.',
      is_user: false, is_voice: false,
      created_at: new Date().toISOString(),
      mode: activeMode.value
    });
    return;
  }

  sending.value = true;
  const formData = new FormData();
  const ext = audioBlob.type.includes('ogg') ? 'ogg' : audioBlob.type.includes('mp4') ? 'mp4' : 'webm';
  formData.append("audio", audioBlob, `recording.${ext}`);
  formData.append("mode", activeMode.value);
  formData.append("voice_synthesize", "true");

  const now = new Date().toISOString();
  // Local blob URL — foydalanuvchi o'z ovozini qayta eshitishi uchun
  const localBlobUrl = URL.createObjectURL(audioBlob);
  const durationStr = recordingDuration.value > 0 
    ? `0:${String(recordingDuration.value).padStart(2, '0')}`
    : '0:00';

  // Ovozli xabar Telegram uslubida (matn emas)
  const placeholderIndex = messages.value.push({ 
    text: null,
    is_user: true, 
    is_voice: true,
    local_audio_url: localBlobUrl,
    duration: durationStr,
    _sending: true,  // Yuborilmoqda holati
    created_at: now,
    mode: activeMode.value 
  }) - 1;
  
  scrollToBottom();

  try {
    const res = await api.post('/ai-chat/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    
    // User bubble: ovozli ko'rinish saqlanadi, faqat _sending olib tashlanadi
    messages.value[placeholderIndex]._sending = false;
    
    // AI javobi ham ovozli bubble sifatida
    messages.value.push({
      ...res.data,
      is_voice: true,  // AI javobi ham ovozli xabar sifatida ko'rinsin
      duration: null   // AI javob uzunligini frontend da bilmaymiz
    });
    scrollToBottom();

    // AI ovozli javobi AVTOMATIK ijro
    if (res.data.audio_url) {
      playAudio(res.data.audio_url);
    }
  } catch (e) {
    console.error("STT error:", e.response?.data || e.message);
    const errMsg = e.response?.data?.error || 'Ovozli xabar yuborishda xatolik.';
    messages.value[placeholderIndex].is_voice = false;
    messages.value[placeholderIndex].text = `🎤 ${errMsg}`;
    messages.value[placeholderIndex]._sending = false;
  } finally {
    sending.value = false;
  }
};

// Ovozli xabar play tugmasi (user o'z ovozini eshitishi)
const playVoiceMsg = (msg) => {
  const url = msg.local_audio_url || msg.audio_url;
  if (!url) return;
  playAudio(url);
};

const playAudio = (url) => {
  if (audioPlayer) {
    audioPlayer.pause();
  }
  
  if (currentlyPlaying.value === url) {
    currentlyPlaying.value = null;
    return;
  }

  currentlyPlaying.value = url;
  
  // Backend bazaviy URL ulash (runtimeConfig dan dinamik ravishda)
  const absoluteUrl = url.startsWith('http') ? url : `${API_MEDIA_BASE}${url}`;
  console.log('Playing audio URL:', absoluteUrl);
  audioPlayer = new Audio(absoluteUrl);
  audioPlayer.play().catch(err => {
    console.error("Audio play error:", err);
    currentlyPlaying.value = null;
  });
  
  audioPlayer.onended = () => {
    currentlyPlaying.value = null;
  };
  
  audioPlayer.onerror = (e) => {
    console.error("Audio load error:", e, absoluteUrl);
    currentlyPlaying.value = null;
  };
};

// "Tinglash" tugmasi bosilganda: audio bo'lsa eshit, bo'lmasa TTS so'ra
const listenMessage = async (msg) => {
  if (msg.audio_url) {
    // Audio allaqachon mavjud — to'g'ridan-to'g'ri ijro et
    playAudio(msg.audio_url);
    return;
  }
  
  // Agar audio URL yo'q bo'lsa (matn xabari) — on-demand TTS so'raymiz
  if (msg._fetchingAudio) return;
  msg._fetchingAudio = true;
  
  try {
    const res = await api.post('/ai/tts/', { text: msg.text });
    if (res.data.audio_url) {
      msg.audio_url = res.data.audio_url;
      playAudio(res.data.audio_url);
    }
  } catch (e) {
    // TTS endpointi bo'lmasa — frontend-dan to'g'ridan-to'g'ri Web Speech API ishlatamiz
    console.warn("TTS endpoint not available, using Web Speech API:", e.message);
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(msg.text);
      utterance.lang = 'uz-UZ';
      utterance.rate = 0.9;
      currentlyPlaying.value = msg.id || msg.text.substring(0, 20);
      utterance.onend = () => { currentlyPlaying.value = null; };
      window.speechSynthesis.speak(utterance);
    }
  } finally {
    msg._fetchingAudio = false;
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
/* ======= OVOZLI XABAR BUBBLE (Telegram uslubi) ======= */
.voice-bubble {
  padding: 10px 14px !important;
  min-width: 200px;
  max-width: 300px;
}

.voice-message-player {
  min-width: 200px;
}

.voice-play-btn {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  border: none;
  background: rgba(255,255,255,0.25);
  color: inherit;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  cursor: pointer;
  flex-shrink: 0;
  transition: all 0.2s ease;
}

.user-bubble .voice-play-btn {
  background: rgba(255,255,255,0.2);
  color: #fff;
}

.ai-bubble .voice-play-btn {
  background: var(--primary-light);
  color: var(--primary);
}

.voice-play-btn.playing {
  background: var(--primary) !important;
  color: #fff !important;
}

.voice-play-btn:hover {
  transform: scale(1.05);
  opacity: 0.9;
}

.voice-waveform {
  display: flex;
  align-items: center;
  gap: 2px;
  height: 28px;
}

.waveform-bar {
  display: inline-block;
  width: 3px;
  border-radius: 3px;
  background: currentColor;
  opacity: 0.5;
  transition: height 0.1s ease;
}

/* Ijro bo'layotganda animatsiya */
.voice-play-btn.playing ~ .voice-waveform .waveform-bar {
  animation: waveAnim 1s ease-in-out infinite alternate;
  opacity: 0.9;
}

@keyframes waveAnim {
  0% { opacity: 0.4; transform: scaleY(0.6); }
  100% { opacity: 1; transform: scaleY(1); }
}

.voice-duration {
  font-size: 0.72rem;
  opacity: 0.8;
  flex-shrink: 0;
}
</style>
