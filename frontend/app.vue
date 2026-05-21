<template>
  <div>
    <NuxtLayout>
      <svg
        xmlns="http://www.w3.org/2000/svg"
        class="goo"
        version="1.1"
        width="100%"
      >
        <defs>
          <filter id="goo">
            <feGaussianBlur
              in="SourceGraphic"
              stdDeviation="6"
              result="blur"
            ></feGaussianBlur>
            <feColorMatrix
              in="blur"
              mode="matrix"
              values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 35 -15"
              result="goo"
            ></feColorMatrix>
            <feComposite
              in="SourceGraphic"
              in2="goo"
              operator="atop"
            ></feComposite>
          </filter>
        </defs>
      </svg>
      <div id="cursor" ref="cursorRef"></div>
      <NuxtLoadingIndicator />
      <NuxtPage />
    </NuxtLayout>
  </div>
</template>
<script setup>
import { ref, onMounted, onBeforeUnmount } from "vue";
import useColorTheme from "@/composables/useColorTheme";

const cursorRef = ref(null);
const { mode } = useColorTheme();

const TAIL_LENGTH = 20;
let mouseX = 0;
let mouseY = 0;
let cursorCircles = [];
let cursorHistory = Array.from({ length: TAIL_LENGTH }, () => ({ x: 0, y: 0 }));
let rafId = null;

function onMouseMove(e) {
  mouseX = e.clientX;
  mouseY = e.clientY;
}

function initCursor() {
  if (!cursorRef.value) return;

  cursorRef.value.innerHTML = ""; // safety

  for (let i = 0; i < TAIL_LENGTH; i++) {
    const div = document.createElement("div");
    div.className = "cursor-circle";
    cursorRef.value.appendChild(div);
  }

  cursorCircles = Array.from(cursorRef.value.children);
}

function updateCursor() {
  cursorHistory.shift();
  cursorHistory.push({ x: mouseX, y: mouseY });

  cursorCircles.forEach((circle, i) => {
    const p = cursorHistory[i];
    const scale = i / TAIL_LENGTH;
    circle.style.transform = `translate(${p.x}px, ${p.y}px) scale(${scale})`;
  });

  rafId = requestAnimationFrame(updateCursor);
}

onMounted(() => {
  document.addEventListener("mousemove", onMouseMove);
  initCursor();
  updateCursor();
});

onBeforeUnmount(() => {
  document.removeEventListener("mousemove", onMouseMove);
  cancelAnimationFrame(rafId);
});
</script>


