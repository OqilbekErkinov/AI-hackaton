<template>
  <div class="scholarship-page p-3">
    <!-- HEADER -->
    <div
      class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-3"
    >
      <h1 class="page-title">🎓 Stipendiyalar</h1>
<!-- 
      <NuxtLink to="/profiles/documents" class="btn btn-primary read-btn">
        <span class="contact-btn-content">Reyting</span>
      </NuxtLink> -->

      <!-- SEARCH -->
      <input
        v-model="search"
        type="text"
        class="form-control search-input"
        placeholder="Stipendiya qidirish..."
      />
    </div>

    <!-- FILTER -->
    <div class="filter-bar mb-4">
      <button
        v-for="cat in categories"
        :key="cat.value"
        class="filter-btn"
        :class="{ active: activeCategory === cat.value }"
        @click="activeCategory = cat.value"
      >
        {{ cat.label }}
      </button>
    </div>

    <!-- CARDS -->
    <div class="row g-4">
      <div
        v-for="item in filteredScholarships"
        :key="item.id"
        class="col-lg-4 col-md-6"
      >
        <div class="sch-card">
          <!-- DEADLINE -->
          <div class="deadline">
            ⏰ {{ new Date(item.deadline).toLocaleDateString() }}
          </div>

          <h3 class="sch-title">
            {{ item.title }}
          </h3>

          <p class="sch-desc">
            {{ item.short_description }}
          </p>

          <div class="sch-amount">💰 {{ item.amount }}</div>

          <button
            class="btn btn-primary read-btn"
            @click="openScholarship(item.id)"
          >
            Batafsil
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import useApi from "@/composables/useApi";

const router = useRouter();
const api = useApi();

const search = ref("");
const activeCategory = ref("All");
const scholarships = ref([]);

const categories = [
  { label: "All", value: "All" },
  { label: "Davlat", value: "state" },
  { label: "Xususiy", value: "private" },
  { label: "Xalqaro", value: "international" },
];

const fetchScholarships = async () => {
  try {
    const res = await api.get("/scholarships/");
    scholarships.value = res.data;
  } catch (err) {
    console.error("fetchScholarships error", err);
  }
};

onMounted(fetchScholarships);

const filteredScholarships = computed(() => {
  return scholarships.value.filter((s) => {
    const matchSearch =
      s.title.toLowerCase().includes(search.value.toLowerCase()) ||
      s.short_description.toLowerCase().includes(search.value.toLowerCase());

    const matchCategory =
      activeCategory.value === "All" || s.category === activeCategory.value;

    return matchSearch && matchCategory;
  });
});

const openScholarship = (id) => {
  router.push(`/scholarship/${id}`);
};
</script>


