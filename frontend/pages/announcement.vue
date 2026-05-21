<template>
  <div class="carousel">

    <!-- SLIDER -->
    <div class="list">
      <div class="item" v-for="(item, index) in topAnnouncements" :key="index">
        <div class="content">
          <div class="author">Nexora</div>
          <div class="title">{{ item.title }}</div>
          <!-- <div class="scroll-down" @click="scrollToFeed">
            <div class="circle">
              <span>PASTGA</span>
              ↓
            </div>
          </div> -->
          <div class="topic">{{ item.topic }}</div>
          <div class="des">
            {{ item.short }}
          </div>
          <!-- <div class="views">
            👁 {{ item.views }} ta ko‘rildi
          </div> -->

          <div v-if="item.deadline" class="mt-2 deadline" style="top: 28.5rem; height: 5%; left: 2%; width: 14%;">
            ⏳ {{ getRemainingDays(item.deadline) }} kun qoldi
          </div>

          <div class="buttons">
            <button @click="openModal(item)">BATAFSIL</button>
          </div>
        </div>
      </div>
    </div>

    <!-- THUMBNAIL -->
    <div class="thumbnail">
      <div class="item" v-for="(item, index) in topAnnouncements" :key="index">
        <div class="thumb-card">{{ item.topic }}</div>
      </div>
    </div>

    <!-- ARROWS -->
    <div class="arrows">
      <button id="prev">
        < </button>
          <button id="next">></button>
    </div>

    <div class="time"></div>


    <!-- 🔥 MODAL -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-box theme-card">

        <!-- BADGES -->
        <div class="badges">
          <span class="badge type">{{ selected.type }}</span>
        </div>
        <img v-if="selected.image" :src="selected.image" class="modal-image" />

        <!-- TITLE -->
        <h2 class="modal-title text-main">{{ selected.title }}</h2>
        <h4 class="modal-topic">{{ selected.topic }}</h4>

        <!-- DESCRIPTION -->
        <p class="modal-desc text-secondary">
          {{ selected.description }}
        </p>

        <!-- LOCATIONS -->
        <div v-if="selected.locations?.length" class="modal-section">
          <h3 class="text-main">📍 Joylar</h3>
          <ul class="text-secondary">
            <li v-for="(loc, i) in selected.locations" :key="i">
              {{ loc }}
            </li>
          </ul>
        </div>

        <!-- REQUIREMENTS -->
        <div v-if="selected.requirements?.length" class="modal-section">
          <h3 class="text-main">📌 Talablar</h3>
          <ul class="text-secondary">
            <li v-for="(req, i) in selected.requirements" :key="i">
              {{ req }}
            </li>
          </ul>
        </div>

        <!-- BENEFITS -->
        <div v-if="selected.benefits?.length" class="modal-section">
          <h3 class="text-main">🎁 Imkoniyatlar</h3>
          <ul class="text-secondary">
            <li v-for="(b, i) in selected.benefits" :key="i">
              {{ b }}
            </li>
          </ul>
        </div>

        <!-- DEADLINE -->
        <div v-if="selected.deadline" class="modal-deadline">
          ⏳ Oxirgi sana: {{ formatDate(selected.deadline) }}
        </div>
        <div v-if="selected.deadline" class="text-secondary small">
          ⏳ {{ getRemainingDays(selected.deadline) }} kun qoldi
        </div>

        <!-- ACTIONS -->
        <div class="modal-actions">
          <a v-if="selected.link" :href="selected.link" target="_blank">
            <button class="apply-btn">Ariza topshirish</button>
          </a>

          <button class="close-btn" @click="closeModal">Yopish</button>
        </div>

      </div>
    </div>

  </div>
  <!-- 🔥 ANNOUNCEMENT FEED -->
  <div class="feed">
    <h2 class="feed-title">Barcha e’lonlar</h2>
    <div class="filters">
      <button :class="{ active: selectedFilter === 'new' }" @click="selectedFilter = 'new'">
        🆕 Yangi
      </button>

      <button :class="{ active: selectedFilter === 'popular' }" @click="selectedFilter = 'popular'">
        🔥 Mashhur
      </button>
    </div>

    <div class="feed-grid">
      <div class="feed-card theme-card" v-for="item in filteredAnnouncements" :key="item.id">
        <div class="feed-top">
          <span class="badge type">{{ item.type }}</span>
        </div>

        <h3 class="text-main">{{ item.title }}</h3>
        <p class="feed-topic">{{ item.topic }}</p>

        <p class="feed-short text-secondary">{{ item.short }}</p>

        <div class="feed-bottom">
          <span v-if="item.deadline" class="text-muted">
            📅 {{ formatDate(item.deadline) }}
          </span>
        </div>
        <div v-if="item.deadline" class="text-muted">
          ⏳ {{ getRemainingDays(item.deadline) }} kun qoldi
        </div>

        <div class="feed-actions mt-2">
          <button @click="openModal(item)" class="theme-btn-sm">BATAFSIL</button>
          <div class="views mb-2 mt-3 me-3 text-muted">
            👁 {{ item.views }}
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import useApi from "@/composables/useApi";

