<template>
  <div class="quiz-container py-5">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-lg-8 col-xl-7">
          
          <!-- Bosh sahifa (Mavzu tanlash) -->
          <div v-if="!isQuizStarted && !isQuizFinished" class="card theme-card shadow-sm border-0 rounded-4 p-4 p-md-5">
            <div class="text-center mb-4">
              <div class="icon-circle mx-auto mb-3">
                <i class="bi bi-controller fs-2"></i>
              </div>
              <h2 class="fw-bold text-main">Smart Edu Viktorina</h2>
              <p class="text-muted">Aql-zakovatingizni sinab ko'ring va XP ballarini ishlang!</p>
            </div>

            <div class="mb-4">
              <label class="form-label fw-semibold text-main">Qaysi mavzuda test ishlaysiz?</label>
              <!-- Custom dropdown -->
              <div class="custom-dropdown" :class="{ open: dropdownOpen }">
                <button 
                  type="button"
                  class="dropdown-toggle-btn"
                  @click="dropdownOpen = !dropdownOpen"
                >
                  <span>{{ selectedTopic }}</span>
                  <i class="bi bi-chevron-down dropdown-arrow"></i>
                </button>
                <ul v-show="dropdownOpen" class="dropdown-menu-list">
                  <li 
                    v-for="topic in topics" 
                    :key="topic"
                    @click="selectTopic(topic)"
                    :class="{ active: selectedTopic === topic }"
                  >
                    <i class="bi bi-bookmark-star me-2"></i>{{ topic }}
                  </li>
                </ul>
              </div>
            </div>

            <button 
              @click="startQuiz" 
              class="btn btn-bg btn-lg w-100 rounded-pill fw-bold"
              :disabled="loading"
            >
              <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
              {{ loading ? "Test yaratilmoqda..." : "Boshlash!" }}
            </button>
          </div>

          <!-- Test jarayoni -->
          <div v-else-if="isQuizStarted && !isQuizFinished" class="card theme-card shadow-sm border-0 rounded-4 p-4 p-md-5 position-relative overflow-hidden">
            <!-- Progress bar -->
            <div class="progress" style="height: 6px; position: absolute; top: 0; left: 0; right: 0; border-radius: 0;">
              <div class="progress-bar progress-bar-themed transition-all" :style="{ width: progressPercentage + '%' }"></div>
            </div>

            <div class="d-flex justify-content-between align-items-center mb-4 mt-2">
              <span class="badge quiz-badge px-3 py-2 fs-6">
                Savol {{ currentQuestionIndex + 1 }} / {{ questions.length }}
              </span>
              <span class="text-muted fw-semibold">
                <i class="bi bi-bookmark-star text-warning"></i> {{ selectedTopic }}
              </span>
            </div>

            <h4 class="fw-bold mb-4 text-main" style="line-height: 1.5;">
              {{ currentQuestion.question }}
            </h4>

            <div class="options-list d-flex flex-column gap-3">
              <button 
                v-for="(optionText, optionKey) in currentQuestion.options" 
                :key="optionKey"
                @click="selectOption(optionKey)"
                class="btn option-btn text-start p-3 rounded-4 d-flex align-items-center gap-3 transition-all"
                :class="{
                  'selected': selectedOption === optionKey,
                  'correct': showResult && optionKey === currentQuestion.correct,
                  'wrong': showResult && selectedOption === optionKey && optionKey !== currentQuestion.correct
                }"
                :disabled="showResult"
              >
                <div class="option-letter fw-bold">{{ optionKey }}</div>
                <div class="option-text flex-grow-1">{{ optionText }}</div>
                <i v-if="showResult && optionKey === currentQuestion.correct" class="bi bi-check-circle-fill text-success fs-5"></i>
                <i v-if="showResult && selectedOption === optionKey && optionKey !== currentQuestion.correct" class="bi bi-x-circle-fill text-danger fs-5"></i>
              </button>
            </div>

            <div class="mt-4 pt-3 border-top text-end" v-if="showResult">
              <button @click="nextQuestion" class="btn btn-bg px-4 rounded-pill fw-bold" :disabled="submitLoading">
                <span v-if="submitLoading" class="spinner-border spinner-border-sm me-2"></span>
                {{ currentQuestionIndex === questions.length - 1 ? "Natijani ko'rish" : "Keyingi savol" }} <i v-if="!submitLoading" class="bi bi-arrow-right"></i>
              </button>
            </div>
          </div>

          <!-- Natija -->
          <div v-else-if="isQuizFinished" class="card theme-card shadow-sm border-0 rounded-4 p-4 p-md-5 text-center">
            <div class="mb-4">
              <div class="trophy-icon mx-auto mb-3">🏆</div>
              <h2 class="fw-bold text-main">Tabriklaymiz!</h2>
              <p class="text-muted fs-5">Siz testni yakunladingiz.</p>
            </div>

            <div class="row g-3 justify-content-center mb-4">
              <div class="col-6 col-sm-4">
                <div class="result-card result-score rounded-4 p-3">
                  <div class="text-muted small fw-semibold mb-1">To'g'ri javoblar</div>
                  <h3 class="fw-bold text-success mb-0">{{ score }} / {{ questions.length }}</h3>
                </div>
              </div>
              <div class="col-6 col-sm-4">
                <div class="result-card result-xp rounded-4 p-3">
                  <div class="small fw-semibold mb-1" style="color: var(--primary-light);">Olingan XP</div>
                  <h3 class="fw-bold mb-0" style="color: var(--primary);">+{{ xpEarned }}</h3>
                </div>
              </div>
            </div>

            <button @click="resetQuiz" class="btn btn-bg btn-lg rounded-pill px-5 fw-bold">
              Boshqa test ishlash
            </button>
          </div>

        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useApi } from '~/composables/useApi';

