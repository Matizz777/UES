<template>
  <div class="form-container">
    <div class="register-card">
      <h2>Izveidot kontu</h2>

      <div v-if="errorMsg" class="error-banner">{{ errorMsg }}</div>

      <input type="text"     v-model="regData.username" placeholder="Lietotājvārds" />
      <input type="email"    v-model="regData.email"    placeholder="E-pasts" />
      <input type="password" v-model="regData.password" placeholder="Parole" />

      <select v-model="regData.roles" class="role-select">
        <option value="3">Esmu klients</option>
        <option value="2">Esmu pakalpojuma sniedzējs</option>
      </select>

      <div v-if="regData.roles == '2'" class="provider-extra-fields">
        <select v-model="regData.industry" class="role-select">
          <option value="">Izvēlies nozari</option>
          <option value="Skaistumkopšana">Skaistumkopšana</option>
          <option value="Medicīna">Medicīna</option>
          <option value="IT pakalpojumi">IT pakalpojumi</option>
          <option value="Sports">Sports un Fitness</option>
        </select>
        <textarea
          v-model="regData.description"
          placeholder="Pastāsti par saviem pakalpojumiem..."
          class="desc-textarea"
        ></textarea>
      </div>

      <button class="btn-register" @click="submit" :disabled="loading">
        {{ loading ? 'Lādē...' : 'Sākt darbu' }}
      </button>

      <p class="back-link" @click="$emit('go-login')">
        Jau ir konts? <span class="link-accent">Pieslēgties</span>
      </p>
      <p class="back-link" @click="$emit('back')">← Atpakaļ uz sākumu</p>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue';
import axios from 'axios';

const emit = defineEmits(['register-success', 'go-login', 'back']);

const regData  = reactive({ username: '', email: '', password: '', roles: '3', industry: '', description: '' });
const loading  = ref(false);
const errorMsg = ref('');

const submit = async () => {
  errorMsg.value = '';

  if (!regData.username || !regData.email || !regData.password) {
    errorMsg.value = 'Lūdzu, aizpildi visus obligātos laukus.';
    return;
  }
  if (regData.roles == '2' && !regData.industry) {
    errorMsg.value = 'Lūdzu, izvēlies nozari.';
    return;
  }

  const payload = { ...regData };
  if (payload.roles == 3) {
    payload.industry    = 'Klients';
    payload.description = 'Lietotāja profils';
  }

  loading.value = true;
  try {
    const { data } = await axios.post('http://127.0.0.1:8080/api/register/', payload);
    emit('register-success', data);
  } catch (err) {
    errorMsg.value = err.response?.data?.error || 'Servera kļūda. Mēģini vēlreiz.';
  } finally {
    loading.value = false;
  }
};
</script>
