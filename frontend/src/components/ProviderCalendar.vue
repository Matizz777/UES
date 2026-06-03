<template>
  <div class="provider-calendar fade-in">
    <div class="view-header">
      <button @click="$emit('back')" class="btn-back">← {{ $t('back') }}</button>
      <h2>{{ $t('my_calendar') }}</h2>
    </div>

    <div class="cal-nav">
      <button @click="changeMonth(-1)">‹</button>
      <span>{{ monthName }} {{ year }}</span>
      <button @click="changeMonth(1)">›</button>
    </div>

    <!-- Day detail panel -->
    <div v-if="selectedDay" class="day-panel">
      <h3>{{ selectedDay }}. {{ monthName }}</h3>

      <div v-if="selectedDayBookings.length === 0" class="empty-day">
        <p>{{ $t('no_bookings_this_day') }}</p>
      </div>

      <div v-else class="timeline">
        <div v-for="b in selectedDayBookings" :key="b.id" class="timeline-block">
          <div class="timeline-time">
            <span class="t-start">{{ b.start }}</span>
            <span class="t-end">{{ b.end }}</span>
          </div>
          <div class="timeline-content">
            <div class="timeline-service">{{ b.service }}</div>
            <div class="timeline-client">👤 {{ $t('client') }}: {{ b.client_name }}</div>
            <div class="timeline-price" v-if="b.booked_price">💶 {{ b.booked_price }} €</div>
          </div>
          <div class="timeline-actions">
            <button class="btn-reschedule" @click="openReschedule(b)">✏️ {{ $t('reschedule') }}</button>
            <button class="btn-cancel-booking" @click="openCancel(b)">✕ {{ $t('cancel') }}</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Cancel modal -->
    <div v-if="cancelTarget" class="modal-overlay" @click.self="cancelTarget = null">
      <div class="modal-card">
        <h3>{{ $t('cancel_booking') }}</h3>
        <p><strong>{{ cancelTarget.service }}</strong> — {{ cancelTarget.client_name }}</p>
        <p>{{ cancelTarget.date }} {{ cancelTarget.start }} – {{ cancelTarget.end }}</p>
        <label class="modal-label">{{ $t('cancel_reason') }}</label>
        <textarea v-model="cancelReason" :placeholder="$t('cancel_reason_placeholder')" rows="3"></textarea>
        <div class="modal-footer">
          <button class="btn-secondary" @click="cancelTarget = null">{{ $t('close') }}</button>
          <button class="btn-danger" @click="confirmCancel" :disabled="!cancelReason.trim()">{{ $t('cancel_booking') }}</button>
        </div>
      </div>
    </div>

    <!-- Reschedule modal -->
    <div v-if="rescheduleTarget" class="modal-overlay" @click.self="rescheduleTarget = null">
      <div class="modal-card">
        <h3>{{ $t('reschedule') }}</h3>
        <p><strong>{{ rescheduleTarget.service }}</strong> — {{ rescheduleTarget.client_name }}</p>
        <p class="old-time">{{ $t('current_time') }}: {{ rescheduleTarget.date }} {{ rescheduleTarget.start }}</p>

        <label class="modal-label">{{ $t('select_date') }}</label>
        <input type="date" v-model="newDate" :min="todayStr" />

        <label class="modal-label">{{ $t('select_time') }}</label>
        <input type="time" v-model="newTime" />

        <label class="modal-label">{{ $t('reschedule_reason') }}</label>
        <textarea v-model="rescheduleReason" :placeholder="$t('reschedule_reason_placeholder')" rows="2"></textarea>

        <div class="modal-footer">
          <button class="btn-secondary" @click="rescheduleTarget = null">{{ $t('close') }}</button>
          <button class="btn-primary" @click="confirmReschedule" :disabled="!newDate || !newTime || !rescheduleReason.trim()">
            {{ $t('save') }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading-overlay">{{ $t('loading') }}</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';

const props = defineProps({ user: Object });
defineEmits(['back']);

const now         = new Date();
const viewDate    = ref(new Date(now.getFullYear(), now.getMonth(), 1));
const bookings    = ref([]);
const loading     = ref(false);
const selectedDay = ref(null);

// Cancel state
const cancelTarget = ref(null);
const cancelReason = ref('');

// Reschedule state
const rescheduleTarget = ref(null);
const newDate          = ref('');
const newTime          = ref('');
const rescheduleReason = ref('');

const todayStr = new Date().toISOString().split('T')[0];

const year  = computed(() => viewDate.value.getFullYear());
const month = computed(() => viewDate.value.getMonth() + 1);
const monthName = computed(() =>
  viewDate.value.toLocaleString('lv-LV', { month: 'long' })
);
const daysInMonth = computed(() =>
  new Date(year.value, month.value, 0).getDate()
);
const firstDayOffset = computed(() => {
  const d = new Date(year.value, month.value - 1, 1).getDay();
  return d === 0 ? 6 : d - 1;
});

const isToday = (day) => {
  const t = new Date();
  return day === t.getDate() && month.value === t.getMonth() + 1 && year.value === t.getFullYear();
};

const getBookingsForDay = (day) => {
  const d = String(day).padStart(2, '0');
  const m = String(month.value).padStart(2, '0');
  const dateStr = `${year.value}-${m}-${d}`;
  return bookings.value.filter(b => b.date === dateStr);
};

const hasBookings = (day) => getBookingsForDay(day).length > 0;

const selectedDayBookings = computed(() => {
  if (!selectedDay.value) return [];
  return getBookingsForDay(selectedDay.value);
});

const selectDay = (day) => {
  selectedDay.value = selectedDay.value === day ? null : day;
};

const loadBookings = async () => {
  loading.value = true;
  try {
    const { data } = await axios.get('http://127.0.0.1:8080/api/provider-calendar/', {
      params: { year: year.value, month: month.value }
    });
    console.log('Ielādētie pieraksti:', data);
    console.log('Pierakstu skaits:', data.length);
    bookings.value = data;
  } catch (e) {
    console.error('Kļūda ielādējot kalendāru:', e);
  } finally {
    loading.value = false;
  }
};
const changeMonth = async (offset) => {
  viewDate.value = new Date(year.value, month.value - 1 + offset, 1);
  selectedDay.value = null;
  await loadBookings();
};

// ── Cancel ────────────────────────────────────────────────────────────────────
const openCancel = (b) => {
  cancelTarget.value = b;
  cancelReason.value = '';
};

const confirmCancel = async () => {
  try {
    console.log('Atceļ pierakstu...');
    await axios.delete(`http://127.0.0.1:8080/api/cancel-booking/${cancelTarget.value.id}/`, {
      data: { reason: cancelReason.value }
    });
    console.log('Pieraksts atcelts');
    cancelTarget.value = null;
    
    console.log('Pirms loadBookings, bookings garums:', bookings.value.length);
    await loadBookings();
    console.log('Pēc loadBookings, bookings garums:', bookings.value.length);
    
    if (selectedDay.value) {
      const currentDay = selectedDay.value;
      selectedDay.value = null;
      setTimeout(() => {
        selectedDay.value = currentDay;
        console.log('SelectedDay atjaunots');
      }, 50);
    }
  } catch (err) {
    console.error('Kļūda:', err);
    alert('Kļūda atceļot pierakstu.');
  }
};

// ── Reschedule ────────────────────────────────────────────────────────────────
const openReschedule = (b) => {
  rescheduleTarget.value = b;
  newDate.value          = b.date;
  newTime.value          = b.start;
  rescheduleReason.value = '';
};

const confirmReschedule = async () => {
  try {
    await axios.patch(`http://127.0.0.1:8080/api/reschedule-booking/${rescheduleTarget.value.id}/`, {
      res_date: newDate.value,
      res_time: newTime.value,
      reason: rescheduleReason.value,
    });
    rescheduleTarget.value = null;
    await loadBookings();
    
    if (selectedDay.value) {
      const currentDay = selectedDay.value;
      selectedDay.value = null;
      setTimeout(() => {
        selectedDay.value = currentDay;
      }, 50);
    }
  } catch (err) {
    alert('Kļūda pārceļot pierakstu: ' + (err.response?.data?.error ?? ''));
  }
};

onMounted(loadBookings);
</script>

<style scoped>
.provider-calendar { 
  padding: 0.5rem;
  width: 100%;
  margin: 0 auto;
}

@media (min-width: 768px) {
  .provider-calendar {
    width: 95%;
  }
}

@media (min-width: 1200px) {
  .provider-calendar {
    width: 900px;
  }
}

@media (min-width: 1600px) {
  .provider-calendar {
    width: 1100px;
  }
}

.cal-nav {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin: 1rem 0;
  font-size: 1rem;
  font-weight: 600;
  flex-wrap: wrap;
}

@media (min-width: 768px) {
  .cal-nav {
    gap: 1.5rem;
    font-size: 1.1rem;
  }
}

.cal-nav button {
  background: none;
  border: 1px solid #ccc;
  border-radius: 8px;
  width: 36px;
  height: 36px;
  font-size: 1.2rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

@media (max-width: 480px) {
  .cal-nav button {
    width: 32px;
    height: 32px;
    font-size: 1rem;
  }
}

.month-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
  margin-bottom: 1.5rem;
}

@media (min-width: 768px) {
  .month-grid {
    gap: 8px;
  }
}

@media (min-width: 1200px) {
  .month-grid {
    gap: 12px;
  }
}

.grid-header {
  text-align: center;
  font-size: 0.7rem;
  color: #aaa;
  padding: 0.4rem 0;
  font-weight: 600;
}

@media (min-width: 768px) {
  .grid-header {
    font-size: 0.8rem;
  }
}

@media (min-width: 1200px) {
  .grid-header {
    font-size: 0.9rem;
  }
}

.grid-cell {
  min-height: 60px;
  border-radius: 10px;
  padding: 0.3rem;
  background: var(--color-background-soft, #f9f9f9);
  cursor: pointer;
  transition: background 0.15s;
}

@media (min-width: 768px) {
  .grid-cell {
    min-height: 80px;
    padding: 0.4rem;
  }
}

@media (min-width: 1200px) {
  .grid-cell {
    min-height: 100px;
    padding: 0.6rem;
  }
}

.grid-cell:hover { background: #e8f5e9; }
.grid-cell.empty { background: transparent; cursor: default; }

.grid-cell.today .day-num {
  background: #388e3c;
  color: #fff;
  border-radius: 50%;
  width: 22px;
  height: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
}

@media (min-width: 768px) {
  .grid-cell.today .day-num {
    width: 26px;
    height: 26px;
    font-size: 0.85rem;
  }
}

.grid-cell.selected { background: #c8e6c9; border: 2px solid #388e3c; }
.grid-cell.has-bookings { background: #f1f8e9; }

.day-num {
  font-size: 0.8rem;
  font-weight: 600;
  color: #444;
  display: inline-block;
  width: 22px;
  height: 22px;
  line-height: 22px;
  text-align: center;
}

@media (min-width: 768px) {
  .day-num {
    font-size: 0.85rem;
    width: 26px;
    height: 26px;
    line-height: 26px;
  }
}

@media (min-width: 1200px) {
  .day-num {
    font-size: 0.95rem;
    width: 30px;
    height: 30px;
    line-height: 30px;
  }
}

.booking-dots { 
  display: flex; 
  flex-wrap: wrap; 
  gap: 2px; 
  margin-top: 4px; 
}

@media (min-width: 768px) {
  .booking-dots { 
    gap: 3px; 
    margin-top: 6px; 
  }
}

.dot { 
  width: 6px; 
  height: 6px; 
  border-radius: 50%; 
  background: #388e3c; 
  display: inline-block; 
}

@media (min-width: 768px) {
  .dot { 
    width: 8px; 
    height: 8px; 
  }
}

.dot-more { 
  font-size: 0.6rem; 
  color: #888; 
}

@media (min-width: 768px) {
  .dot-more { 
    font-size: 0.7rem; 
  }
}

.day-panel {
  background: var(--color-background-soft, #f9f9f9);
  border-radius: 14px;
  padding: 1rem;
  margin-top: 0.5rem;
}

@media (min-width: 768px) {
  .day-panel {
    padding: 1.25rem;
  }
}

.day-panel h3 { 
  margin: 0 0 1rem; 
  font-size: 1rem; 
  text-transform: capitalize; 
}

@media (min-width: 768px) {
  .day-panel h3 { 
    font-size: 1.1rem; 
  }
}

.empty-day { 
  color: #aaa; 
  font-size: 0.85rem; 
}

.timeline { 
  display: flex; 
  flex-direction: column; 
  gap: 0.75rem; 
}

.timeline-block {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  background: #fff;
  border-radius: 10px;
  padding: 0.75rem;
  border-left: 4px solid #388e3c;
}

@media (min-width: 640px) {
  .timeline-block {
    flex-direction: row;
    align-items: center;
    gap: 1rem;
    padding: 0.75rem 1rem;
  }
}

.timeline-time {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.82rem;
  color: #888;
}

@media (min-width: 640px) {
  .timeline-time {
    flex-direction: column;
    min-width: 48px;
    gap: 0;
  }
}

.t-start { 
  font-weight: 700; 
  color: #333; 
  font-size: 0.9rem; 
}

.timeline-content { 
  flex: 1; 
  display: flex; 
  flex-direction: column; 
  gap: 0.2rem; 
}

.timeline-service { 
  font-weight: 600; 
  font-size: 0.9rem; 
}

@media (min-width: 768px) {
  .timeline-service { 
    font-size: 0.95rem; 
  }
}

.timeline-client { 
  font-size: 0.8rem; 
  color: #666; 
}

.timeline-price { 
  font-size: 0.8rem; 
  color: #2e7d32; 
  font-weight: 600; 
}

.timeline-actions { 
  display: flex; 
  gap: 0.5rem; 
  justify-content: flex-end;
}

.btn-reschedule,
.btn-cancel-booking {
  padding: 0.4rem 1rem;
  font-size: 0.8rem;
  border-radius: 20px;
  font-weight: 500;
  transition: all 0.2s ease;
  cursor: pointer;
}

.btn-reschedule {
  background: #4a90e2;
  border: none;
  color: white;
}

.btn-reschedule:hover {
  background: #357abd;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(74, 144, 226, 0.3);
}

.btn-cancel-booking {
  background: #fff;
  border: 1px solid #e53935;
  color: #e53935;
}

.btn-cancel-booking:hover {
  background: #e53935;
  color: white;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(229, 57, 53, 0.3);
}

@media (min-width: 768px) {
  .btn-reschedule,
  .btn-cancel-booking {
    padding: 0.5rem 1.2rem;
    font-size: 0.85rem;
  }
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-card {
  background: #fff;
  border-radius: 16px;
  padding: 1.25rem;
  width: 100%;
  max-width: 400px;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  box-shadow: 0 8px 32px rgba(0,0,0,0.18);
}

@media (min-width: 768px) {
  .modal-card {
    padding: 1.75rem;
    max-width: 440px;
  }
}

.modal-card h3 { 
  margin: 0 0 0.25rem; 
  font-size: 1rem; 
}

@media (min-width: 768px) {
  .modal-card h3 { 
    font-size: 1.15rem; 
  }
}

.modal-card p { 
  margin: 0; 
  font-size: 0.85rem; 
  color: #555; 
}

.old-time { 
  color: #aaa !important; 
  font-size: 0.8rem !important; 
}

.modal-label {
  font-size: 0.8rem;
  color: #888;
  margin-top: 0.5rem;
}

.modal-card textarea,
.modal-card input[type="date"],
.modal-card input[type="time"] {
  width: 100%;
  border: 1px solid #ccc;
  border-radius: 8px;
  padding: 0.5rem;
  font-family: inherit;
  font-size: 0.85rem;
  box-sizing: border-box;
  resize: vertical;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 0.5rem;
}

.btn-danger {
  background: #e53935;
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 0.4rem 1rem;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.85rem;
}

.btn-danger:disabled { 
  opacity: 0.5; 
  cursor: not-allowed; 
}

.loading-overlay { 
  text-align: center; 
  color: #aaa; 
  padding: 2rem; 
}
</style>