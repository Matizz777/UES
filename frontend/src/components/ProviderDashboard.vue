<template>
  <!-- Main panel -->
  <div v-if="activeTab === 'main'">
    <div class="section-header">
      <h2>Sveiki, {{ user.username }}!</h2>
      <p>Pārvaldiet savus pakalpojumus un pieejamību.</p>
    </div>

    <div class="dashboard-grid">
      <!-- Add service card -->
      <div class="card setup-card shadow">
        <div class="card-icon">➕</div>
        <h3>Pievienot pakalpojumu</h3>
        <div class="form-compact">
          <input v-model="newService.name" placeholder="Piemēram: Matu griešana" />
          <div class="input-with-unit">
            <input v-model="newService.price" type="number" placeholder="Cena" />
            <span>€</span>
          </div>
          <textarea
            v-model="newService.description"
            placeholder="Apraksts (neobligāti) — pastāsti, ko ietver šis pakalpojums..."
            class="desc-textarea"
            rows="3"
          ></textarea>
          <button class="btn-primary full-width" @click="saveService">Pievienot sarakstam</button>
        </div>
      </div>

      <!-- Availability card -->
      <div class="card availability-card shadow">
        <div class="card-icon">📅</div>
        <h3>Mana pieejamība</h3>
        <p>Iestatiet darba laikus, lai klienti varētu pieteikties.</p>
        <button class="btn-secondary-outline" @click="$emit('change-tab', 'calendar')">
          Atvērt kalendāru
        </button>
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
              <span class="service-name">{{ s.name }}</span>
              <span class="service-desc" v-if="s.description">{{ s.description }}</span>
            </div>
            <span class="service-price">{{ s.price }} €</span>
            <div class="service-actions">
              <button class="btn-edit" @click="startEdit(s)">✏️ Labot</button>
              <button class="btn-delete" @click="deleteService(s.id)">🗑️ Dzēst</button>
            </div>
          </template>

          <!-- Edit mode -->
          <template v-else>
            <div class="edit-fields">
              <input v-model="editData.name" class="edit-input" placeholder="Nosaukums" />
              <div class="input-with-unit">
                <input v-model="editData.price" type="number" class="edit-input" placeholder="Cena" />
                <span>€</span>
              </div>
              <textarea
                v-model="editData.description"
                class="edit-textarea"
                placeholder="Apraksts..."
                rows="2"
              ></textarea>
            </div>
            <div class="service-actions">
              <button class="btn-primary" @click="saveEdit(s.id)">💾 Saglabāt</button>
              <button class="btn-cancel-text" @click="editingId = null">Atcelt</button>
            </div>
          </template>

        </div>
      </div>
    </div>
  </div>

  <!-- Calendar / availability setup -->
  <div v-if="activeTab === 'calendar'" class="calendar-setup-view">
    <div class="view-header">
      <button @click="$emit('change-tab', 'main')" class="btn-back">← Atpakaļ</button>
      <h2>Mana pieejamība</h2>
    </div>
    <div class="card shadow">
      <h3>Iestatīt darba laiku</h3>
      <div class="setup-row">
        <label>No:</label>
        <input type="time" v-model="availability.start" class="modern-input" />
        <label>Līdz:</label>
        <input type="time" v-model="availability.end" class="modern-input" />
      </div>
      <button class="btn-primary" @click="saveAvailability">Saglabāt darba laiku</button>
    </div>
  </div>

  <!-- My bookings -->
  <ReservationList
    v-if="activeTab === 'my-bookings'"
    :user="user"
  />
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue';
import axios from 'axios';
import ReservationList from './ReservationList.vue';

const props = defineProps({ user: Object, activeTab: String });
defineEmits(['change-tab']);

const newService      = reactive({ name: '', price: '', description: '' });
const availability    = reactive({ start: '09:00', end: '17:00' });
const services        = ref([]);
const loadingServices = ref(false);
const editingId       = ref(null);
const editData        = reactive({ name: '', price: '', description: '' });

// ── Load services ────────────────────────────────────────────────────────────
const loadServices = async () => {
  loadingServices.value = true;
  try {
    const { data } = await axios.get('http://127.0.0.1:8080/api/services/my/', {
      params: { provider_id: props.user.id }
    });
    services.value = data;
  } catch {
    alert('Nevarēja ielādēt pakalpojumus.');
  } finally {
    loadingServices.value = false;
  }
};

onMounted(loadServices);

// ── Add service ──────────────────────────────────────────────────────────────
const saveService = async () => {
  if (!newService.name || !newService.price) {
    alert('Lūdzu, aizpildi nosaukumu un cenu!');
    return;
  }
  try {
    const res = await axios.post('http://127.0.0.1:8080/api/services/add/', {
      name:        newService.name,
      price:       newService.price,
      description: newService.description,
      provider_id: props.user.id
    });
    if (res.status === 201) {
      newService.name        = '';
      newService.price       = '';
      newService.description = '';
      await loadServices();
    }
  } catch {
    alert('Neizdevās saglabāt pakalpojumu.');
  }
};

// ── Edit service ─────────────────────────────────────────────────────────────
const startEdit = (s) => {
  editingId.value        = s.id;
  editData.name          = s.name;
  editData.price         = s.price;
  editData.description   = s.description || '';
};

const saveEdit = async (id) => {
  if (!editData.name || !editData.price) {
    alert('Lūdzu, aizpildi nosaukumu un cenu!');
    return;
  }
  try {
    await axios.put(`http://127.0.0.1:8080/api/services/edit/${id}/`, {
      name:        editData.name,
      price:       editData.price,
      description: editData.description
    });
    editingId.value = null;
    await loadServices();
  } catch {
    alert('Neizdevās saglabāt izmaiņas.');
  }
};

// ── Delete service ───────────────────────────────────────────────────────────
const deleteService = async (id) => {
  if (!confirm('Vai tiešām dzēst šo pakalpojumu?')) return;
  try {
    await axios.delete(`http://127.0.0.1:8080/api/services/delete/${id}/`);
    await loadServices();
  } catch {
    alert('Neizdevās dzēst pakalpojumu.');
  }
};

// ── Availability ─────────────────────────────────────────────────────────────
const saveAvailability = async () => {
  try {
    await axios.post('http://127.0.0.1:8080/api/availability/', availability);
    alert('Darba laiks saglabāts!');
  } catch {
    alert('Kļūda saglabājot darba laiku.');
  }
};
</script>

<style scoped>
.services-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-top: 1rem;
}

.service-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem 1rem;
  background: var(--color-background-soft, #f9f9f9);
  border-radius: 10px;
  flex-wrap: wrap;
}

.service-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.service-name {
  font-weight: 600;
}

.service-desc {
  font-size: 0.85rem;
  color: #888;
}

.service-price {
  color: #2e7d32;
  font-weight: 600;
  min-width: 60px;
}

.service-actions {
  display: flex;
  gap: 0.5rem;
}

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
  gap: 0.5rem;
}

.edit-input {
  border: 1px solid #ccc;
  border-radius: 8px;
  padding: 0.4rem 0.6rem;
  width: 100%;
}

.edit-textarea {
  border: 1px solid #ccc;
  border-radius: 8px;
  padding: 0.4rem 0.6rem;
  width: 100%;
  resize: vertical;
  font-family: inherit;
  font-size: 0.9rem;
}

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
</style>