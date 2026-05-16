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
            <span class="month">{{ res.date.split('-')[1] }}</span>
          </div>
          <div class="res-details">
            <h4>{{ res.service }}</h4>
            <p>
              🕙 {{ res.time && res.time !== 'Nav laika' ? res.time.slice(0, 5) : 'Laiks nav norādīts' }}
              • {{ user.roles === 2 ? 'Klients: ' + res.client_name : 'Pie speciālista' }}
            </p>
          </div>
        </div>
        <button class="btn-cancel-text" @click="cancel(res.id)">Atcelt pierakstu</button>
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