const api = useApi();
const config = useRuntimeConfig();

// Base URL for images (remove /api from the end of config.public.apiUrl)
const API_BASE_URL = (config.public.apiUrl || "http://127.0.0.1:9000/api").replace(/\/api$/, "");

// 🔥 DATA
const announcements = ref([]);

const scrollToFeed = () => {
  const el = document.querySelector(".feed");
  if (el) {
    el.scrollIntoView({ behavior: "smooth" });
  }
};

// 🔥 TOP 5 ENG KO‘RILGAN
const topAnnouncements = computed(() => {
  return [...announcements.value]
    .sort((a, b) => b.views - a.views)
    .slice(0, 5);
});

const getRemainingDays = (deadline) => {
  const now = new Date();
  const end = new Date(deadline);
  const diff = end - now;

  const days = Math.ceil(diff / (1000 * 60 * 60 * 24));
  return days > 0 ? days : 0;
};

const selectedFilter = ref("new"); // new | popular
const filteredAnnouncements = computed(() => {
  let data = [...announcements.value]; // clone

  if (selectedFilter.value === "new") {
    return [...data].sort(
      (a, b) => new Date(b.created_at) - new Date(a.created_at)
    );
  }

  if (selectedFilter.value === "popular") {
    return [...data].sort((a, b) => b.views - a.views);
  }

  return data;
});

const formatDate = (date) => {
  const d = new Date(date);

  const day = String(d.getDate()).padStart(2, "0");
  const month = String(d.getMonth() + 1).padStart(2, "0");
  const year = d.getFullYear();

  return `${day}.${month}.${year}`;
};

const saved = ref([]);

onMounted(() => {
  const data = localStorage.getItem("savedAnnouncements");
  if (data) saved.value = JSON.parse(data);
});

const toggleSave = (item) => {
  const exists = saved.value.find(i => i.id === item.id);

  if (exists) {
    saved.value = saved.value.filter(i => i.id !== item.id);
  } else {
    saved.value.push(item);
  }

  localStorage.setItem("savedAnnouncements", JSON.stringify(saved.value));
};

// 🔥 MODAL
const showModal = ref(false);
const selected = ref({});

const openModal = async (item) => {
  selected.value = item;
  showModal.value = true;

  try {
    await api.post(`/announcements/${item.id}/view/`);
    item.views++;
  } catch (e) {
    console.log(e);
  }
};

const closeModal = () => {
  showModal.value = false;
};

const fetchAnnouncements = async () => {
  try {
    const res = await api.get("/announcements/");
    announcements.value = res.data.map(item => ({
      ...item,
      image: item.image
        ? API_BASE_URL + item.image
        : null
    }));
  } catch (err) {
    console.log(err);
  }
};

onMounted(() => {
  fetchAnnouncements();
  const carouselDom = document.querySelector(".carousel");
  if (!carouselDom) return;

  const nextDom = document.getElementById("next");
  const prevDom = document.getElementById("prev");

  const sliderDom = carouselDom.querySelector(".list");
  const thumbnailBorderDom = carouselDom.querySelector(".thumbnail");

  let timeRunning = 3000;
  let timeAutoNext = 7000;
  let runTimeOut;
  let runNextAuto;

  let thumbnailItemsDom = thumbnailBorderDom.querySelectorAll(".item");

  if (thumbnailItemsDom.length > 0) {
    thumbnailBorderDom.appendChild(thumbnailItemsDom[0]);
  }

  nextDom.onclick = () => showSlider("next");
  prevDom.onclick = () => showSlider("prev");

  runNextAuto = setTimeout(() => nextDom.click(), timeAutoNext);

  function showSlider(type) {
    const sliderItemsDom = sliderDom.querySelectorAll(".item");
    const thumbnailItemsDom = thumbnailBorderDom.querySelectorAll(".item");

    if (type === "next") {
      sliderDom.appendChild(sliderItemsDom[0]);
      thumbnailBorderDom.appendChild(thumbnailItemsDom[0]);
      carouselDom.classList.add("next");
    } else {
      sliderDom.prepend(sliderItemsDom[sliderItemsDom.length - 1]);
      thumbnailBorderDom.prepend(
        thumbnailItemsDom[thumbnailItemsDom.length - 1]
      );
      carouselDom.classList.add("prev");
    }

    clearTimeout(runTimeOut);
    runTimeOut = setTimeout(() => {
      carouselDom.classList.remove("next");
      carouselDom.classList.remove("prev");
    }, timeRunning);

    clearTimeout(runNextAuto);
    runNextAuto = setTimeout(() => nextDom.click(), timeAutoNext);
  }
});
</script>


