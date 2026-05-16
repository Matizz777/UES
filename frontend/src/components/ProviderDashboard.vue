<template>
  <!-- Main panel -->
  <div v-if="activeTab === 'main'">
    <div class="section-header">
      <h2>Sveiki, {{ user.username }}!</h2>
      <p>Pārvaldiet savus pakalpojumus un pieejamību.</p>
    </div>

    <div class="dashboard-grid">
      <!-- Add service card -->
      <div class="card setup-card shadow" style="grid-column: 1 / -1;">
        <div class="card-icon">➕</div>
        <h3>Pievienot pakalpojumu</h3>
        <div class="form-compact">
          <div class="form-row-2">
            <input v-model="newService.name" placeholder="Nosaukums (piem. Matu griešana)" />
            <div class="input-with-unit">
              <input v-model="newService.price" type="number" placeholder="Cena" />
              <span>€</span>
            </div>
          </div>

          <textarea
            v-model="newService.description"
            placeholder="Apraksts (neobligāti)"
            class="desc-textarea"
            rows="2"
          ></textarea>

          <div class="form-row-2">
            <label class="form-label-group">
              <span>⏱ Ilgums (minūtes)</span>
              <input v-model="newService.duration_minutes" type="number" min="15" step="15" placeholder="60" />
            </label>
            <label class="form-label-group">
              <span>🕐 Darba laiks</span>
              <div class="time-range">
                <input type="time" v-model="newService.work_start" />
                <span>—</span>
                <input type="time" v-model="newService.work_end" />
              </div>
            </label>
          </div>

          <div class="form-label-group">
            <span>📅 Darba dienas</span>
            <div class="day-picker">
              <button
                v-for="d in DAYS"
                :key="d.value"
                :class="['day-btn', { active: newService.work_days.includes(d.value) }]"
                @click="toggleDay(newService.work_days, d.value)"
                type="button"
              >{{ d.label }}</button>
            </div>
          </div>

          <button class="btn-primary full-width" @click="saveService">Pievienot sarakstam</button>
        </div>
      </div>
    </div>

    <!-- My services list -->
    <div class="card shadow" style="margin-top: 1.5rem;">
      <div class="card-icon">🛠️</div>
      <h3>Mani pakalpojumi</h3>

      <div v-if="loadingServices" style="padding: 1rem;">Ielādē...</div>
      <div v-else-if="services.length === 0" style="padding: 1rem; color: #888;">
        Vēl nav pievienots neviens pakalpojums.
      </div>

      <div v-else class="services-list">
        <div v-for="s in services" :key="s.id" class="service-row">

          <!-- View mode -->
          <template v-if="editingId !== s.id">
            <div class="service-info">
              <div class="service-top">
                <span class="service-name">{{ s.name }}</span>
                <span class="service-price">{{ s.price }} €</span>
              </div>
              <span class="service-desc" v-if="s.description">{{ s.description }}</span>
              <div class="service-meta">
                <span>⏱ {{ s.duration_minutes }} min</span>
                <span>🕐 {{ s.work_start }} — {{ s.work_end }}</span>
                <span>📅 {{ formatWorkDays(s.work_days) }}</span>
              </div>
            </div>
            <div class="service-actions">
              <button class="btn-edit" @click="startEdit(s)">✏️ Labot</button>
              <button class="btn-delete" @click="deleteService(s.id)">🗑️ Dzēst</button>
            </div>
          </template>

          <!-- Edit mode -->
          <template v-else>
            <div class="edit-fields">
              <div class="form-row-2">
                <input v-model="editData.name" class="edit-input" placeholder="Nosaukums" />
                <div class="input-with-unit">
                  <input v-model="editData.price" type="number" class="edit-input" placeholder="Cena" />
                  <span>€</span>
                </div>
              </div>
              <textarea v-model="editData.description" class="edit-textarea" placeholder="Apraksts..." rows="2"></textarea>
              <div class="form-row-2">
                <label class="form-label-group">
                  <span>⏱ Ilgums (min)</span>
                  <input v-model="editData.duration_minutes" type="number" min="15" step="15" class="edit-input" />
                </label>
                <label class="form-label-group">
                  <span>🕐 Darba laiks</span>
                  <div class="time-range">
                    <input type="time" v-model="editData.work_start" />
                    <span>—</span>
                    <input type="time" v-model="editData.work_end" />
                  </div>
                </label>
              </div>
              <div class="form-label-group">
                <span>📅 Darba dienas</span>
                <div class="day-picker">
                  <button
                    v-for="d in DAYS"
                    :key="d.value"
                    :class="['day-btn', { active: editData.work_days.includes(d.value) }]"
                    @click="toggleDay(editData.work_days, d.value)"
                    type="button"
                  >{{ d.label }}</button>
                </div>
              </div>
            </div>
            <div class="service-actions" style="align-self: flex-end;">
              <button class="btn-primary" @click="saveEdit(s.id)">💾 Saglabāt</button>
              <button class="btn-cancel-text" @click="editingId = null">Atcelt</button>
            </div>
          </template>

        </div>
      </div>
    </div>
  </div>

  <!-- Provider calendar -->
  <ProviderCalendar
    v-if="activeTab === 'calendar'"
    :user="user"
    @back="$emit('change-tab', 'main')"
  />

  <!-- My bookings -->
  <div v-if="activeTab === 'my-bookings'">
    <div class="view-header">
      <button class="btn-back" @click="$emit('change-tab', 'main')">← Atpakaļ</button>
    </div>
    <ReservationList :user="user" />
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue';
import axios from 'axios';
import ReservationList from './ReservationList.vue';
import ProviderCalendar from './ProviderCalendar.vue';