const api = useApi();
const loading = ref(false);
const submitLoading = ref(false);
const dropdownOpen = ref(false);

const topics = [
  'Dasturlash asoslari',
  "Sun'iy intellekt",
  "O'zbekiston tarixi",
  'Matematika va mantiq',
  'Axborot xavfsizligi',
  "Oliy ta'lim qoidalari"
];

const selectedTopic = ref('Dasturlash asoslari');
const isQuizStarted = ref(false);
const isQuizFinished = ref(false);

const questions = ref([]);
const currentQuestionIndex = ref(0);
const selectedOption = ref(null);
const showResult = ref(false);
const score = ref(0);
const xpEarned = ref(0);

const currentQuestion = computed(() => questions.value[currentQuestionIndex.value] || {});
const progressPercentage = computed(() => ((currentQuestionIndex.value + (showResult.value ? 1 : 0)) / questions.value.length) * 100);

const selectTopic = (topic) => {
  selectedTopic.value = topic;
  dropdownOpen.value = false;
};

const startQuiz = async () => {
  loading.value = true;
  try {
    const res = await api.get('/ai/quiz/generate/', {
      params: { topic: selectedTopic.value }
    });
    
    if (res.data && Array.isArray(res.data) && res.data.length > 0) {
      questions.value = res.data;
      currentQuestionIndex.value = 0;
      score.value = 0;
      isQuizStarted.value = true;
      isQuizFinished.value = false;
      showResult.value = false;
      selectedOption.value = null;
    } else {
      alert("Savollarni yaratishda xatolik yuz berdi. Iltimos qaytadan urinib ko'ring.");
    }
  } catch (error) {
    console.error("Quiz generate error:", error);
    alert("Xatolik yuz berdi. Iltimos keyinroq qayta urinib ko'ring.");
  } finally {
    loading.value = false;
  }
};

const selectOption = (optionKey) => {
  if (showResult.value) return;
  selectedOption.value = optionKey;
  showResult.value = true;
  
  if (optionKey === currentQuestion.value.correct) {
    score.value++;
  }
};

const nextQuestion = async () => {
  if (currentQuestionIndex.value < questions.value.length - 1) {
    currentQuestionIndex.value++;
    selectedOption.value = null;
    showResult.value = false;
  } else {
    // Finish quiz and submit score
    await submitScore();
  }
};

const submitScore = async () => {
  submitLoading.value = true;
  try {
    const res = await api.post('/ai/quiz/submit/', {
      topic: selectedTopic.value,
      score: score.value,
      total_questions: questions.value.length
    });
    
    xpEarned.value = res.data.xp_earned;
    isQuizFinished.value = true;
  } catch (error) {
    console.error("Submit error:", error);
    alert("Natijani saqlashda xatolik yuz berdi.");
  } finally {
    submitLoading.value = false;
  }
};