<style scoped>
@import url("https://fonts.googleapis.com/css2?family=Poppins:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&display=swap");

body {
  margin: 0;
  background-color: #000;
  color: #eee;
  font-family: Poppins;
  font-size: 12px;
}

a {
  text-decoration: none;
}

.carousel {
  height: 90vh;
  /* margin-top: -50px; */
  overflow: hidden;
  position: relative;
}

.carousel .list .item {
  width: 100%;
  height: 100%;
  position: absolute;
  inset: 0 0 0 0;
}

.carousel .list .item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.carousel .list .item .content {
  position: absolute;
  top: 0%;
  width: 1140px;
  max-width: 80%;
  left: 40%;
  transform: translateX(-50%);
  padding-right: 30%;
  box-sizing: border-box;
  color: #112d4e;
  text-shadow: 0 5px 10px #0004;
}

.carousel .list .item .author {
  font-weight: bold;
  letter-spacing: 10px;
}

.carousel .list .item .title,
.carousel .list .item .topic {
  font-size: 5em;
  font-weight: bold;
  line-height: 1.3em;
}

.carousel .list .item .topic {
  color: #f1683a;
}

.carousel .list .item .buttons {
  display: grid;
  grid-template-columns: repeat(2, 130px);
  grid-template-rows: 40px;
  gap: 5px;
  margin-top: 20px;
}

.carousel .list .item .buttons button {
  border: 1px solid #112d4e;
  border-radius: 7px;
  background-color: #112d4e;
  color: #ffff;
  letter-spacing: 3px;
  font-family: Poppins;
  font-weight: 500;
  transition: 0.3s ease;
}

.carousel .list .item .buttons button:nth-child(2) {
  background-color: transparent;
  border: 1px solid #112d4e;
  color: #112d4e;
  transition: 0.3s ease;
}

.carousel .list .item .buttons button:hover {
  border: 1px solid #112d4e;
  border-radius: 7px;
  background-color: #fff;
  color: #112d4e;
  letter-spacing: 3px;
  font-family: Poppins;
  font-weight: 500;
}

.carousel .list .item .buttons button:nth-child(2):hover {
  background-color: #112d4e;
  border: 1px solid #fff;
  color: #fff;
}

/* thumbail */
.thumbnail {
  position: absolute;
  bottom: 40px;
  left: 50%;
  width: max-content;
  z-index: 100;
  display: flex;
  gap: 20px;
}

.thumbnail .item {
  width: 150px;
  height: 240px;
  flex-shrink: 0;
  position: relative;
}

.thumbnail .item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 20px;
}

.thumbnail .item .content {
  color: #fff;
  position: absolute;
  bottom: 10px;
  left: 10px;
  right: 10px;
}

.thumbnail .item .content .title {
  font-weight: 500;
}

.thumbnail .item .content .description {
  font-weight: 300;
}

.thumb-card {
  font-size: 1.2rem;
}

/* arrows */
.arrows {
  position: absolute;
  top: 87%;
  right: 52%;
  z-index: 100;
  width: 300px;
  max-width: 30%;
  display: flex;
  gap: 10px;
  align-items: center;
}

.arrows button {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #eee4;
  border: 1px solid #112d4e;
  color: #112d4e;
  font-family: monospace;
  font-weight: bold;
  transition: 0.5s;
}

.arrows button:hover {
  background-color: #fff;
  color: #000;
}

/* animation */
.carousel .list .item:nth-child(1) {
  z-index: 1;
}

