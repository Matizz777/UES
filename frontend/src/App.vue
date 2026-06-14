<template>
  <div class="app">
    <NavBar 
      v-if="user" 
      :user="user" 
      @logout="handleLogout"
      @show-profile="showProfileModal = true"
    />

    <ResetPassword
      v-if="!user && resetToken"
      :token="resetToken"
      @go-login="clearResetToken"
    />

    <div class="apraksts" v-if="!user && !isResetRoute && authView === 'none'">
      <main class="hero">
        <h1>{{ $t('app_title') }}</h1>
        <p>{{ $t('app_subtitle') }}</p>
      </main>
      
      <div class="language-wrapper">
        <LanguageSelector />
      </div>
      
      <div class="auth-cta">
        <button class="btn-login"    @click="authView = 'login'">{{ $t('login') }}</button>
        <button class="btn-register" @click="authView = 'register'">{{ $t('register') }}</button>
      </div>
    </div>

    <LoginForm
      v-else-if="!user && !isResetRoute && authView === 'login'"
      @login-success="onAuthSuccess"
      @go-register="authView = 'register'"
      @go-forgot="authView = 'forgot'"
      @back="authView = 'none'"
    />

    <RegisterForm
      v-else-if="!user && !isResetRoute && authView === 'register'"
      @register-success="onAuthSuccess"
      @go-login="authView = 'login'"
      @back="authView = 'none'"
    />

    <ForgotPassword
      v-else-if="!user && !isResetRoute && authView === 'forgot'"
      @back="authView = 'login'"
    />

    <ResetPassword
      v-if="!user && isResetRoute"
      :token="resetToken"
      @go-login="handleResetComplete"
    />

    <ProfileModal 
      v-if="showProfileModal"
      :user="user"
      @close="showProfileModal = false"
    />

    <Dashboard v-else-if="user" :user="user" />

    <div class="clouds-container">
      <div class="cloud cloud-solid"></div>
      <div class="cloud cloud-transparent"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useI18n } from 'vue-i18n';
import axios from 'axios';

import NavBar        from './components/NavBar.vue';
import LoginForm     from './components/LoginForm.vue';
import RegisterForm  from './components/RegisterForm.vue';
import ForgotPassword from './components/ForgotPassword.vue';
import ResetPassword from './components/ResetPassword.vue';
import Dashboard     from './components/Dashboard.vue';
import ProfileModal  from './components/ProfileModal.vue';
import LanguageSelector from './components/LanguageSelector.vue';

import './assets/style.css';

const { locale } = useI18n();
const user        = ref(null);
const authView    = ref('none');
const showProfileModal = ref(false);
const resetToken  = ref('');

const isResetRoute = computed(() => {
  return window.location.pathname.includes('/reset-password/');
});

const handleResetComplete = () => {
  resetToken.value = null;
  authView.value = 'login';
  // Notīrīt URL
  window.history.pushState({}, '', '/');
};

  const path = window.location.pathname;
  if (path.startsWith('/reset-password/')) {
    const token = path.split('/reset-password/')[1];
    if (token && token.length > 0) {
      resetToken.value = token;
      console.log('Reset token loaded:', token);
    }
  }

onMounted(() => {
  const savedLang = localStorage.getItem('language');
  if (savedLang && (savedLang === 'en' || savedLang === 'lv')) {
    locale.value = savedLang;
  }
  
  // Pārbaudīt reset token no URL path
  const path = window.location.pathname;
  if (path.startsWith('/reset-password/')) {
    const token = path.split('/reset-password/')[1];
    if (token && token.length > 0) {
      resetToken.value = token;
      console.log('Reset token found:', token);
    }
  }
  
  const saved = localStorage.getItem('user_auth');
  if (saved) {
    const parsed = JSON.parse(saved);
    user.value = parsed;
    axios.defaults.headers.common['Authorization'] = `Bearer ${parsed.token}`;
  }
});

const onAuthSuccess = (authData) => {
  authData.roles = parseInt(authData.roles);
  user.value = authData;
  localStorage.setItem('user_auth', JSON.stringify(authData));
  axios.defaults.headers.common['Authorization'] = `Bearer ${authData.token}`;
  authView.value = 'none';
};

const handleLogout = () => {
  user.value = null;
  localStorage.removeItem('user_auth');
  delete axios.defaults.headers.common['Authorization'];
  authView.value = 'none';
};
</script>