const resetQuiz = () => {
  isQuizStarted.value = false;
  isQuizFinished.value = false;
  questions.value = [];
};
</script>

<style scoped>
.quiz-container {
  min-height: 80vh;
  background-color: var(--bg-app);
}

.icon-circle {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(var(--primary-rgb), 0.1), rgba(var(--accent-rgb), 0.1));
  color: var(--primary);
}

/* Custom Dropdown */
.custom-dropdown {
  position: relative;
}

.dropdown-toggle-btn {
  width: 100%;
  padding: 14px 18px;
  background-color: var(--bg-card);
  border: 2px solid var(--border-color);
  border-radius: var(--radius-md);
  color: var(--text-main);
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: var(--transition-base);
}

.dropdown-toggle-btn:hover {
  border-color: var(--primary-light);
}

.custom-dropdown.open .dropdown-toggle-btn {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(var(--primary-rgb), 0.1);
}

.dropdown-arrow {
  transition: transform 0.3s ease;
}
.custom-dropdown.open .dropdown-arrow {
  transform: rotate(180deg);
}

.dropdown-menu-list {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  right: 0;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
  list-style: none;
  padding: 8px 0;
  margin: 0;
  z-index: 100;
  max-height: 280px;
  overflow-y: auto;
}

.dropdown-menu-list li {
  padding: 12px 18px;
  cursor: pointer;
  color: var(--text-secondary);
  font-weight: 500;
  transition: var(--transition-base);
}

.dropdown-menu-list li:hover {
  background-color: rgba(var(--primary-rgb), 0.06);
  color: var(--primary);
}

.dropdown-menu-list li.active {
  background-color: rgba(var(--primary-rgb), 0.1);
  color: var(--primary);
  font-weight: 600;
}

/* Progress bar */
.progress-bar-themed {
  background: linear-gradient(90deg, var(--primary), var(--primary-light));
}

/* Quiz badge */
.quiz-badge {
  background-color: rgba(var(--primary-rgb), 0.08);
  color: var(--primary);
  border: 1px solid rgba(var(--primary-rgb), 0.15);
}

/* Option buttons */
.option-btn {
  background-color: var(--bg-card);
  border: 2px solid var(--border-color);
  color: var(--text-main);
  transition: all 0.2s ease;
}

.option-btn:hover:not(:disabled) {
  background-color: rgba(var(--primary-rgb), 0.04);
  border-color: rgba(var(--primary-rgb), 0.2);
  transform: translateY(-2px);
}

.option-letter {
  width: 32px;
  height: 32px;
  background-color: rgba(var(--primary-rgb), 0.06);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  font-size: 0.85rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.option-btn.selected:not(.correct):not(.wrong) {
  border-color: var(--primary);
  background-color: rgba(var(--primary-rgb), 0.06);
}
.option-btn.selected:not(.correct):not(.wrong) .option-letter {
  background-color: var(--primary);
  color: white;
}

.option-btn.correct {
  border-color: var(--success);
  background-color: rgba(16, 106, 43, 0.06);
  color: var(--success);
}
.option-btn.correct .option-letter {
  background-color: var(--success);
  color: white;
}

.option-btn.wrong {
  border-color: var(--error);
  background-color: rgba(225, 29, 72, 0.06);
  color: var(--error);
}
.option-btn.wrong .option-letter {
  background-color: var(--error);
  color: white;
}

.option-btn:disabled {
  opacity: 0.9;
  cursor: default;
}

/* Result cards */
.result-card {
  border: 1px solid var(--border-color);
  background-color: var(--bg-card);
}
.result-xp {
  border-color: rgba(var(--primary-rgb), 0.2);
  background-color: rgba(var(--primary-rgb), 0.05);
}

/* Trophy */
.trophy-icon {
  font-size: 72px;
  line-height: 1;
  filter: drop-shadow(0 10px 15px rgba(0,0,0,0.1));
}

.drop-shadow {
  filter: drop-shadow(0 10px 15px rgba(0,0,0,0.1));
}

.transition-all {
  transition: all 0.25s ease;
}
</style>