/* animation text in first item */
.carousel .list .item:nth-child(1) .content .author {
  transform: translateY(100px);
}

.carousel .list .item:nth-child(1) .content .author,
.carousel .list .item:nth-child(1) .content .title,
.carousel .list .item:nth-child(1) .content .topic,
.carousel .list .item:nth-child(1) .content .des,
.carousel .list .item:nth-child(1) .content .deadline,
.carousel .list .item:nth-child(1) .content .views,
.carousel .list .item:nth-child(1) .content .buttons {
  transform: translateY(50px);
  filter: blur(20px);
  opacity: 0;
  animation: showContent 0.5s 1s linear 1 forwards;
}

@keyframes showContent {
  to {
    transform: translateY(0px);
    filter: blur(0px);
    opacity: 1;
  }
}

.carousel .list .item:nth-child(1) .content .title {
  animation-delay: 1.2s !important;
}

.carousel .list .item:nth-child(1) .content .topic {
  animation-delay: 1.4s !important;
}

.carousel .list .item:nth-child(1) .content .des {
  animation-delay: 1.6s !important;
}

.carousel .list .item:nth-child(1) .content .deadline {
  animation-delay: 1.6s !important;
}

.carousel .list .item:nth-child(1) .content .views {
  animation-delay: 1.6s !important;
}

.carousel .list .item:nth-child(1) .content .buttons {
  animation-delay: 1.8s !important;
}

/* create animation when next click */
.carousel.next .list .item:nth-child(1) img {
  width: 150px;
  height: 220px;
  position: absolute;
  bottom: 50px;
  left: 50%;
  border-radius: 30px;
  animation: showimagess 0.5s linear 1 forwards;
}

@keyframes showimagess {
  to {
    bottom: 0;
    left: 0;
    width: 100%;
    height: 100%;
    border-radius: 0;
  }
}

.carousel.next .thumbnail .item:nth-last-child(1) {
  overflow: hidden;
  animation: showThumbnail 0.5s linear 1 forwards;
}

.carousel.prev .list .item img {
  z-index: 100;
}

@keyframes showThumbnail {
  from {
    width: 0;
    opacity: 0;
  }
}

.carousel.next .thumbnail {
  animation: effectNext 0.5s linear 1 forwards;
}

@keyframes effectNext {
  from {
    transform: translateX(150px);
  }
}

/* running time */

.carousel .time {
  position: absolute;
  z-index: 1000;
  width: 0%;
  height: 3px;
  background-color: #f1683a;
  left: 0;
  top: 0;
}

.carousel.next .time,
.carousel.prev .time {
  animation: runningTime 3s linear 1 forwards;
}

@keyframes runningTime {
  from {
    width: 100%;
  }

  to {
    width: 0;
  }
}

/* prev click */

.carousel.prev .list .item:nth-child(2) {
  z-index: 2;
}

.carousel.prev .list .item:nth-child(2) img {
  animation: outFrame 0.5s linear 1 forwards;
  position: absolute;
  bottom: 0;
  left: 0;
}

@keyframes outFrame {
  to {
    width: 150px;
    height: 220px;
    bottom: 50px;
    left: 50%;
    border-radius: 20px;
  }
}

.carousel.prev .thumbnail .item:nth-child(1) {
  overflow: hidden;
  opacity: 0;
  animation: showThumbnail 0.5s linear 1 forwards;
}

.carousel.next .arrows button,
.carousel.prev .arrows button {
  pointer-events: none;
}

.carousel.prev .list .item:nth-child(2) .content .author,
.carousel.prev .list .item:nth-child(2) .content .title,
.carousel.prev .list .item:nth-child(2) .content .topic,
.carousel.prev .list .item:nth-child(2) .content .des,
.carousel.prev .list .item:nth-child(2) .content .buttons {
  animation: contentOut 1.5s linear 1 forwards !important;
}

@keyframes contentOut {
  to {
    transform: translateY(-150px);
    filter: blur(20px);
    opacity: 0;
  }
}

@media screen and (max-width: 678px) {
  .carousel .list .item .content {
    padding-right: 0;
  }

  .carousel .list .item .content .title {
    font-size: 30px;
  }
}

.thumb-card {
  margin-top: 13rem;
  color: #112d4e;
}


.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 999;
}

.modal-box {
  background: var(--bg-card);
  padding: 30px;
  border-radius: 15px;
  max-width: 500px;
  width: 90%;
  text-align: center;
}

