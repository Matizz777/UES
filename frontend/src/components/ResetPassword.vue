<template>
  <div class="form-container">
    <div class="register-card">
      <LanguageSelector inline />
      <h2>{{ $t('reset_password') }}</h2>

      <div v-if="errorMsg" class="error-banner">{{ errorMsg }}</div>
      <div v-if="message" class="success-banner">{{ message }}</div>

      <input
        type="password"
        v-model="newPassword"
        :placeholder="$t('new_password')"
        @keyup.enter="submit"
      />
      <input
        type="password"
        v-model="confirmPassword"
        :placeholder="$t('confirm_password')"
        @keyup.enter="submit"
      />

      <button class="btn-register" @click="submit" :disabled="loading">
        {{ loading ? $t('loading') : $t('reset_password') }}
      </button>

      <!-- Atpakaļ poga -->
      <button class="btn-back-link" @click="goBack">
        ← {{ $t('back_to_login') }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import LanguageSelector from './LanguageSelector.vue';

const emit = defineEmits(['go-login']);

const props = defineProps({
  token: String
});

const newPassword = ref('');
const confirmPassword = ref('');
const loading = ref(false);
const message = ref('');
const errorMsg = ref('');

const goBack = () => {
  // Notīrīt URL no reset token
  window.history.pushState({}, '', '/');
  emit('go-login');
};

const submit = async () => {
  if (!newPassword.value || !confirmPassword.value) {
    errorMsg.value = 'Lūdzu, aizpildiet abus laukus.';
    return;
  }

  if (newPassword.value !== confirmPassword.value) {
    errorMsg.value = 'Paroles nesakrīt.';
    return;
  }

  if (newPassword.value.length < 6) {
    errorMsg.value = 'Parolei jābūt vismaz 6 rakstzīmēm.';
    return;
  }

  loading.value = true;
  errorMsg.value = '';
  message.value = '';

  try {
    await axios.post('http://127.0.0.1:8080/api/password-reset/confirm/', {
      token: props.token,
      new_password: newPassword.value
    });
    message.value = 'Parole veiksmīgi mainīta! Jūs varat pieslēgties.';
    
    // Pēc 2 sekundēm notīrīt URL un doties uz login
    setTimeout(() => {
      window.history.pushState({}, '', '/');
      emit('go-login');
    }, 2000);
  } catch (err) {
    errorMsg.value = err.response?.data?.error || 'Kļūda mainot paroli. Saite var būt novecojusi.';
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  if (!props.token) {
    errorMsg.value = 'Nederīga paroles atjaunošanas saite.';
  }
});
</script>

<style scoped>
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

.register-card {
  background: white;
  border-radius: 30px;
  padding: 2rem;
  width: 100%;
  max-width: 450px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.btn-back-link {
  background: none;
  border: none;
  color: #666;
  cursor: pointer;
  font-size: 0.85rem;
  margin-top: 1rem;
  padding: 0.5rem;
  width: 100%;
}

.btn-back-link:hover {
  color: #4a90e2;
  text-decoration: underline;
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

.error-banner {
  background: #ffebee;
  color: #c62828;
  padding: 0.75rem;
  border-radius: 10px;
  margin-bottom: 1rem;
  font-size: 0.85rem;
  text-align: center;
}

input {
  width: 100%;
  padding: 0.75rem;
  margin-bottom: 1rem;
  border: 1px solid #ddd;
  border-radius: 12px;
  font-size: 0.9rem;
  box-sizing: border-box;
}

input:focus {
  outline: none;
  border-color: #4a90e2;
}

.btn-register {
  width: 100%;
  padding: 0.75rem;
  background: #4a90e2;
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-register:hover {
  background: #357abd;
  transform: translateY(-1px);
}

.btn-register:disabled {
  background: #ccc;
  cursor: not-allowed;
}
</style>