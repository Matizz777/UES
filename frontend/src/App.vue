<template>
  <nav class="navbar">
    <div class="logo">
      <span class="logo-icon">☁️</span> UES
    </div>

    <div class="auth-buttons">
      <template v-if="!user">
        <button class="btn-login">Pieslēgties</button>
        <button class="btn-register" @click="showRegister = true">Reģistrēties</button>
      </template>

      <template v-else>
        <div class="user-menu">
          <div class="user-info">
            <div class="avatar">{{ user.username[0].toUpperCase() }}</div>
            <div class="user-details">
              <span class="welcome-msg"> {{ user.username }}</span>
              <span class="user-role">
                {{ user.roles === 2 ? 'Pakalpojuma sniedzējs' : 'Klients' }}
              </span>
            </div>
          </div>
          <button class="btn-logout" @click="handleLogout" title="Iziet">
            <span class="logout-icon">→</span>
          </button>
        </div>
      </template>
    </div>
  </nav>

  <div class="apraksts" v-if="!user && !showRegister">
    <main class="hero">
      <h1>Universālā e-pierakstu sistēma</h1>
      <p>Pieraksts pāris klikšķu attālumā</p>
    </main>
  </div>

  <div class="form-container" v-else-if="!user && showRegister">
    <div class="register-card">
      <h2>Izveidot kontu</h2>
      <input type="text" v-model="regData.username" placeholder="Lietotājvārds" />
      <input type="email" v-model="regData.email" placeholder="E-pasts" />
      <input type="password" v-model="regData.password" placeholder="Parole" />
      <select v-model="regData.roles" class="role-select">
        <option value="3">Esmu klients</option>
        <option value="2">Esmu pakalpojuma sniedzējs</option>
      </select>
      <button class="btn-register" @click="submitRegistration">Sākt darbu</button>
      <p @click="showRegister = false" class="back-link">Atpakaļ</p>
    </div>
  </div>

  <div class="dashboard-container" v-else>
    <main class="dashboard-content">
      <h2>Sveicināti darba vidē!</h2>
      <div class="dashboard-grid">
        <div class="card" v-if="user.roles === 2">
          <h3>Tavi pakalpojumi</h3>
          <p>Šeit tu vari pievienot jaunus pierakstu laikus.</p>
        </div>
        <div class="card">
          <h3>Tavi pieraksti</h3>
          <p>Pārvaldi savas rezervācijas šeit.</p>
        </div>
      </div>
    </main>
  </div>

  <div class="clouds-container">
    <div class="cloud cloud-solid"></div>
    <div class="cloud cloud-transparent"></div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import './assets/style.css';
import axios from 'axios';

const showRegister = ref(false);
const user = ref(null); 

const regData = reactive({
  username: '',
  email: '',
  password: '',
  roles: '3'
});

onMounted(() => {
  const savedUser = localStorage.getItem('user_auth');
  if (savedUser) {
    const parsedUser = JSON.parse(savedUser);
    user.value = parsedUser;
    
    axios.defaults.headers.common['Authorization'] = `Bearer ${parsedUser.token}`;
  }
});

const submitRegistration = async () => {
  try {
    const response = await axios.post('http://127.0.0.1:8080/api/register/', regData);
    
    const authData = response.data;
    user.value = authData;
    
    localStorage.setItem('user_auth', JSON.stringify(authData));
    
    axios.defaults.headers.common['Authorization'] = `Bearer ${authData.token}`;

    showRegister.value = false;
    alert("Reģistrācija veiksmīga!");
  } catch (error) {
    const errorMsg = error.response?.data?.error || "Servera kļūda";
    alert("Kļūda: " + errorMsg);
  }
};

const handleLogout = () => {
  user.value = null;
  localStorage.removeItem('user_auth');
  delete axios.defaults.headers.common['Authorization'];
};
</script>