.modal-box {
  background: var(--bg-card);
  padding: 30px;
  border-radius: 15px;
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  text-align: left;
  animation: scaleUp 0.3s ease;
}

.modal-title {
  margin-top: 10px;
}

.modal-image {
  width: 100%;
  height: 220px;
  object-fit: cover;
  border-radius: 10px;
  margin: 15px 0;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.modal-topic {
  color: #f1683a;
  margin-bottom: 15px;
}

.modal-desc {
  margin-bottom: 20px;
  color: var(--text-secondary);
}

.modal-section {
  margin-bottom: 20px;
}

.modal-section h3 {
  margin-bottom: 8px;
}

.modal-section ul {
  padding-left: 20px;
}

.modal-deadline {
  margin-top: 10px;
  font-weight: 600;
  color: #c0392b;
}

.modal-actions {
  margin-top: 20px;
  display: flex;
  gap: 10px;
}

.badge {
  padding: 5px 10px;
  border-radius: 8px;
  font-size: 12px;
  margin-right: 5px;
}

.important {
  background: red;
  color: #fff;
}

.type {
  background: var(--primary);
  color: #fff;
}

.deadline {
  margin-top: 10px;
  font-size: 14px;
  color: var(--text-main);
  font-weight: 600;
}

.apply-btn {
  background: #112d4e;
  color: #fff;
  padding: 10px 20px;
  border-radius: 8px;
  border: #112d4e 1px solid;
  transition: 0.3s ease;
}

.apply-btn:hover {
  background: #fff;
  color: #112d4e;
  border: #112d4e 1px solid;
}

.close-btn {
  padding: 10px 20px;
  border: none;
  background: #fff;
  color: #112d4e;
  border: #112d4e 1px solid;
  border-radius: 8px;
  transition: 0.3s ease;
}

.close-btn:hover {
  background: #112d4e;
  color: #fff;
  border: #fff 1px solid;
}

.modal-box {
  animation: scaleUp 0.3s ease;
}

@keyframes scaleUp {
  from {
    transform: scale(0.7);
    opacity: 0;
  }

  to {
    transform: scale(1);
    opacity: 1;
  }
}



.feed {
  padding: 50px 20px;
  background: var(--bg-app);
}

.feed-title {
  text-align: center;
  /* margin-bottom: 30px; */
  font-size: 28px;
}

.feed-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.feed-card {
  background: var(--bg-card);
  padding: 20px;
  border-radius: 15px;
  margin-bottom: 20px;
  box-shadow: var(--shadow-sm);
  transition: 0.3s;
}

.feed-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.feed-card:hover {
  transform: translateY(-5px);
}

.feed-top {
  margin-bottom: 10px;
}

.feed-topic {
  color: #f1683a;
  font-weight: 600;
  margin: 0;
}

.feed-short {
  margin-top: 5px;
  color: var(--text-secondary);
}

.feed-bottom {
  font-size: 14px;
  margin-bottom: 10px;
}

.feed-actions {
  display: flex;
  justify-content: space-between;
}

.feed-actions button {
  padding: 8px 15px;
  border-radius: 8px;
  border: none;
  background: #112d4e;
  color: #fff;
  border: #112d4e 1px solid;
  transition: 0.3s ease;
}

.feed-actions button:hover {
  background: #fff;
  color: #112d4e;
  border: #112d4e 1px solid;
}

@media (max-width: 768px) {
  .feed-grid {
    grid-template-columns: 1fr;
  }
}

.filters {
  display: flex;
  justify-content: end;
  gap: 10px;
  margin-bottom: 20px;
}

.filters button {
  padding: 5px 10px;
  border-radius: 8px;
  border: none;
  background: #ddd;
  transition: 0.3s ease;

}

.filters button:hover {
  background: #112d4ed1;
  color: #ffff;
}

.filters button.active {
  background: #112d4e;
  color: #fff;
}

.views {
  font-size: 13px;
  color: var(--text-muted);
  margin-top: 5px;
}


.scroll-down {
  position: absolute;
  bottom: 80%;
  right: 0%;
  transform: translateX(-50%);
  z-index: 200;
  cursor: pointer;
}

.circle {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  border: 1px solid #112d4e;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: #112d4e;
  font-size: 14px;
  text-align: center;
  transition: 0.3s ease;
}

.circle:hover {
  background: #112d4e;
  color: #fff;
}

.circle span {
  font-size: 10px;
  margin-bottom: 5px;
}
</style>
