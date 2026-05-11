<template>
  <div class="form-container">
    <div class="register-card">
      <h2>Pieslēgties</h2>

      <div v-if="errorMsg" class="error-banner">{{ errorMsg }}</div>

      <input
        type="text"
        v-model="credentials.username"
        placeholder="Lietotājvārds"
        @keyup.enter="submit"
      />
      <input
        type="password"
        v-model="credentials.password"
        placeholder="Parole"
        @keyup.enter="submit"
      />

      <button class="btn-register" @click="submit" :disabled="loading">
        {{ loading ? 'Lādē...' : 'Pieslēgties' }}
      </button>

      <p class="back-link" @click="$emit('go-register')">
        Nav konta? <span class="link-accent">Reģistrēties</span>
      </p>
      <p class="back-link" @click="$emit('back')">← Atpakaļ uz sākumu</p>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue';
import axios from 'axios';

const emit = defineEmits(['login-success', 'go-register', 'back']);

const credentials = reactive({ username: '', password: '' });
const loading     = ref(false);
const errorMsg    = ref('');

const submit = async () => {
  if (loading.value) return;
  errorMsg.value = '';

  if (!credentials.username || !credentials.password) {
    errorMsg.value = 'Lūdzu, aizpildi visus laukus.';
    return;
  }

  loading.value = true;
  try {
    const { data } = await axios.post('http://127.0.0.1:8080/api/login/', credentials);
    emit('login-success', data);
  } catch (err) {
    errorMsg.value = err.response?.data?.error || 'Nepareizs lietotājvārds vai parole.';
  } finally {
    loading.value = false;
  }
};
</script>