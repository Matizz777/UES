<template>
  <!-- Main panel -->
  <div v-if="activeTab === 'main'">
    <div class="section-header">
      <h2>Sveiki, {{ user.username }}!</h2>
      <p>Pārvaldiet savus pakalpojumus un pieejamību.</p>
    </div>

    <div class="dashboard-grid">
      <div class="card setup-card shadow">
        <div class="card-icon">➕</div>
        <h3>Pievienot pakalpojumu</h3>
        <div class="form-compact">
          <input v-model="newService.name" placeholder="Piemēram: Matu griešana" />
          <div class="input-with-unit">
            <input v-model="newService.price" type="number" placeholder="Cena" />
            <span>€</span>
          </div>
          <button class="btn-primary full-width" @click="saveService">Pievienot sarakstam</button>
        </div>
      </div>

      <div class="card availability-card shadow">
        <div class="card-icon">📅</div>
        <h3>Mana pieejamība</h3>
        <p>Iestatiet darba laikus, lai klienti varētu pieteikties.</p>
        <button class="btn-secondary-outline" @click="$emit('change-tab', 'calendar')">
          Atvērt kalendāru
        </button>
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

  <!-- My bookings (clients who booked me) -->
  <ReservationList
    v-if="activeTab === 'my-bookings'"
    :user="user"
  />
</template>

<script setup>
import { reactive } from 'vue';
import axios from 'axios';
import ReservationList from './ReservationList.vue';

const props = defineProps({ user: Object, activeTab: String });
defineEmits(['change-tab']);

const newService = reactive({ name: '', price: '' });
const availability = reactive({ start: '09:00', end: '17:00' });

const saveService = async () => {
  if (!newService.name || !newService.price) {
    alert('Lūdzu, aizpildi visus laukus!');
    return;
  }
  try {
    const res = await axios.post('http://127.0.0.1:8080/api/services/add/', {
      name: newService.name,
      price: newService.price,
      provider_id: props.user.id
    });
    if (res.status === 201) {
      alert('Pakalpojums pievienots!');
      newService.name  = '';
      newService.price = '';
    }
  } catch {
    alert('Neizdevās saglabāt pakalpojumu.');
  }
};

const saveAvailability = async () => {
  try {
    await axios.post('http://127.0.0.1:8080/api/availability/', availability);
    alert('Darba laiks saglabāts!');
  } catch {
    alert('Kļūda saglabājot darba laiku.');
  }
};
</script>
