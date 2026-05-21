<template>
  <div class="documents-page">
    <h1 class="title">📁 Hujjatlarim</h1>

    <!-- UPLOAD CARD -->
    <div class="upload-card">
      <select v-model="docType">
        <option value="transcript">📄 Transcript</option>
        <option value="article">📝 Maqola</option>
        <option value="thesis">📚 Tezis</option>
        <option value="language_cert">🌍 Til sertifikati</option>
        <option value="recommendation">📨 Tavsiyanoma</option>
      </select>

      <input type="file" @change="(e) => (selectedFile = e.target.files[0])" />

      <button @click="upload">Upload</button>
    </div>

    <!-- DOCUMENT LIST -->
    <div class="doc-list">
      <div v-for="doc in documents" :key="doc.id" class="doc-card">
        <div class="doc-info">
          <div class="doc-type">{{ doc.doc_type }}</div>
          <div v-if="doc.file_url">
            <a :href="doc.file_url" target="_blank">Ko‘rish</a>
          </div>
        </div>

        <button class="delete-btn" @click="removeDoc(doc.id)">❌</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import useApi from "@/composables/useApi";

const api = useApi();
const documents = ref([]);
const selectedFile = ref(null);
const docType = ref("transcript");

// 📥 Fetch docs
const fetchDocuments = async () => {
  try {
    const res = await api.get("/documents/");
    documents.value = res.data;
  } catch (err) {
    console.error("fetchDocuments error", err);
  }
};

// 📤 Upload
const upload = async () => {
  if (!selectedFile.value) return;

  const formData = new FormData();
  formData.append("file", selectedFile.value);
  formData.append("doc_type", docType.value);

  try {
    await api.post("/documents/upload/", formData);
    selectedFile.value = null;
    fetchDocuments();
  } catch (err) {
    console.error("upload error", err);
  }
};

// ❌ Delete
const removeDoc = async (id) => {
  try {
    await api.delete(`/documents/${id}/delete/`);
    fetchDocuments();
  } catch (err) {
    console.error("removeDoc error", err);
  }
};

onMounted(fetchDocuments);
</script>


