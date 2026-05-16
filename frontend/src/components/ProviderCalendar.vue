<template>
  <div class="provider-calendar fade-in">
    <div class="view-header">
      <button @click="$emit('back')" class="btn-back">← Atpakaļ</button>
      <h2>Mans kalendārs</h2>
    </div>

    <!-- Month nav -->
    <div class="cal-nav">
      <button @click="changeMonth(-1)">‹</button>
      <span>{{ monthName }} {{ year }}</span>
      <button @click="changeMonth(1)">›</button>
    </div>

    <!-- Month grid -->
    <div class="month-grid">
      <div v-for="d in ['Pr','Ot','Tr','Ce','Pk','Se','Sv']" :key="d" class="grid-header">{{ d }}</div>
      <div v-for="blank in firstDayOffset" :key="'b'+blank" class="grid-cell empty"></div>
      <div
        v-for="day in daysInMonth"
        :key="day"
        class="grid-cell"
        :class="{ today: isToday(day), selected: selectedDay === day, 'has-bookings': hasBookings(day) }"
        @click="selectDay(day)"
      >
        <span class="day-num">{{ day }}</span>
        <div class="booking-dots">
          <span
            v-for="(b, i) in getBookingsForDay(day).slice(0, 3)"
            :key="i"
            class="dot"
            :title="b.service + ' ' + b.start"
          ></span>
          <span v-if="getBookingsForDay(day).length > 3" class="dot-more">
            +{{ getBookingsForDay(day).length - 3 }}
          </span>
        </div>
      </div>
    </div>

    <!-- Day detail panel -->
    <div v-if="selectedDay" class="day-panel">
      <h3>{{ selectedDay }}. {{ monthName }}</h3>

      <div v-if="selectedDayBookings.length === 0" class="empty-day">
        <p>Nav rezervāciju šajā dienā.</p>
      </div>

      <div v-else class="timeline">
        <div v-for="b in selectedDayBookings" :key="b.id" class="timeline-block">
          <div class="timeline-time">
            <span class="t-start">{{ b.start }}</span>
            <span class="t-end">{{ b.end }}</span>
          </div>
          <div class="timeline-content">
            <div class="timeline-service">{{ b.service }}</div>
            <div class="timeline-client">👤 {{ b.client_name }}</div>
            <div class="timeline-price" v-if="b.booked_price">💶 {{ b.booked_price }} €</div>
          </div>
          <div class="timeline-actions">
            <button class="btn-reschedule" @click="openReschedule(b)">✏️ Pārcelt</button>
            <button class="btn-cancel-booking" @click="openCancel(b)">✕ Atcelt</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Cancel modal -->
    <div v-if="cancelTarget" class="modal-overlay" @click.self="cancelTarget = null">
      <div class="modal-card">
        <h3>Atcelt pierakstu</h3>
        <p><strong>{{ cancelTarget.service }}</strong> — {{ cancelTarget.client_name }}</p>
        <p>{{ cancelTarget.date }} {{ cancelTarget.start }} – {{ cancelTarget.end }}</p>
        <label class="modal-label">Atcelšanas iemesls (nosūtīs klientam)</label>
        <textarea v-model="cancelReason" placeholder="Piem.: Esmu saslimis, lūdzu piesakieties vēlreiz." rows="3"></textarea>
        <div class="modal-footer">
          <button class="btn-secondary" @click="cancelTarget = null">Aizvērt</button>
          <button class="btn-danger" @click="confirmCancel" :disabled="!cancelReason.trim()">Atcelt pierakstu</button>
        </div>
      </div>
    </div>

    <!-- Reschedule modal -->
    <div v-if="rescheduleTarget" class="modal-overlay" @click.self="rescheduleTarget = null">
      <div class="modal-card">
        <h3>Pārcelt pierakstu</h3>
        <p><strong>{{ rescheduleTarget.service }}</strong> — {{ rescheduleTarget.client_name }}</p>
        <p class="old-time">Esošais laiks: {{ rescheduleTarget.date }} {{ rescheduleTarget.start }}</p>

        <label class="modal-label">Jauns datums</label>
        <input type="date" v-model="newDate" :min="todayStr" />

        <label class="modal-label" style="margin-top:0.75rem;">Jauns laiks</label>
        <input type="time" v-model="newTime" />

        <label class="modal-label" style="margin-top:0.75rem;">Iemesls (nosūtīs klientam)</label>
        <textarea v-model="rescheduleReason" placeholder="Piem.: Nepieciešams pārcelt grafika izmaiņu dēļ." rows="2"></textarea>

        <div class="modal-footer">
          <button class="btn-secondary" @click="rescheduleTarget = null">Aizvērt</button>
          <button class="btn-primary" @click="confirmReschedule" :disabled="!newDate || !newTime || !rescheduleReason.trim()">
            Saglabāt
          </button>
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading-overlay">Ielādē...</div>
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
    await axios.delete(`http://127.0.0.1:8080/api/cancel-booking/${cancelTarget.value.id}/`, {
      data: { reason: cancelReason.value }
    });
    cancelTarget.value = null;
    await loadBookings();
  } catch {
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
      res_date:   newDate.value,
      res_time:   newTime.value,
      reason:     rescheduleReason.value,
    });
    rescheduleTarget.value = null;
    await loadBookings();
  } catch (err) {
    alert('Kļūda pārceļot pierakstu: ' + (err.response?.data?.error ?? ''));
  }
};