const props = defineProps({ user: Object, activeTab: String });
defineEmits(['change-tab']);

const DAYS = [
  { value: '1', label: 'Pr' },
  { value: '2', label: 'Ot' },
  { value: '3', label: 'Tr' },
  { value: '4', label: 'Ce' },
  { value: '5', label: 'Pk' },
  { value: '6', label: 'Se' },
  { value: '7', label: 'Sv' },
];

const DAY_SHORT = { '1':'Pr','2':'Ot','3':'Tr','4':'Ce','5':'Pk','6':'Se','7':'Sv' };

// FIX: handle both array and string formats safely
const formatWorkDays = (work_days) => {
  if (!work_days) return '';
  const days = Array.isArray(work_days)
    ? work_days
    : String(work_days).split(',');
  return days.map(d => DAY_SHORT[d.trim()] || d).join(', ');
};

const toggleDay = (arr, value) => {
  const idx = arr.indexOf(value);
  if (idx === -1) arr.push(value);
  else arr.splice(idx, 1);
  arr.sort();
};

const blankService = () => ({
  name: '', price: '', description: '',
  duration_minutes: 60,
  work_days: ['1','2','3','4','5'],
  work_start: '09:00', work_end: '17:00',
});

const newService      = reactive(blankService());
const services        = ref([]);
const loadingServices = ref(false);
const editingId       = ref(null);
const editData        = reactive(blankService());

const loadServices = async () => {
  loadingServices.value = true;
  try {
    const { data } = await axios.get('http://127.0.0.1:8080/api/services/my/', {
      params: { provider_id: props.user.id }
    });
    // Always normalize work_days to array
    services.value = data.map(s => ({
      ...s,
      work_days: Array.isArray(s.work_days)
        ? s.work_days
        : String(s.work_days || '1,2,3,4,5').split(',').map(x => x.trim())
    }));
  } catch {
    alert('Nevarēja ielādēt pakalpojumus.');
  } finally {
    loadingServices.value = false;
  }
};

onMounted(loadServices);

