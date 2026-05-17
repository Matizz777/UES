<template>
    <NavBar 
    v-if="user" 
    :user="user" 
    @logout="handleLogout"
    @show-profile="showProfileModal = true"
  />

  <!-- Landing / Auth -->
  <div class="apraksts" v-if="!user && authView === 'none'">
    <main class="hero">
      <h1>Universālā e-pierakstu sistēma</h1>
      <p>Pieraksts pāris klikšķu attālumā</p>
    </main>
    <div class="auth-cta">
      <button class="btn-login"    @click="authView = 'login'">Pieslēgties</button>
      <button class="btn-register" @click="authView = 'register'">Reģistrēties</button>
    </div>
  </div>

  <LoginForm
    v-else-if="!user && authView === 'login'"
    @login-success="onAuthSuccess"
    @go-register="authView = 'register'"
    @back="authView = 'none'"
  />

  <RegisterForm
    v-else-if="!user && authView === 'register'"
    @register-success="onAuthSuccess"
    @go-login="authView = 'login'"
    @back="authView = 'none'"
  />
    <ProfileModal 
    v-if="showProfileModal"
    :user="user"
    @close="showProfileModal = false"
  />

  <!-- Authenticated dashboard -->
  <Dashboard v-else-if="user" :user="user" />

  <div class="clouds-container">
    <div class="cloud cloud-solid"></div>
    <div class="cloud cloud-transparent"></div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

import NavBar      from './components/NavBar.vue';
import LoginForm   from './components/LoginForm.vue';
import RegisterForm from './components/RegisterForm.vue';
import Dashboard   from './components/Dashboard.vue';
import ProfileModal from './components/ProfileModal.vue';

import './assets/style.css';

const user     = ref(null);
const authView = ref('none'); // 'none' | 'login' | 'register'
const showProfileModal = ref(false);

onMounted(() => {
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

const refreshUser = () => {
  
};
</script>
