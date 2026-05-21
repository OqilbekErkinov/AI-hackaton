<template>
  <section class="hero-wrapper">
    <div class="header">
      <div class="mid-spot" @click="toggleGold"></div>
      <div class="spotlight">
        <div></div>
        <div></div>
        <div></div>
      </div>
    </div>

    <canvas ref="canvasRef" id="particleCanvas"></canvas>

    <div class="accent-lines">
      <div>
        <div></div>
        <div></div>
        <div></div>
        <div></div>
        <div></div>
      </div>
      <div>
        <div></div>
        <div></div>
        <div></div>
        <div></div>
      </div>
    </div>

    <div class="heroSubP">
      <p>O‘zbekiston milliy reyting platformasi</p>
    </div>

    <div class="hero">
      <div class="heroT">
        <h2>RankEdu</h2>
        <h2>RankEdu</h2>
      </div>
    </div>

    <p class="heroP">
      Grant taqsimoti, talabalar faolligi va ochiq reyting
      <br />
      yagona raqamli tizimda.
    </p>

    <NuxtLink to="/profile" class="contact-btn2">
      <span class="contact-btn-content">Boshlash</span>
    </NuxtLink>

    <div class="mountains">
      <div></div>
      <div></div>
      <div></div>
    </div>

    <NuxtLink to="/reyting" class="contact-btn">
      <span class="contact-btn-content">Reyting</span>
    </NuxtLink>
  </section>
</template>

<script setup>
import { onMounted, ref } from "vue";

const canvasRef = ref(null);

function toggleGold() {
  document.body.classList.toggle("gold");
}

onMounted(() => {
  const canvas = canvasRef.value;
  const ctx = canvas.getContext("2d");

  const updateSize = () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  };
  updateSize();

  let particles = [];
  let particleCount = calculateParticleCount();

  class Particle {
    constructor() {
      this.reset();
      this.y = Math.random() * canvas.height;
    }
    reset() {
      this.x = Math.random() * canvas.width;
      this.y = Math.random() * canvas.height;
      this.speed = Math.random() / 5 + 0.1;
      this.opacity = 1;
      this.fadeDelay = Math.random() * 600 + 100;
      this.fadeStart = Date.now() + this.fadeDelay;
      this.fadingOut = false;
    }
    update() {
      this.y -= this.speed;
      if (this.y < 0) this.reset();
      if (!this.fadingOut && Date.now() > this.fadeStart) this.fadingOut = true;
      if (this.fadingOut) {
        this.opacity -= 0.008;
        if (this.opacity <= 0) this.reset();
      }
    }
    draw() {
      const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
      const color = isDark ? `rgba(255, 255, 255, ${this.opacity * 0.3})` : `rgba(17, 45, 78, ${this.opacity * 0.4})`;
      ctx.fillStyle = color;
      ctx.fillRect(this.x, this.y, 0.4, Math.random() * 2 + 1);
    }
  }

  function initParticles() {
    particles = [];
    for (let i = 0; i < particleCount; i++) {
        particles.push(new Particle());
    }
  }

  function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    particles.forEach(p => { p.update(); p.draw(); });
    requestAnimationFrame(animate);
  }

  function calculateParticleCount() {
    return Math.floor((canvas.width * canvas.height) / 6000);
  }

  window.addEventListener("resize", () => {
    updateSize();
    particleCount = calculateParticleCount();
    initParticles();
  });

  initParticles();
  animate();
});
</script>

<style scoped>
@import url('https://fonts.cdnfonts.com/css/hubot-sans');

.hero-wrapper {
  position: relative;
  margin: 0;
  font-family: 'Hubot-Sans', sans-serif;
  background: var(--bg-app);
  color: var(--text-main);
  font-size: max(calc(var(--_size) * 0.03), 10px);
  --_factor: min(600px, 80vh);
  --_size: min(var(--_factor), 80vw);
  min-height: 400px;
  max-height: 900px;
  overflow: hidden;
  margin-top: -5rem;
  width: 100%;
}

h2, p { margin: 0; padding: 0; }

.header {
  display: flex; width: 100%; justify-content: center;
  padding-top: 6rem; position: absolute; top: 0; left: 0; right: 0;
  margin-top: -3rem; opacity: 0; translate: 0 -1em;
  animation: load 2s ease-in 2s forwards, up 1.4s ease-out 2s forwards;
}

.mid-spot {
  width: 1.8em; height: 1.8em; border-radius: 50%;
  background: var(--primary);
  box-shadow: 0 0 1em 0 rgba(var(--primary-rgb), 0.4);
  cursor: pointer;
}