const saveService = async () => {
  if (!newService.name || !newService.price) {
    alert('Lūdzu, aizpildi nosaukumu un cenu!');
    return;
  }
  if (newService.work_days.length === 0) {
    alert('Izvēlies vismaz vienu darba dienu!');
    return;
  }
  try {
    const res = await axios.post('http://127.0.0.1:8080/api/services/add/', {
      ...newService,
      work_days: newService.work_days.join(','),
      provider_id: props.user.id
    });
    if (res.status === 201) {
      Object.assign(newService, blankService());
      await loadServices();
    }
  } catch {
    alert('Neizdevās saglabāt pakalpojumu.');
  }
};

const startEdit = (s) => {
  editingId.value = s.id;
  Object.assign(editData, {
    name:             s.name,
    price:            s.price,
    description:      s.description || '',
    duration_minutes: s.duration_minutes || 60,
    work_days:        Array.isArray(s.work_days)
                        ? [...s.work_days]
                        : String(s.work_days || '1,2,3,4,5').split(',').map(x => x.trim()),
    work_start:       s.work_start || '09:00',
    work_end:         s.work_end   || '17:00',
  });
};

const saveEdit = async (id) => {
  if (!editData.name || !editData.price) {
    alert('Lūdzu, aizpildi nosaukumu un cenu!');
    return;
  }
  try {
    await axios.put(`http://127.0.0.1:8080/api/services/edit/${id}/`, {
      ...editData,
      work_days: editData.work_days.join(','),
    });
    editingId.value = null;
    await loadServices();
  } catch {
    alert('Neizdevās saglabāt izmaiņas.');
  }
};

const deleteService = async (id) => {
  if (!confirm('Vai tiešām dzēst šo pakalpojumu?')) return;
  try {
    await axios.delete(`http://127.0.0.1:8080/api/services/delete/${id}/`);
    await loadServices();
  } catch {
    alert('Neizdevās dzēst pakalpojumu.');
  }
};
</script>

<style scoped>
.form-row-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}
.form-label-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  font-size: 0.88rem;
  color: #666;
}
.time-range {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}
.time-range input {
  flex: 1;
  border: 1px solid #ccc;
  border-radius: 8px;
  padding: 0.4rem 0.5rem;
}
.day-picker {
  display: flex;
  gap: 0.4rem;
  flex-wrap: wrap;
}
.day-btn {
  padding: 0.3rem 0.6rem;
  border: 1px solid #ccc;
  border-radius: 8px;
  background: none;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.15s;
}
.day-btn.active {
  background: #388e3c;
  color: #fff;
  border-color: #388e3c;
}
.services-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-top: 1rem;
}
.service-row {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem;
  background: var(--color-background-soft, #f9f9f9);
  border-radius: 12px;
  flex-wrap: wrap;
}
.service-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}
.service-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.service-name { font-weight: 600; font-size: 1rem; }
.service-price { color: #2e7d32; font-weight: 700; }
.service-desc  { font-size: 0.85rem; color: #888; }
.service-meta {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  font-size: 0.82rem;
  color: #aaa;
  margin-top: 0.2rem;
}
.service-actions { display: flex; gap: 0.5rem; flex-shrink: 0; }
.btn-edit {
  background: none;
  border: 1px solid #aaa;
  border-radius: 8px;
  padding: 0.3rem 0.7rem;
  cursor: pointer;
}
.btn-delete {
  background: none;
  border: 1px solid #e57373;
  color: #e57373;
  border-radius: 8px;
  padding: 0.3rem 0.7rem;
  cursor: pointer;
}
.edit-fields {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}
.edit-input {
  border: 1px solid #ccc;
  border-radius: 8px;
  padding: 0.4rem 0.6rem;
  width: 100%;
  box-sizing: border-box;
}
.edit-textarea,
.desc-textarea {
  width: 100%;
  border: 1px solid #ccc;
  border-radius: 8px;
  padding: 0.5rem 0.75rem;
  font-family: inherit;
  font-size: 0.9rem;
  resize: vertical;
  box-sizing: border-box;
}
.view-header {
  margin-bottom: 1rem;
}
</style>