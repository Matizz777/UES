<template>
  <div class="form-container">
    <div class="register-card">
      <LanguageSelector />
      <h2>{{ $t('forgot_password') }}</h2>
      
      <p class="info-text">{{ $t('forgot_password_instruction') }}</p>

      <div v-if="message" class="success-banner">{{ message }}</div>
      <div v-if="errorMsg" class="error-banner">{{ errorMsg }}</div>

      <input
        type="email"
        v-model="email"
        :placeholder="$t('email')"
        @keyup.enter="submit"
      />

      <button class="btn-register" @click="submit" :disabled="loading">
        {{ loading ? $t('loading') : $t('send_reset_link') }}
      </button>

      <p class="back-link" @click="$emit('back')">← {{ $t('back_to_login') }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';
import LanguageSelector from './LanguageSelector.vue';

const emit = defineEmits(['back']);

const email = ref('');
const loading = ref(false);
const message = ref('');
const errorMsg = ref('');

const submit = async () => {
  if (!email.value) {
    errorMsg.value = 'Lūdzu, ievadiet e-pasta adresi.';
    return;
  }

  loading.value = true;
  errorMsg.value = '';
  message.value = '';

  try {
    const response = await axios.post('http://127.0.0.1:8080/api/password-reset/request/', {
      email: email.value
    });
    message.value = response.data.message || 'Paroles atjaunošanas saite nosūtīta uz jūsu e-pastu.';
  } catch (err) {
    errorMsg.value = err.response?.data?.error || 'Kļūda. Lūdzu, mēģiniet vēlreiz.';
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.info-text {
  font-size: 0.85rem;
  color: #666;
  margin-bottom: 1rem;
  text-align: center;
}

.success-banner {
  background: #e8f5e9;
  color: #2e7d32;
  padding: 0.75rem;
  border-radius: 10px;
  margin-bottom: 1rem;
  font-size: 0.85rem;
  text-align: center;
}
.form-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  position: relative;
  z-index: 2;
  padding: 2rem;
}
</style>