/* ================= BUTTONS ================= */
.contact-btn, .contact-btn2 {
  position: absolute; bottom: 0; width: 9.5em; height: 3.2em;
  cursor: pointer; border-radius: 20em; border: 1px solid var(--divider-color);
  background: var(--primary); color: #fff;
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 20rem; text-decoration: none; transition: 0.3s;
  font-weight: 700; font-size: 13px;
  z-index: 1000;
}
.contact-btn { right: min(28em, 40vw); }
.contact-btn2 { left: min(35em, 28.5vw); }

.contact-btn:hover, .contact-btn2:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 25px rgba(var(--primary-rgb), 0.3);
  background-color: var(--primary-light);
}

/* ================= SPOTLIGHT ================= */
.header .spotlight {
  pointer-events: none; position: absolute; left: 0; right: 0; top: 0;
  margin: 0 auto; transition: filter 1s ease-in-out;
  height: 42em; width: 100%; overflow: hidden;
}
.header .spotlight>div {
  border-radius: 0 0 50% 50%; position: absolute; left: 0; right: 0; margin: 0 auto;
  top: 3em; width: 30em; height: max(42em, 86vh);
  background-image: conic-gradient(from 0deg at 50% -5%,
      transparent 45%,
      rgba(var(--primary-rgb), .2) 49%,
      rgba(var(--primary-rgb), .35) 50%,
      rgba(var(--primary-rgb), .2) 51%,
      transparent 55%);
  transform-origin: 50% 0;
  filter: blur(15px) opacity(0.4);
  z-index: -1;
  animation: load 2s ease-in-out forwards, loadrot 2s ease-in-out forwards, spotlight 21s ease-in-out infinite reverse;
}
.header .spotlight>div:nth-child(1) { rotate: 20deg; animation: load 2.5s ease-in-out forwards, loadrot 2s ease-in-out forwards, spotlight 17s ease-in-out infinite; }
.header .spotlight>div:nth-child(2) { rotate: -20deg; animation: load 2.5s ease-in-out forwards, loadrot 2s ease-in-out forwards, spotlight 14s ease-in-out infinite; }

@keyframes loadrot { 0% { rotate: 0deg; scale: 0; } 100% { scale: 1; } }
@keyframes spotlight {
  0%, 100% { transform: rotateZ(0deg) scale(1); filter: blur(15px) opacity(0.4); }
  50% { transform: rotateZ(2deg) scale(1.3); filter: blur(14px) opacity(0.3); }
}

/* ================= HERO TEXT ================= */
.heroT {
  position: absolute; top: 23%; left: 0; right: 0; margin: auto;
  height: 30em; translate: 0 -1.6em; opacity: 0;
  animation: load 2s ease-in-out 0.6s forwards;
  z-index: 10;
}

.heroT>h2 {
  position: absolute; left: 0; right: 0; margin: auto; width: fit-content;
  font-size: 7.5em; font-weight: 700; color: var(--text-main);
  background: radial-gradient(2em 2em at 50% 50%,
      transparent calc(var(--p) - 2em),
      var(--primary) calc(var(--p) - 1em),
      var(--primary) calc(var(--p) - 0.4em),
      transparent var(--p)),
    linear-gradient(0deg, var(--text-main) 30%, var(--text-main) 100%);
  background-clip: text; -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  text-shadow: 0 4px 20px rgba(var(--primary-rgb), .1);
  --p: 0%; transition: --p 3s linear; animation: pulse 10s linear 1.2s infinite;
}
.heroT h2:nth-child(2) { filter: blur(20px) opacity(0.25); }

@keyframes pulse { 0% { --p: 0%; } 50%, 100% { --p: 300%; } }

/* ================= HERO SUBTEXT ================= */
.heroSubP {
  position: absolute; left: 0; right: 0; top: 16em; margin: auto;
  opacity: 0; translate: 0 -1em;
  animation: load3 2s ease-in 0s forwards, up 1.4s ease-out 0s forwards;
  z-index: 11;
}
@keyframes load3 { 0% { opacity: 0; } 100% { opacity: 0.8; } }

