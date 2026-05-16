<template>
  <div class="reservations-view fade-in">
    <div class="section-header">
      <h2>{{ user.roles === 2 ? 'Klientu pieteikumi' : 'Mani plānotie pieraksti' }}</h2>
    </div>

    <div v-if="loading" class="empty-state"><p>Ielādē...</p></div>

    <div v-else-if="reservations.length === 0" class="empty-state">
      <p>Šeit vēl nekas neparādās.</p>
    </div>

    <div class="res-list-container" v-else>
      <div v-for="res in reservations" :key="res.id" class="res-card-modern">
        <div class="res-main-info">
          <div class="res-date-box">
            <span class="day">{{ res.date.split('-')[2] }}</span>
            <span class="month">{{ monthName(res.date.split('-')[1]) }}</span>
          </div>
          <div class="res-details">
            <h4>{{ res.service }}</h4>
            <div class="res-meta">
              <span>🕙 {{ res.time && res.time !== 'Nav laika' ? res.time.slice(0, 5) : 'Laiks nav norādīts' }}</span>
              <span v-if="user.roles === 2">👤 Klients: <strong>{{ res.client_name }}</strong></span>
              <span v-else>👤 Speciālists: <strong>{{ res.provider_name || 'Nav norādīts' }}</strong></span>
              <span class="res-price">💶 {{ res.booked_price ? res.booked_price + ' €' : 'Cena nav fiksēta' }}</span>
            </div>
          </div>
        </div>
        <button class="btn-cancel-text" @click="cancel(res.id)">Atcelt</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

const props = defineProps({ user: Object });

const reservations = ref([]);
const loading      = ref(false);

const MONTHS = ['Jan','Feb','Mar','Apr','Mai','Jūn','Jūl','Aug','Sep','Okt','Nov','Dec'];
const monthName = (m) => MONTHS[parseInt(m) - 1] || m;

const load = async () => {
  loading.value = true;
  try {
    const { data } = await axios.get('http://127.0.0.1:8080/api/my-reservations/', {
      params: { role: props.user.roles }
    });
    reservations.value = data;
  } catch {
    alert('Nevarēja ielādēt pierakstus!');
  } finally {
    loading.value = false;
  }
};

const cancel = async (id) => {
  if (!confirm('Vai tiešām vēlaties atcelt šo pierakstu?')) return;
  try {
    await axios.delete(`http://127.0.0.1:8080/api/cancel-booking/${id}/`);
    await load();
  } catch {
    alert('Kļūda atceļot pierakstu');
  }
};

onMounted(load);
</script>

<style scoped>
.res-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem 1rem;
  font-size: 0.9rem;
  color: #666;
  margin-top: 0.25rem;
}

.res-price {
  color: #2e7d32;
  font-weight: 600;
}
</style>