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
            <div v-if="!canReschedule(res) && user.roles === 3" class="warning-note">
              ⚠️ Nevar pārcelt - mazāk par 24h līdz pierakstam
            </div>
          </div>
        </div>
        <div class="res-actions">
          <button 
            v-if="user.roles === 3 && canReschedule(res)" 
            class="btn-reschedule" 
            @click="openReschedule(res)"
          >
            📅 Pārcelt
          </button>
          <button 
            class="btn-cancel-text" 
            @click="cancel(res.id)"
          >
            Atcelt
          </button>
        </div>
      </div>
    </div>

    <div v-if="rescheduleTarget" class="modal-overlay" @click.self="rescheduleTarget = null">
      <div class="modal-card">
        <h3>Pārcelt pierakstu</h3>
        <p><strong>{{ rescheduleTarget.service }}</strong></p>
        <p class="old-time">Esošais laiks: {{ rescheduleTarget.date }} {{ rescheduleTarget.time }}</p>

        <label class="modal-label">Jauns datums</label>
        <input type="date" v-model="newDate" :min="minDate" />

        <label class="modal-label">Jauns laiks</label>
        <select v-model="newTime" :disabled="loadingTimes">
          <option value="">Vispirms izvēlieties datumu</option>
          <option v-for="t in availableTimes" :key="t" :value="t">{{ t }}</option>
        </select>

        <div class="modal-footer">
          <button class="btn-secondary" @click="rescheduleTarget = null">Aizvērt</button>
          <button class="btn-primary" @click="confirmReschedule" :disabled="!newDate || !newTime">
            Apstiprināt
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import axios from 'axios';

const props = defineProps({ user: Object });

const reservations = ref([]);
const loading = ref(false);
const rescheduleTarget = ref(null);
const newDate = ref('');
const newTime = ref('');
const availableTimes = ref([]);
const loadingTimes = ref(false);

const MONTHS = ['Jan','Feb','Mar','Apr','Mai','Jūn','Jūl','Aug','Sep','Okt','Nov','Dec'];
const monthName = (m) => MONTHS[parseInt(m) - 1] || m;

const canReschedule = (res) => {
  if (!res || !res.date || !res.time) return false;
  const bookingDateTime = new Date(`${res.date}T${res.time}`);
  const now = new Date();
  const hoursUntil = (bookingDateTime - now) / (1000 * 60 * 60);
  return hoursUntil >= 24;
};

const minDate = computed(() => {
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  return tomorrow.toISOString().split('T')[0];
});

const load = async () => {
  loading.value = true;
  try {
    const { data } = await axios.get('http://127.0.0.1:8080/api/my-reservations/', {
      params: { role: props.user.roles }
    });
    reservations.value = data;
  } catch (err) {
    console.error('Error loading reservations:', err);
    alert('Nevarēja ielādēt pierakstus!');
  } finally {
    loading.value = false;
  }
};

const cancel = async (id) => {
  if (!confirm('Vai tiešām vēlaties atcelt šo pierakstu?')) return;
  
  try {
    await axios.delete(`http://127.0.0.1:8080/api/cancel-booking/${id}/`, {
      data: { is_client_cancel: props.user.roles === 3 }
    });
    await load();
  } catch (err) {
    alert(err.response?.data?.error || 'Kļūda atceļot pierakstu');
  }
};

const openReschedule = (res) => {
  rescheduleTarget.value = res;
  newDate.value = '';
  newTime.value = '';
  availableTimes.value = [];
};

const confirmReschedule = async () => {
  try {
    await axios.patch(`http://127.0.0.1:8080/api/reschedule-booking/${rescheduleTarget.value.id}/`, {
      res_date: newDate.value,
      res_time: newTime.value,
      is_client_reschedule: props.user.roles === 3,
    });
    rescheduleTarget.value = null;
    await load();
  } catch (err) {
    alert(err.response?.data?.error || 'Kļūda pārceļot pierakstu');
  }
};

watch(newDate, async (date) => {
  if (date && rescheduleTarget.value) {
    loadingTimes.value = true;
    try {
      const { data } = await axios.get('http://127.0.0.1:8080/api/occupied-times/', {
        params: {
          service_id: rescheduleTarget.value.service_id,
          provider_id: rescheduleTarget.value.provider_id,
          date: date
        }
      });
      availableTimes.value = data.available || [];
    } catch {
      availableTimes.value = [];
    } finally {
      loadingTimes.value = false;
    }
  }
});

onMounted(load);
</script>

<style scoped>
.warning-note {
  font-size: 0.75rem;
  color: #e53935;
  margin-top: 0.25rem;
}

.res-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.btn-reschedule {
  background: none;
  border: 1px solid #2196f3;
  color: #2196f3;
  border-radius: 8px;
  padding: 0.3rem 0.7rem;
  cursor: pointer;
  font-size: 0.8rem;
}

.btn-reschedule:hover {
  background: #2196f3;
  color: white;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-card {
  background: #fff;
  border-radius: 16px;
  padding: 1.5rem;
  width: 90%;
  max-width: 400px;
}

.modal-card h3 {
  margin-top: 0;
  margin-bottom: 1rem;
}

.old-time {
  color: #888;
  font-size: 0.85rem;
  margin-bottom: 1rem;
}

.modal-label {
  display: block;
  font-size: 0.85rem;
  font-weight: 600;
  margin-top: 1rem;
  margin-bottom: 0.25rem;
  color: #555;
}

.modal-card input,
.modal-card select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-family: inherit;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.5rem;
}

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