.heroSubP p {
  font-size: 1.1em; position: relative; width: fit-content; margin: -6rem auto 0;
  color: var(--text-main); font-weight: 500; letter-spacing: 0.05em;
}
.heroSubP p::before, .heroSubP p::after {
  position: absolute; top: 60%; display: block; content: '';
  width: 6em; height: 1px; opacity: 0;
  animation: load2 1.4s ease-in-out 0s forwards, up 1.4s ease-out 0s forwards;
}
@keyframes load2 { 0% { opacity: 0; } 100% { opacity: 0.4; } }
.heroSubP p::before { background: linear-gradient(-90deg, var(--primary) 0%, transparent 100%); right: 120%; translate: -5em 0; }
.heroSubP p::after { background: linear-gradient(90deg, var(--primary) 0%, transparent 100%); left: 120%; translate: 5em 0; }

.heroP {
  font-size: 1.3em; position: absolute; left: 0; right: 0; top: 22em;
  margin: -7rem auto 0; text-align: center; opacity: 0; translate: 0 1em;
  animation: load 1.2s ease-out 1.2s forwards, up 1.2s ease-out 1.2s forwards;
  color: var(--text-secondary); line-height: 1.4; font-weight: 500;
  z-index: 11;
}
@keyframes up { 100% { translate: 0; } }

/* ================= ACCENT LINES ================= */
.accent-lines {
  pointer-events: none; position: absolute; top: 0; left: 0; right: 0;
  width: 100%; height: 48em; z-index: -2;
}
.accent-lines>div:nth-child(1)>div {
  position: absolute; width: 100%; height: 1px;
  background: linear-gradient(90deg, transparent, var(--divider-color), transparent);
  animation: accentload 2s ease-out 2.4s forwards; opacity: 0; scale: 0;
}
.accent-lines>div:nth-child(1)>div:nth-child(1) { top: 6em; }
.accent-lines>div:nth-child(1)>div:nth-child(2) { top: 11em; }
.accent-lines>div:nth-child(1)>div:nth-child(3) { top: 16em; }
.accent-lines>div:nth-child(1)>div:nth-child(4) { top: 24em; }
.accent-lines>div:nth-child(1)>div:nth-child(5) { top: 29em; }

@keyframes accentload { 0% { opacity: 0; scale: 0; } 100% { opacity: 1; scale: 1; } }

.accent-lines>div:nth-child(2)>div {
  position: absolute; top: 0; width: 1px; height: 100%;
  background: var(--divider-color); opacity: 0; scale: 0;
  animation: accentload 2s ease-out 2s forwards;
}
.accent-lines>div:nth-child(2)>div:nth-child(1) { left: 24em; }
.accent-lines>div:nth-child(2)>div:nth-child(2) { left: 34em; }
.accent-lines>div:nth-child(2)>div:nth-child(3) { right: 24em; }
.accent-lines>div:nth-child(2)>div:nth-child(4) { right: 34em; }

/* ================= MOUNTAINS ================= */
.mountains {
  position: relative; left: 0; right: 0; top: -12em; margin: auto;
  width: 100%; height: 10em; pointer-events: none; z-index: 1;
}
.mountains::before {
  content: ''; display: block; width: 100%; height: 500%;
  position: absolute; top: 0%;
  background: linear-gradient(0deg, var(--bg-app) 80%, transparent 95%);
  z-index: 200;
}
.mountains>div {
  box-shadow: -1em -0.2em 0.4em -1.1em rgba(var(--primary-rgb), .25),
    inset 0em 0em 0em 2px var(--divider-color),
    inset 0.2em 0.3em 0.2em -0.2em rgba(var(--primary-rgb), .2);
  background: var(--bg-app); z-index: 100; filter: brightness(0.98);
  position: absolute; left: 0; right: 0; margin: auto; width: 22em; height: 22em; rotate: 45deg;
}
.mountains>div:nth-child(1) { bottom: -240%; translate: -7em 2em; animation: mountainload1 2s ease-out 2.4s forwards; }
.mountains>div:nth-child(2) { bottom: -240%; translate: -2em 0em; width: 16em; height: 20em; animation: mountainload2 2s ease-out 2.2s forwards; }
.mountains>div:nth-child(3) { bottom: -240%; translate: 7em 3em; animation: mountainload1 2s ease-out 2s forwards; }

@keyframes mountainload1 { 100% { bottom: -140%; } }
@keyframes mountainload2 { 100% { bottom: -108%; } }

@keyframes load { 0% { opacity: 0; } 100% { opacity: 1; } }
@keyframes up { 100% { translate: 0; } }

.mountains>div::before {
  content: ''; display: block;
  background: repeating-radial-gradient(at 100% 100%, transparent 0%, var(--divider-color) 2px, transparent 4px);
  width: 12em; height: 12em; position: absolute; left: 0; top: 0; border-bottom-right-radius: 100%;
}
</style>