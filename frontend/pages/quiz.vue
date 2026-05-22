<template>
  <div class="quiz-container py-5">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-lg-8 col-xl-7">
          
          <!-- Bosh sahifa (Mavzu tanlash) -->
          <div v-if="!isQuizStarted && !isQuizFinished" class="card shadow-sm border-0 rounded-4 p-4 p-md-5">
            <div class="text-center mb-4">
              <div class="icon-circle bg-primary bg-opacity-10 text-primary mx-auto mb-3">
                <i class="bi bi-controller fs-2"></i>
              </div>
              <h2 class="fw-bold">Smart Edu Viktorina</h2>
              <p class="text-muted">Aql-zakovatingizni sinab ko'ring va XP ballarini ishlang!</p>
            </div>

            <div class="mb-4">
              <label class="form-label fw-semibold">Qaysi mavzuda test ishlaysiz?</label>
              <select v-model="selectedTopic" class="form-select form-select-lg">
                <option value="Dasturlash asoslari">Dasturlash asoslari</option>
                <option value="Sun'iy intellekt">Sun'iy intellekt</option>
                <option value="O'zbekiston tarixi">O'zbekiston tarixi</option>
                <option value="Matematika va mantiq">Matematika va mantiq</option>
                <option value="Axborot xavfsizligi">Axborot xavfsizligi</option>
                <option value="Oliy ta'lim qoidalari">Oliy ta'lim qoidalari</option>
              </select>
            </div>

            <button 
              @click="startQuiz" 
              class="btn btn-primary btn-lg w-100 rounded-pill fw-bold"
              :disabled="loading"
            >
              <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
              {{ loading ? "Test yaratilmoqda..." : "Boshlash!" }}
            </button>
          </div>

          <!-- Test jarayoni -->
          <div v-else-if="isQuizStarted && !isQuizFinished" class="card shadow-sm border-0 rounded-4 p-4 p-md-5 position-relative overflow-hidden">
            <!-- Progress bar -->
            <div class="progress" style="height: 6px; position: absolute; top: 0; left: 0; right: 0; border-radius: 0;">
              <div class="progress-bar bg-success transition-all" :style="{ width: progressPercentage + '%' }"></div>
            </div>

            <div class="d-flex justify-content-between align-items-center mb-4 mt-2">
              <span class="badge bg-light text-dark border px-3 py-2 fs-6">
                Savol {{ currentQuestionIndex + 1 }} / {{ questions.length }}
              </span>
              <span class="text-muted fw-semibold">
                <i class="bi bi-bookmark-star text-warning"></i> {{ selectedTopic }}
              </span>
            </div>

            <h4 class="fw-bold mb-4" style="line-height: 1.5;">
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
              <button @click="nextQuestion" class="btn btn-primary px-4 rounded-pill fw-bold" :disabled="submitLoading">
                <span v-if="submitLoading" class="spinner-border spinner-border-sm me-2"></span>
                {{ currentQuestionIndex === questions.length - 1 ? "Natijani ko'rish" : "Keyingi savol" }} <i v-if="!submitLoading" class="bi bi-arrow-right"></i>
              </button>
            </div>
          </div>

          <!-- Natija -->
          <div v-else-if="isQuizFinished" class="card shadow-sm border-0 rounded-4 p-4 p-md-5 text-center">
            <div class="mb-4">
              <img src="https://cdn-icons-png.flaticon.com/512/3113/3113073.png" alt="Trophy" width="120" class="mb-3 drop-shadow">
              <h2 class="fw-bold">Tabriklaymiz!</h2>
              <p class="text-muted fs-5">Siz testni yakunladingiz.</p>
            </div>

            <div class="row g-3 justify-content-center mb-4">
              <div class="col-6 col-sm-4">
                <div class="bg-light rounded-4 p-3 border">
                  <div class="text-muted small fw-semibold mb-1">To'g'ri javoblar</div>
                  <h3 class="fw-bold text-success mb-0">{{ score }} / {{ questions.length }}</h3>
                </div>
              </div>
              <div class="col-6 col-sm-4">
                <div class="bg-primary bg-opacity-10 rounded-4 p-3 border border-primary border-opacity-25">
                  <div class="text-primary small fw-semibold mb-1">Olingan XP</div>
                  <h3 class="fw-bold text-primary mb-0">+{{ xpEarned }}</h3>
                </div>
              </div>
            </div>

            <button @click="resetQuiz" class="btn btn-outline-primary btn-lg rounded-pill px-5 fw-bold">
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
  background-color: #f8fafc;
}

.icon-circle {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.option-btn {
  background-color: #f1f5f9;
  border: 2px solid transparent;
  color: #334155;
  transition: all 0.2s ease;
}

.option-btn:hover:not(:disabled) {
  background-color: #e2e8f0;
  transform: translateY(-2px);
}

.option-letter {
  width: 32px;
  height: 32px;
  background-color: white;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.option-btn.selected:not(.correct):not(.wrong) {
  border-color: #3b82f6;
  background-color: #eff6ff;
}
.option-btn.selected:not(.correct):not(.wrong) .option-letter {
  background-color: #3b82f6;
  color: white;
}

.option-btn.correct {
  border-color: #10b981;
  background-color: #ecfdf5;
  color: #065f46;
}
.option-btn.correct .option-letter {
  background-color: #10b981;
  color: white;
}

.option-btn.wrong {
  border-color: #ef4444;
  background-color: #fef2f2;
  color: #991b1b;
}
.option-btn.wrong .option-letter {
  background-color: #ef4444;
  color: white;
}

.option-btn:disabled {
  opacity: 0.9;
  cursor: default;
}

.drop-shadow {
  filter: drop-shadow(0 10px 15px rgba(0,0,0,0.1));
}

.transition-all {
  transition: all 0.25s ease;
}
</style>
