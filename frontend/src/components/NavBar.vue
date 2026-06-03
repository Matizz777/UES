<template>
  <nav class="navbar">
    <div class="logo">
      <span class="logo-icon">☁️</span> UES
    </div>
    
    <div class="nav-controls">
      <div class="language-switcher">
        <button 
          @click="switchLanguage('en')" 
          :class="{ active: currentLanguage === 'en' }"
          class="lang-btn"
        >
          EN
        </button>
        <button 
          @click="switchLanguage('lv')" 
          :class="{ active: currentLanguage === 'lv' }"
          class="lang-btn"
        >
          LV
        </button>
      </div>

      <div class="auth-buttons">
        <template v-if="user">
          <div class="user-menu">
            <NotificationBell v-if="user.roles === 2 || user.roles === 3" />

            <button class="profile-btn" @click="$emit('show-profile')" :title="$t('profile')">
              👤
            </button>
            <button v-if="user && user.roles === 1" class="admin-btn" @click="$emit('show-admin')">
              👑 {{ $t('admin') }}
            </button>

            <div class="user-info">
              <div class="avatar">{{ user.username[0].toUpperCase() }}</div>
              <div class="user-details">
                <span class="welcome-msg">{{ user.username }}</span>
                <span class="user-role">
                  {{ user.roles === 2 ? $t('provider') : $t('client') }}
                </span>
              </div>
            </div>
            <button class="btn-logout" @click="$emit('logout')" :title="$t('logout')">
              <span class="logout-icon">→</span>
            </button>
          </div>
        </template>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import axios from 'axios';
import NotificationBell from './NotificationBell.vue';

const { locale } = useI18n();
defineProps({ user: Object });
defineEmits(['logout', 'show-profile', 'show-admin']);

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
  const match = document.cookie.match(/django_language=([^;]+)/);
  if (match) {
    currentLanguage.value = match[1];
    locale.value = match[1];
  }
});
</script>

<style scoped>
.profile-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0.3rem;
  border-radius: 50%;
  transition: background 0.2s;
  width: 35px;
  height: 35px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.profile-btn:hover {
  background: #e8f5e9;
}

.nav-controls {
  display: flex;
  align-items: center;
  gap: 2rem;
}

.language-switcher {
  display: flex;
  gap: 0.5rem;
  margin-right: 1rem;
}

.lang-btn {
  background: none;
  border: 1px solid #ddd;
  padding: 0.4rem 0.8rem;
  border-radius: 6px;
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

.user-menu {
  display: flex;
  align-items: center;
  gap: 0.8rem;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.avatar {
  width: 35px;
  height: 35px;
  background: #4caf50;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
}

.user-details {
  display: flex;
  flex-direction: column;
}

.welcome-msg {
  font-size: 0.85rem;
  font-weight: 600;
}

.user-role {
  font-size: 0.7rem;
  color: #888;
}

.btn-logout {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0.3rem;
}
</style>