onMounted(loadBookings);
</script>

<style scoped>
.provider-calendar { padding: 0.5rem 0; }

.cal-nav {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1.5rem;
  margin: 1rem 0;
  font-size: 1.1rem;
  font-weight: 600;
}
.cal-nav button {
  background: none;
  border: 1px solid #ccc;
  border-radius: 8px;
  width: 36px; height: 36px;
  font-size: 1.2rem;
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
}

.month-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
  margin-bottom: 1.5rem;
}
.grid-header {
  text-align: center;
  font-size: 0.8rem;
  color: #aaa;
  padding: 0.4rem 0;
  font-weight: 600;
}
.grid-cell {
  min-height: 72px;
  border-radius: 10px;
  padding: 0.4rem;
  background: var(--color-background-soft, #f9f9f9);
  cursor: pointer;
  transition: background 0.15s;
}
.grid-cell:hover { background: #e8f5e9; }
.grid-cell.empty { background: transparent; cursor: default; }
.grid-cell.today .day-num {
  background: #388e3c;
  color: #fff;
  border-radius: 50%;
  width: 24px; height: 24px;
  display: flex; align-items: center; justify-content: center;
  font-size: 0.85rem;
}
.grid-cell.selected { background: #c8e6c9; border: 2px solid #388e3c; }
.grid-cell.has-bookings { background: #f1f8e9; }

.day-num {
  font-size: 0.85rem;
  font-weight: 600;
  color: #444;
  display: inline-block;
  width: 24px; height: 24px;
  line-height: 24px;
  text-align: center;
}
.booking-dots { display: flex; flex-wrap: wrap; gap: 3px; margin-top: 4px; }
.dot { width: 8px; height: 8px; border-radius: 50%; background: #388e3c; display: inline-block; }
.dot-more { font-size: 0.7rem; color: #888; }

/* Day panel */
.day-panel {
  background: var(--color-background-soft, #f9f9f9);
  border-radius: 14px;
  padding: 1.25rem;
  margin-top: 0.5rem;
}
.day-panel h3 { margin: 0 0 1rem; font-size: 1.1rem; text-transform: capitalize; }
.empty-day { color: #aaa; font-size: 0.9rem; }

.timeline { display: flex; flex-direction: column; gap: 0.75rem; }

.timeline-block {
  display: flex;
  gap: 1rem;
  background: #fff;
  border-radius: 10px;
  padding: 0.75rem 1rem;
  border-left: 4px solid #388e3c;
  align-items: center;
  flex-wrap: wrap;
}
.timeline-time {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 48px;
  font-size: 0.82rem;
  color: #888;
}
.t-start { font-weight: 700; color: #333; font-size: 0.9rem; }
.timeline-content { flex: 1; display: flex; flex-direction: column; gap: 0.2rem; }
.timeline-service { font-weight: 600; font-size: 0.95rem; }
.timeline-client  { font-size: 0.85rem; color: #666; }
.timeline-price   { font-size: 0.85rem; color: #2e7d32; font-weight: 600; }

.timeline-actions { display: flex; gap: 0.5rem; flex-shrink: 0; }

.btn-reschedule {
  background: none;
  border: 1px solid #aaa;
  border-radius: 8px;
  padding: 0.3rem 0.7rem;
  font-size: 0.82rem;
  cursor: pointer;
}
.btn-cancel-booking {
  background: none;
  border: 1px solid #e57373;
  color: #e57373;
  border-radius: 8px;
  padding: 0.3rem 0.7rem;
  font-size: 0.82rem;
  cursor: pointer;
}

/* Modal */
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
  padding: 1.75rem;
  width: 100%;
  max-width: 440px;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  box-shadow: 0 8px 32px rgba(0,0,0,0.18);
}
.modal-card h3 { margin: 0 0 0.25rem; font-size: 1.15rem; }
.modal-card p  { margin: 0; font-size: 0.9rem; color: #555; }
.old-time      { color: #aaa !important; font-size: 0.85rem !important; }

.modal-label {
  font-size: 0.85rem;
  color: #888;
  margin-top: 0.5rem;
}
.modal-card textarea,
.modal-card input[type="date"],
.modal-card input[type="time"] {
  width: 100%;
  border: 1px solid #ccc;
  border-radius: 8px;
  padding: 0.5rem 0.75rem;
  font-family: inherit;
  font-size: 0.9rem;
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
  padding: 0.5rem 1.25rem;
  cursor: pointer;
  font-weight: 600;
}
.btn-danger:disabled { opacity: 0.5; cursor: not-allowed; }

.loading-overlay { text-align: center; color: #aaa; padding: 2rem; }
</style>