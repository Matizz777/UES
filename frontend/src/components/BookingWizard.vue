<template>
  <div class="booking-wizard-modern shadow">
    <div class="wizard-top">
      <button class="btn-back" @click="$emit('cancel')">← Atpakaļ</button>
      <p>Rezervācija pie <strong>{{ provider?.username }}</strong></p>
    </div>

    <nav class="wizard-steps">
      <div :class="['step-node', { active: step === 1, done: step > 1 }]">Pakalpojums</div>
      <div :class="['step-node', { active: step === 2, done: step > 2 }]">Datums</div>
      <div :class="['step-node', { active: step === 3, done: step > 3 }]">Laiks</div>
    </nav>

    <div class="wizard-body">

      <!-- Step 1: Service details -->
      <div v-if="step === 1" class="service-detail-step">
        <div class="service-detail-card">
          <div class="service-detail-header">
            <h3>{{ service.name }}</h3>
            <span class="price-badge">{{ service.price }} €</span>
          </div>
          <div class="service-detail-body">
            <div class="detail-row">
              <span class="detail-label">🏢 Speciālists</span>
              <span class="detail-value">{{ provider.username }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">🏷️ Nozare</span>
              <span class="detail-value">{{ provider.industry || 'Nav norādīta' }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">💶 Cena</span>
              <span class="detail-value price-highlight">{{ service.price }} €</span>
            </div>
            <div v-if="service.description" class="detail-row column">
              <span class="detail-label">📋 Pakalpojuma apraksts</span>
              <span class="detail-value desc-text">{{ service.description }}</span>
            </div>
            <div v-if="provider.description" class="detail-row column">
              <span class="detail-label">👤 Par speciālistu</span>
              <span class="detail-value desc-text">{{ provider.description }}</span>
            </div>
          </div>
          <div class="confirm-notice">
            ℹ️ Cena tiek fiksēta rezervācijas brīdī. Turpmākas cenas izmaiņas jūs neskar.
          </div>
        </div>
        <div class="wizard-footer">
          <button class="btn-text" @click="$emit('cancel')">Atcelt</button>
          <button class="btn-primary" @click="goToCalendar">Turpināt →</button>
        </div>
      </div>

      <!-- Step 2: Date picker -->
      <div v-if="step === 2" class="calendar-step">
        <h3>Izvēlieties datumu</h3>

        <div v-if="loadingDates" style="text-align:center; padding: 2rem; color: #888;">
          Ielādē pieejamos datumus...
        </div>

        <div class="calendar-wrapper" v-else>
          <div class="calendar-header">
            <button @click="changeMonth(-1)">‹</button>
            <span>{{ currentMonthName }} {{ currentYear }}</span>
            <button @click="changeMonth(1)">›</button>
          </div>
          <div class="calendar-legend">
            <span class="legend-item"><span class="legend-dot green"></span> Pieejams</span>
            <span class="legend-item"><span class="legend-dot grey"></span> Nav brīvu laiku</span>
          </div>
          <div class="calendar-grid">
            <div v-for="day in ['Pr','Ot','Tr','Ce','Pk','Se','Sv']" :key="day" class="day-name">{{ day }}</div>
            <div v-for="blank in firstDayOffset" :key="'b'+blank" class="day empty"></div>
            <div
              v-for="date in daysInMonth"
              :key="date"
              class="day-cell"
              :class="dayClass(date)"
              @click="selectDate(date)"
            >{{ date }}</div>
          </div>
        </div>

        <div class="wizard-footer">
          <button class="btn-secondary" @click="step = 1">Atpakaļ</button>
          <button class="btn-primary" @click="loadTimes" :disabled="!selectedDate">Tālāk</button>
        </div>
      </div>

      <!-- Step 3: Time slots -->
      <div v-if="step === 3" class="time-selection-step">
        <h3>Pieejamie laiki: {{ selectedDate }}</h3>

        <div class="booking-summary">
          <div class="summary-row"><span>Pakalpojums:</span><strong>{{ service.name }}</strong></div>
          <div class="summary-row"><span>Speciālists:</span><strong>{{ provider.username }}</strong></div>
          <div class="summary-row"><span>Datums:</span><strong>{{ selectedDate }}</strong></div>
          <div class="summary-row"><span>Cena:</span><strong class="price-highlight">{{ service.price }} €</strong></div>
        </div>

        <div class="time-grid" v-if="availableTimes.length > 0">
          <button
            v-for="t in availableTimes"
            :key="t"
            :class="['time-slot-btn', { selected: selectedTime === t }]"
            @click="selectedTime = t"
          >{{ t }}</button>
        </div>
        <div v-else class="empty-state">
          <p>Diemžēl šajā dienā visi laiki ir aizņemti.</p>
        </div>
        <div class="wizard-footer">
          <button class="btn-secondary" @click="step = 2">Atpakaļ</button>
          <button class="btn-confirm" @click="confirmBooking" :disabled="!selectedTime">
            Apstiprināt rezervāciju
          </button>
        </div>
      </div>

      <!-- Step 4: Success -->
      <div v-if="step === 4" class="success-wrap">
        <div class="check-animation">✅</div>
        <h2>Rezervācija apstiprināta!</h2>
        <div class="success-summary">
          <div class="summary-row"><span>Pakalpojums:</span><strong>{{ service.name }}</strong></div>
          <div class="summary-row"><span>Speciālists:</span><strong>{{ provider.username }}</strong></div>
          <div class="summary-row"><span>Datums:</span><strong>{{ selectedDate }}</strong></div>
          <div class="summary-row"><span>Laiks:</span><strong>{{ selectedTime }}</strong></div>
          <div class="summary-row"><span>Apmaksājamā cena:</span><strong class="price-highlight">{{ service.price }} €</strong></div>
        </div>
        <button class="btn-primary" @click="$emit('done')">Pabeigt</button>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import axios from 'axios';

const props = defineProps({
  provider: Object,  // { id, username, industry, description }
  service:  Object,  // { id, name, price, description }
});
defineEmits(['done', 'cancel']);

const step            = ref(1);
const selectedDate    = ref('');
const selectedTime    = ref('');
const availableTimes  = ref([]);
const viewDate        = ref(new Date());
const loadingDates    = ref(false);

// dateAvailability: { 'YYYY-MM-DD': true/false }  true = has free slots
const dateAvailability = ref({});

const ALL_SLOTS = [
  '09:00','09:30','10:00','10:30','11:00','11:30',
  '12:00','12:30','13:00','13:30','14:00','14:30',
  '15:00','15:30','16:00','16:30'
];

// ── Calendar computeds ───────────────────────────────────────────────────────
const currentMonthName = computed(() =>
  viewDate.value.toLocaleString('lv-LV', { month: 'long' })
);
const currentYear = computed(() => viewDate.value.getFullYear());
const daysInMonth = computed(() =>
  new Date(viewDate.value.getFullYear(), viewDate.value.getMonth() + 1, 0).getDate()
);
const firstDayOffset = computed(() => {
  const d = new Date(viewDate.value.getFullYear(), viewDate.value.getMonth(), 1).getDay();
  return d === 0 ? 6 : d - 1;
});

const dateStr = (day) => {
  const y = viewDate.value.getFullYear();
  const m = String(viewDate.value.getMonth() + 1).padStart(2, '0');
  const d = String(day).padStart(2, '0');
  return `${y}-${m}-${d}`;
};

const isPast = (day) => {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return new Date(currentYear.value, viewDate.value.getMonth(), day) < today;
};

const isSelected = (day) => selectedDate.value === dateStr(day);

const hasAvailability = (day) => {
  if (isPast(day)) return false;
  const key = dateStr(day);
  // if we haven't loaded this date yet, assume available
  if (!(key in dateAvailability.value)) return true;
  return dateAvailability.value[key];
};

const dayClass = (day) => ({
  selected:      isSelected(day),
  past:          isPast(day),
  'day-available': !isPast(day) && hasAvailability(day),
  'day-full':    !isPast(day) && !hasAvailability(day),
});

const selectDate = (day) => {
  if (isPast(day) || !hasAvailability(day)) return;
  selectedDate.value = dateStr(day);
};

// ── Load availability for whole month ────────────────────────────────────────
const loadMonthAvailability = async () => {
  loadingDates.value = true;
  const y = viewDate.value.getFullYear();
  const m = String(viewDate.value.getMonth() + 1).padStart(2, '0');
  const days = new Date(y, viewDate.value.getMonth() + 1, 0).getDate();

  const results = {};
  // fetch all days in parallel
  await Promise.all(
    Array.from({ length: days }, (_, i) => i + 1).map(async (day) => {
      const d = String(day).padStart(2, '0');
      const key = `${y}-${m}-${d}`;
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      if (new Date(y, viewDate.value.getMonth(), day) < today) {
        results[key] = false;
        return;
      }
      try {
        const { data } = await axios.get('http://127.0.0.1:8080/api/occupied-times/', {
          params: { provider_id: props.provider.id, date: key }
        });
        results[key] = data.length < ALL_SLOTS.length; // true if at least one slot free
      } catch {
        results[key] = true; // assume available on error
      }
    })
  );

  dateAvailability.value = { ...dateAvailability.value, ...results };
  loadingDates.value = false;
};

const changeMonth = async (offset) => {
  viewDate.value = new Date(viewDate.value.getFullYear(), viewDate.value.getMonth() + offset, 1);
  selectedDate.value = '';
  await loadMonthAvailability();
};

const goToCalendar = async () => {
  step.value = 2;
  await loadMonthAvailability();
};

// ── Load times for selected date ─────────────────────────────────────────────
const loadTimes = async () => {
  try {
    const { data } = await axios.get('http://127.0.0.1:8080/api/occupied-times/', {
      params: { provider_id: props.provider.id, date: selectedDate.value }
    });
    availableTimes.value = ALL_SLOTS.filter(t => !data.includes(t));
    selectedTime.value = '';
    step.value = 3;
  } catch {
    alert('Kļūda ielādējot laikus');
  }
};

// ── Confirm booking ──────────────────────────────────────────────────────────
const confirmBooking = async () => {
  try {
    await axios.post('http://127.0.0.1:8080/api/book/', {
      provider_id:  props.provider.id,
      service_id:   props.service.id,
      service_name: props.service.name,
      booked_price: props.service.price,
      res_date:     selectedDate.value,
      res_time:     selectedTime.value
    });
    step.value = 4;
  } catch (err) {
    alert('Rezervācija neizdevās: ' + (err.response?.data?.error ?? ''));
  }
};
</script>

<style scoped>
/* ── Calendar day colours ── */
.day-cell.day-available {
  background: #e8f5e9;
  color: #2e7d32;
  font-weight: 600;
  cursor: pointer;
  border-radius: 8px;
}

.day-cell.day-available:hover {
  background: #c8e6c9;
}

.day-cell.day-full {
  background: #f5f5f5;
  color: #bbb;
  cursor: not-allowed;
  border-radius: 8px;
}

.day-cell.past {
  color: #ccc;
  cursor: not-allowed;
}

.day-cell.selected {
  background: #388e3c !important;
  color: #fff !important;
  border-radius: 8px;
}

/* ── Legend ── */
.calendar-legend {
  display: flex;
  gap: 1rem;
  margin-bottom: 0.75rem;
  font-size: 0.85rem;
  color: #666;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  display: inline-block;
}

.legend-dot.green { background: #c8e6c9; border: 1px solid #2e7d32; }
.legend-dot.grey  { background: #f5f5f5; border: 1px solid #bbb; }

/* ── Service detail card ── */
.service-detail-card {
  background: var(--color-background-soft, #f9f9f9);
  border-radius: 14px;
  padding: 1.5rem;
  margin-bottom: 1rem;
}

.service-detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.25rem;
}

.service-detail-header h3 {
  font-size: 1.3rem;
  font-weight: 700;
  margin: 0;
}

.price-badge {
  background: #e8f5e9;
  color: #2e7d32;
  font-weight: 700;
  font-size: 1.1rem;
  padding: 0.3rem 0.8rem;
  border-radius: 20px;
}

.service-detail-body {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.detail-row.column {
  flex-direction: column;
  gap: 0.25rem;
}

.detail-label {
  color: #888;
  font-size: 0.9rem;
  min-width: 160px;
}

.detail-value {
  font-weight: 500;
  text-align: right;
}

.detail-row.column .detail-value {
  text-align: left;
}

.desc-text {
  color: #555;
  font-size: 0.95rem;
  line-height: 1.5;
  font-weight: 400 !important;
}

.price-highlight {
  color: #2e7d32;
  font-weight: 700;
}

.confirm-notice {
  margin-top: 1.25rem;
  padding: 0.75rem 1rem;
  background: #fff8e1;
  border-left: 3px solid #f9a825;
  border-radius: 8px;
  font-size: 0.88rem;
  color: #666;
}

/* ── Booking summary ── */
.booking-summary {
  background: var(--color-background-soft, #f9f9f9);
  border-radius: 10px;
  padding: 1rem 1.25rem;
  margin-bottom: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.95rem;
}

.summary-row span { color: #888; }

.success-summary {
  background: var(--color-background-soft, #f9f9f9);
  border-radius: 10px;
  padding: 1rem 1.25rem;
  margin: 1rem 0 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  width: 100%;
  max-width: 360px;
}
</style>