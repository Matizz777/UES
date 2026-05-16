<template>
  <!-- Catalog list -->
  <div v-if="!viewingProvider" class="catalog-view">
    <div class="catalog-filter-wrapper">
      <div class="search-main">
        <input v-model="searchQuery" placeholder="Meklēt speciālistu..." @input="fetchProviders" />
        <span class="search-icon">🔍</span>
      </div>
      <select v-model="selectedIndustry" @change="fetchProviders" class="industry-select">
        <option value="">Visas nozares</option>
        <option value="Medicīna">Medicīna</option>
        <option value="IT pakalpojumi">IT pakalpojumi</option>
        <option value="Skaistumkopšana">Skaistumkopšana</option>
        <option value="Sports">Sports un Fitness</option>
        <option value="Cits">Cits</option>
      </select>
    </div>

    <div class="provider-grid">
      <div v-for="p in providers" :key="p.id" class="provider-card-modern">
        <div class="provider-header">
          <div class="avatar-circle">{{ p.username ? p.username[0].toUpperCase() : '?' }}</div>
          <div class="provider-title">
            <h3>{{ p.username }}</h3>
            <span class="badge-industry">{{ p.industry }}</span>
          </div>
        </div>
        <p class="provider-desc">{{ p.description }}</p>
        <button class="btn-book" @click="viewingProvider = p">Skatīt pakalpojumus</button>
      </div>
    </div>
  </div>

  <!-- Provider profile overlay -->
  <div v-if="viewingProvider" class="provider-profile-overlay">
    <div class="provider-profile-content">
      <button @click="viewingProvider = null" class="close-btn">✕</button>
      <h2>{{ viewingProvider.username }} pakalpojumi</h2>
      <div class="services-vertical-list">
        <div
          v-for="s in viewingProvider.services"
          :key="s.id"
          class="service-row"
          @click="selectService(s)"
        >
          <div class="s-info">
            <span class="s-name">{{ s.name }}</span>
            <span class="s-desc">{{ s.description }}</span>
          </div>
          <div class="s-action">
            <span class="s-price">{{ s.price }}€</span>
            <button class="btn-select">Izvēlēties</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

const emit = defineEmits(['start-booking']);

const providers        = ref([]);
const searchQuery      = ref('');
const selectedIndustry = ref('');
const viewingProvider  = ref(null);

const fetchProviders = async () => {
  try {
    const { data } = await axios.get('http://127.0.0.1:8080/api/catalog/', {
      params: { search: searchQuery.value, industry: selectedIndustry.value }
    });
    providers.value = data.map(p => ({
      id:          p.id,
      username:    p.username || p.name || 'Nezināms',
      industry:    p.industry || 'Nav norādīta',
      description: p.description || p.desc || 'Nav apraksta.',
      services:    p.services || []
    }));
  } catch (err) {
    console.error('Kļūda ielādējot katalogu:', err);
  }
};

const selectService = (service) => {
  emit('start-booking', { provider: viewingProvider.value, service });
  viewingProvider.value = null;
};

onMounted(fetchProviders);
</script>
