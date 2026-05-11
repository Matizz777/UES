<template>
  <div class="booking-wizard-modern shadow">
    <div class="wizard-top">
      <button class="btn-back" @click="$emit('cancel')">← Atpakaļ</button>
      <p>Pakalpojums: <strong>{{ serviceName }}</strong> pie <strong>{{ provider?.username }}</strong></p>
    </div>

    <nav class="wizard-steps">
      <div :class="['step-node', { active: step === 2, done: step > 2 }]">Datums</div>
      <div :class="['step-node', { active: step === 3, done: step > 3 }]">Laiks</div>
    </nav>

    <div class="wizard-body">
      <!-- Step 2: Date picker -->
      <div v-if="step === 2" class="calendar-step">
        <h3>Izvēlieties datumu</h3>
        <div class="calendar-wrapper">
          <div class="calendar-header">
            <button @click="changeMonth(-1)">‹</button>
            <span>{{ currentMonthName }} {{ currentYear }}</span>
            <button @click="changeMonth(1)">›</button>
          </div>
          <div class="calendar-grid">
            <div v-for="day in ['Pr','Ot','Tr','Ce','Pk','Se','Sv']" :key="day" class="day-name">{{ day }}</div>
            <div v-for="blank in firstDayOffset" :key="'b'+blank" class="day empty"></div>
            <div
              v-for="date in daysInMonth"
              :key="date"
              class="day-cell"
              :class="{ selected: isSelected(date), busy: isDateBusy(date), past: isPast(date) }"
              @click="selectDate(date)"
            >{{ date }}</div>
          </div>
        </div>
        <div class="wizard-footer">
          <button class="btn-text" @click="$emit('cancel')">Atcelt</button>
          <button class="btn-primary" @click="loadTimes" :disabled="!selectedDate">Tālāk</button>
        </div>
      </div>

      <!-- Step 3: Time slots -->
      <div v-if="step === 3" class="time-selection-step">
        <h3>Pieejamie laiki: {{ selectedDate }}</h3>
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
        <h2>Rezervācija apstiprināta</h2>
        <button class="btn-primary" @click="$emit('done')">Pabeigt</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import axios from 'axios';

const props = defineProps({ provider: Object, serviceName: String });
defineEmits(['done', 'cancel']);

const step          = ref(2);
const selectedDate  = ref('');
const selectedTime  = ref('');
const availableTimes = ref([]);
const busyDates     = ref([]);
const viewDate      = ref(new Date());

// ── Calendar computeds ──────────────────────────────────────────────────────
const currentMonthName = computed(() =>
  viewDate.value.toLocaleString('lv-LV', { month: 'long' })
);
const currentYear  = computed(() => viewDate.value.getFullYear());
const daysInMonth  = computed(() =>
  new Date(viewDate.value.getFullYear(), viewDate.value.getMonth() + 1, 0).getDate()
);
const firstDayOffset = computed(() => {
  const d = new Date(viewDate.value.getFullYear(), viewDate.value.getMonth(), 1).getDay();
  return d === 0 ? 6 : d - 1;
});

const changeMonth  = (offset) => {
  viewDate.value = new Date(viewDate.value.getFullYear(), viewDate.value.getMonth() + offset, 1);
};

const selectDate = (day) => {
  if (isPast(day)) return;
  const y = viewDate.value.getFullYear();
  const m = String(viewDate.value.getMonth() + 1).padStart(2, '0');
  const d = String(day).padStart(2, '0');
  selectedDate.value = `${y}-${m}-${d}`;
};

const isSelected = (day) => {
  const y = viewDate.value.getFullYear();
  const m = String(viewDate.value.getMonth() + 1).padStart(2, '0');
  const d = String(day).padStart(2, '0');
  return selectedDate.value === `${y}-${m}-${d}`;
};

const isDateBusy = (day) => {
  const y = viewDate.value.getFullYear();
  const m = String(viewDate.value.getMonth() + 1).padStart(2, '0');
  const d = String(day).padStart(2, '0');
  return busyDates.value.includes(`${y}-${m}-${d}`);
};

const isPast = (day) => {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return new Date(currentYear.value, viewDate.value.getMonth(), day) < today;
};

// ── API calls ───────────────────────────────────────────────────────────────
const ALL_SLOTS = ['09:00','10:00','11:00','12:00','13:00','14:00','15:00','16:00'];

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

const confirmBooking = async () => {
  try {
    await axios.post('http://127.0.0.1:8080/api/book/', {
      provider_id:  props.provider.id,
      service_name: props.serviceName,
      res_date:     selectedDate.value,
      res_time:     selectedTime.value
    });
    step.value = 4;
  } catch (err) {
    alert('Rezervācija neizdevās: ' + (err.response?.data?.error ?? ''));
  }
};
</script>
