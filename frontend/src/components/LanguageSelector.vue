<template>
  <div class="language-selector">
    <button 
      @click="switchLanguage('en')" 
      :class="{ active: currentLanguage === 'en' }"
      class="lang-btn"
    >
      🇬🇧 EN
    </button>
    <button 
      @click="switchLanguage('lv')" 
      :class="{ active: currentLanguage === 'lv' }"
      class="lang-btn"
    >
      🇱🇻 LV
    </button>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import axios from 'axios';

const { locale } = useI18n();
const currentLanguage = ref(locale.value);

const switchLanguage = async (lang) => {
  currentLanguage.value = lang;
  locale.value = lang;
  localStorage.setItem('language', lang);
  
  try {
    await axios.post('/api/set-language/', { language: lang });
  } catch (error) {
    console.error('Language switch error:', error);
  }
};

onMounted(() => {
  const savedLang = localStorage.getItem('language');
  if (savedLang && (savedLang === 'en' || savedLang === 'lv')) {
    locale.value = savedLang;
    currentLanguage.value = savedLang;
  }
});
</script>

<style scoped>
.language-selector {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
  margin-bottom: 1rem;
}

.lang-btn {
  background: none;
  border: 1px solid #ddd;
  padding: 0.4rem 1rem;
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.2s;
}

.lang-btn:hover {
  background: #f0f0f0;
  transform: translateY(-1px);
}

.lang-btn.active {
  background: #4caf50;
  border-color: #4caf50;
  color: white;
}
</style>