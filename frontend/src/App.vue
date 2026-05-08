<template>
  <nav class="navbar">
    <div class="logo">
      <span class="logo-icon">☁️</span> UES
    </div>

    <div class="auth-buttons">
      <template v-if="!user">
        <button class="btn-login">Pieslēgties</button>
        <button class="btn-register" @click="showRegister = true">Reģistrēties</button>
      </template>

      <template v-else>
        <div class="user-menu">
          <div class="user-info">
            <div class="avatar">{{ user.username[0].toUpperCase() }}</div>
            <div class="user-details">
              <span class="welcome-msg"> {{ user.username }}</span>
              <span class="user-role">
                {{ user.roles === 2 ? 'Pakalpojuma sniedzējs' : 'Klients' }}
              </span>
            </div>
          </div>
          <button class="btn-logout" @click="handleLogout" title="Iziet">
            <span class="logout-icon">→</span>
          </button>
        </div>
      </template>
    </div>
  </nav>

  <div class="apraksts" v-if="!user && !showRegister">
    <main class="hero">
      <h1>Universālā e-pierakstu sistēma</h1>
      <p>Pieraksts pāris klikšķu attālumā</p>
    </main>
  </div>

  <div class="form-container" v-else-if="!user && showRegister">
    <div class="register-card">
      <h2>Izveidot kontu</h2>
      <input type="text" v-model="regData.username" placeholder="Lietotājvārds" />
      <input type="email" v-model="regData.email" placeholder="E-pasts" />
      <input type="password" v-model="regData.password" placeholder="Parole" />
      
      <select v-model="regData.roles" class="role-select">
        <option value="3">Esmu klients</option>
        <option value="2">Esmu pakalpojuma sniedzējs</option>
      </select>

      <div v-if="regData.roles == '2'" class="provider-extra-fields">
        <select v-model="regData.industry" class="role-select">
          <option value="">Izvēlies nozari</option>
          <option value="Skaistumkopšana">Skaistumkopšana</option>
          <option value="Medicīna">Medicīna</option>
          <option value="IT pakalpojumi">IT pakalpojumi</option>
          <option value="Sports">Sports un Fitness</option>
        </select>
        <textarea v-model="regData.description" placeholder="Pastāsti par saviem pakalpojumiem..." class="desc-textarea"></textarea>
      </div>

      <button class="btn-register" @click="submitRegistration">Sākt darbu</button>
      <p @click="showRegister = false" class="back-link">Atpakaļ</p>
    </div>
  </div>

<div class="dashboard-container" v-else>
  <header class="dashboard-nav">
    <div class="nav-tabs">
      <button :class="{ active: activeTab === 'main' }" @click="activeTab = 'main'; showBooking = false">
        {{ user.roles === 2 ? '🏢 Speciālista panelis' : '🔍 Atrast speciālistu' }}
      </button>
      <button :class="{ active: activeTab === 'my-bookings' }" @click="fetchReservations">
        {{ user.roles === 2 ? '📅 Klientu pieraksti' : '📋 Mani pieraksti' }}
      </button>
    </div>
  </header>

<main class="dashboard-content">
  <div v-if="user.roles === 2">
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
          <button class="btn-secondary-outline" @click="activeTab = 'calendar'">Atvērt kalendāru</button>
        </div>
      </div>
    </div>

    <div v-if="activeTab === 'calendar'" class="calendar-setup-view">
      <div class="view-header">
        <button @click="activeTab = 'main'" class="btn-back">← Atpakaļ</button>
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
  </div>

  <div v-else-if="user.roles === 3">
    <div v-if="!showBooking && activeTab === 'main'" class="catalog-view">
      <div class="catalog-filter-wrapper">
        <div class="search-main">
          <input v-model="searchQuery" placeholder="Meklēt speciālistu..." @input="fetchProviders" />
          <span class="search-icon">🔍</span>
        </div>
        <select v-model="selectedIndustry" @change="fetchProviders" class="industry-select">
          <option value="">Visas nozares</option>
          <option value="Medicīna">Medicīna</option>
          <option value="IT">IT pakalpojumi</option> 
          <option value="Skaistumkopšana">Skaistumkopšana</option>
        </select>
      </div>

      <div class="provider-grid">
        <div v-for="p in providers" :key="p.id" class="provider-card-modern">
          <div class="provider-header">
            <div class="avatar-circle">{{ p.username ? p.username[0].toUpperCase() : '?' }}</div>
            <div class="provider-title">
              <h3>{{ p.username }}</h3>
              <span class="badge-industry">{{ p.industry }}</span>
            </div>
          </div>
          <p class="provider-desc">{{ p.description }}</p>
          <button class="btn-book" @click="openProviderProfile(p)">Skatīt pakalpojumus</button>
        </div>
      </div>
    </div>

    <div v-if="viewingProvider" class="provider-profile-overlay">
      <div class="provider-profile-content">
        <button @click="viewingProvider = null" class="close-btn">X</button>
        <h2>{{ viewingProvider.username }} pakalpojumi</h2>
        <div class="services-vertical-list">
          <div v-for="s in viewingProvider.services" :key="s.id" class="service-row" @click="startBookingFlow(viewingProvider, s)">
            <div class="s-info">
              <span class="s-name">{{ s.name }}</span>
              <span class="s-desc">{{ s.description }}</span>
            </div>
            <div class="s-action">
              <span class="s-price">{{ s.price }}€</span>
              <button class="btn-select">Izvēlēties</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showBooking" class="booking-wizard-modern shadow">
      <div class="wizard-top">
        <button class="btn-back" @click="showBooking = false">← Atpakaļ</button>
        <p>Pakalpojums: <strong>{{ bookingData.service }}</strong> pie <strong>{{ selectedProvider?.username }}</strong></p>
      </div>
      
      <nav class="wizard-steps">
        <div :class="['step-node', { active: step === 2, done: step > 2 }]">Datums</div>
        <div :class="['step-node', { active: step === 3, done: step > 3 }]">Laiks</div>
      </nav>

      <div class="wizard-body">
        <div v-if="step === 2" class="calendar-step">
          <h3>Izvēlieties datumu</h3>
          <div class="calendar-wrapper">
            <div class="calendar-header">
              <button @click="changeMonth(-1)">‹</button>
              <span>{{ currentMonthName }} {{ currentYear }}</span>
              <button @click="changeMonth(1)">›</button>
            </div>
            <div class="calendar-grid">
              <div v-for="day in ['Pr', 'Ot', 'Tr', 'Ce', 'Pk', 'Se', 'Sv']" :key="day" class="day-name">{{ day }}</div>
              <div v-for="blank in firstDayOffset" :key="'blank'+blank" class="day empty"></div>
              <div 
                v-for="date in daysInMonth" 
                :key="date" 
                class="day-cell"
                :class="{ 'selected': isSelected(date), 'busy': isDateBusy(date), 'past': isPast(date) }"
                @click="selectDate(date)"
              >
                {{ date }}
              </div>
            </div>
          </div>
          <div class="wizard-footer">
            <button class="btn-text" @click="showBooking = false">Atcelt</button>
            <button class="btn-primary" @click="checkAvailableTimes" :disabled="!bookingData?.date">Tālāk</button>
          </div>
        </div>

            <div v-if="step === 3" class="time-selection-step">
              <h3>Pieejamie laiki: {{ bookingData.date }}</h3>
              
              <div class="time-grid" v-if="availableTimes.length > 0">
                <button 
                  v-for="t in availableTimes" 
                  :key="t" 
                  :class="['time-slot-btn', { selected: bookingData.time === t }]"
                  @click="bookingData.time = t"
                >
                  {{ t }}
                </button>
              </div>

              <div v-else class="empty-state">
                <p>Diemžēl šajā dienā visi laiki ir aizņemti.</p>
              </div>

              <div class="wizard-footer">
                <button class="btn-secondary" @click="step = 2">Atpakaļ</button>
                <button 
                  class="btn-confirm" 
                  @click="confirmBooking" 
                  :disabled="!bookingData.time"
                >
                  Apstiprināt rezervāciju
                </button>
              </div>
            </div>

        <div v-if="step === 4" class="success-wrap">
           <div class="check-animation">✅</div>
           <h2>Rezervācija apstiprināta</h2>
           <button class="btn-primary" @click="finishBooking">Pabeigt</button>
        </div>
      </div>
    </div>
  </div>

<div v-if="activeTab === 'my-bookings'" class="reservations-view fade-in">
      <div class="section-header">
        <h2>{{ user.roles === 2 ? 'Klientu pieteikumi' : 'Mani plānotie pieraksti' }}</h2>
      </div>
      
      <div v-if="userReservations.length === 0" class="empty-state">
        <p>Šeit vēl nekas neparādās.</p>
      </div>

      <div class="res-list-container" v-else>
        <div v-for="res in userReservations" :key="res.id" class="res-card-modern">
          <div class="res-main-info">
            <div class="res-date-box">
              <span class="day">{{ res.date.split('-')[2] }}</span>
              <span class="month">{{ res.date.split('-')[1] }}</span>
            </div>
            <div class="res-details">
              <h4>{{ res.service }}</h4>
              <p>🕙 {{ res.time && res.time !== 'Nav laika' ? res.time.slice(0, 5) : 'Laiks nav norādīts' }} • {{ user.roles === 2 ? 'Klients: ' + res.client_name : 'Pie speciālista' }}</p>
            </div>
          </div>
          <button class="btn-cancel-text" @click="cancelBooking(res.id)">Atcelt pierakstu</button>
      </div>
    </div>
  </div>
</main>
</div>

  <div class="clouds-container">
    <div class="cloud cloud-solid"></div>
    <div class="cloud cloud-transparent"></div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import './assets/style.css';
import axios from 'axios';

const showRegister = ref(false);
const user = ref(null); 

const regData = reactive({
  username: '',
  email: '',
  password: '',
  roles: '3',
  industry: '',     // Jauns lauks
  description: ''   // Jauns lauks
});

const fetchProviders = async () => {
  try {
    const response = await axios.get('http://127.0.0.1:8080/api/catalog/', {
      params: {
        search: searchQuery.value,
        industry: selectedIndustry.value
      }
    });

    // ŠEIT IR PROBLĒMA - mēs izmetam ārā services datus!
    providers.value = response.data.map(p => ({
      id: p.id,
      username: p.username || p.name || 'Nezināms',
      industry: p.industry || 'Nav norādīta',
      description: p.description || p.desc || 'Nav apraksta.',
      services: p.services || []
    }));

    console.log("Ielādētie sniedzēji:", providers.value);
  } catch (error) {
    console.error("Kļūda ielādējot katalogu:", error);
  }
};

// Lai katalogs ielādētos uzreiz, kad klients atver lapu:
onMounted(() => {
  const savedUser = localStorage.getItem('user_auth');
  if (savedUser) {
    const parsedUser = JSON.parse(savedUser);
    user.value = parsedUser;
    axios.defaults.headers.common['Authorization'] = `Bearer ${parsedUser.token}`;
    
    // Ja ielogotais lietotājs ir klients, ielādējam katalogu
    if (user.value.roles === 3 || user.value.roles === '3') {
      fetchProviders();
    }
  }
});

const submitRegistration = async () => {
  try {
    // 1. Sagatavojam datus (kopējam regData)
    const payload = { ...regData };

    // 2. Ja reģistrējas klients, pieliekam trūkstošās vērtības PIRMS sūtīšanas
    // Izmantojam == , lai noķertu gan skaitli 3, gan tekstu '3'
    if (payload.roles == 3) {
      payload.industry = "Klients";
      payload.description = "Lietotāja profils";
    }

    // 3. Sūtām TIKAI payload (URL, dati)
    const response = await axios.post('http://127.0.0.1:8080/api/register/', payload);
    
    // 4. Apstrādājam atbildi
    const authData = response.data;
    
    // Pārliecināmies, ka loma ir skaitlis (lai Vue v-if strādātu pareizi)
    authData.roles = parseInt(authData.roles);
    user.value = authData;
    
    localStorage.setItem('user_auth', JSON.stringify(authData));
    axios.defaults.headers.common['Authorization'] = `Bearer ${authData.token}`;

    // 5. Ja klients, ielādējam katalogu
    if (user.value.roles == 3) {
      fetchProviders();
    }

    showRegister.value = false;
    alert("Reģistrācija veiksmīga!");
  } catch (error) {
    console.error("Reģistrācijas kļūda:", error.response?.data);
    const errorMsg = error.response?.data?.error || "Servera kļūda";
    alert("Kļūda: " + errorMsg);
  }
};

const handleLogout = () => {
  user.value = null;
  localStorage.removeItem('user_auth');
  delete axios.defaults.headers.common['Authorization'];
};

const step = ref(1);
const showBooking = ref(false);
const bookingData = reactive({
  service: '',
  date: '',
  time: ''
});

const occupiedTimes = ref([]);

const checkAvailableTimes = async () => {
  try {
    const response = await axios.get('http://127.0.0.1:8080/api/occupied-times/', {
      params: {
        provider_id: selectedProvider.value.id,
        date: bookingData.date  // ← Noņemiet .value
      }
    });

    const occupied = response.data; // Pieņemsim: ['09:00', '10:00']
    const allSlots = ['09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00'];
    
    // Izfiltrējam tikai brīvos laikus
    availableTimes.value = allSlots.filter(t => !occupied.includes(t));
    nextStep();
  } catch (error) {
    alert("Kļūda ielādējot laikus");
  }
};


const availability = reactive({
  start: '09:00',
  end: '17:00'
});

const availableTimes = ref([]);

const openCalendar = () => {
  activeTab.value = 'calendar';
};

const nextStep = () => { if (step.value < 4) step.value++; };
const prevStep = () => { if (step.value > 1) step.value--; };

const activeTab = ref('main'); // 'main' vai 'my-bookings'
const userReservations = ref([]);

// Ielādēt lietotāja pierakstus
const fetchReservations = async () => {
  try {
    console.log("Fetching reservations...");
    const response = await axios.get('http://127.0.0.1:8080/api/my-reservations/');
    console.log("Servera atbilde:", response.data);
    
    userReservations.value = response.data;
    
    // Pārbaudām katru rezervāciju
    userReservations.value.forEach(res => {
      console.log(`Rezervācija ${res.id}: service=${res.service}, date=${res.date}, time=${res.time}`);
    });
    
    activeTab.value = 'my-bookings';
  } catch (error) {
    console.error("Kļūda ielādējot pierakstus:", error);
    alert("Nevarēja ielādēt pierakstus!");
  }
};

// Veikt rezervāciju (Backend savienojums)
const confirmBooking = async () => {
  try {
    await axios.post('http://127.0.0.1:8080/api/book/', {
      provider_id: selectedProvider.value.id,
      service_name: bookingData.service,  // ← Noņemiet .value
      res_date: bookingData.date,        // ← Noņemiet .value
      res_time: bookingData.time         // ← Noņemiet .value
    });
    step.value = 4;
  } catch (error) {
    alert("Rezervācija neizdevās: " + error.response.data.error);
  }
};

// Atcelt pierakstu
const cancelBooking = async (id) => {
  if (confirm("Vai tiešām vēlaties atcelt šo pierakstu?")) {
    try {
      await axios.delete(`http://127.0.0.1:8080/api/cancel-booking/${id}/`);
      fetchReservations(); // Atsvaidzinām sarakstu
    } catch (error) {
      alert("Kļūda atceļot pierakstu");
    }
  }
};

const providers = ref([]); // Kataloga sniedzēji
const searchQuery = ref('');
const selectedIndustry = ref('');

// Sniedzēja jauna pakalpojuma dati
const newService = reactive({
  name: '',
  price: '',
  duration: '60'
});
const myServices = ref([]); // Paša sniedzēja izveidotie pakalpojumi

// Pārliecinies, ka šie mainīgie ir definēti augstāk
const viewingProvider = ref(null); 

// Šī ir funkcija, kuras tev trūkst:
const openProviderProfile = (provider) => {
  console.log("Atveram profilu speciālistam:", provider.username);
  console.log("Speciālista dati:", provider); 
  
  viewingProvider.value = provider;
};

// Un šī ir funkcija, kas būs vajadzīga pēc tam:
const startBookingFlow = (provider, service) => {
  selectedProvider.value = provider;
  
  // ŠEIT IR PROBLĒMA - bookingData ir reactive, nevis ref
  // Tāpēc jālieto bookingData.service, nevis bookingData.value.service
  bookingData.service = service.name;  // ← Noņemiet .value
  
  viewingProvider.value = null;
  showBooking.value = true;
  step.value = 2;
};
const selectedProvider = (provider) => {
  selectedProvider.value = provider; // Saglabājam izvēlēto cilvēku
  bookingData.value.service = '';    // Notīrām iepriekšējo pakalpojumu
  bookingData.value.date = '';       // Notīrām datumu
  step.value = 1;                    // Atveram 1. soli (pakalpojumi)
  showBooking.value = true;          // Parādām wizardu
};

const finishBooking = () => {
  showBooking.value = false;
  step.value = 1;
  bookingData.service = '';
  bookingData.date = '';
  bookingData.time = '';
};

const saveService = async () => {
  if (!newService.name || !newService.price) {
    alert("Lūdzu, aizpildi visus laukus!");
    return;
  }

  try {
    const response = await axios.post('http://127.0.0.1:8080/api/services/add/', {
      name: newService.name,
      price: newService.price,
      provider_id: user.value.id
    });

    if (response.status === 201) {
      alert("Pakalpojums pievienots!");
      newService.name = '';
      newService.price = '';
    }
  } catch (error) {
    console.error("Kļūda saglabājot pakalpojumu:", error);
    alert("Neizdevās saglabāt pakalpojumu.");
  }
};

import { computed } from 'vue';

const viewDate = ref(new Date());
const busyDates = ref(['2024-05-20', '2024-05-25']);

const currentMonthName = computed(() => {
  return viewDate.value.toLocaleString('lv-LV', { month: 'long' });
});

const currentYear = computed(() => viewDate.value.getFullYear());

const daysInMonth = computed(() => {
  const year = viewDate.value.getFullYear();
  const month = viewDate.value.getMonth();
  return new Date(year, month + 1, 0).getDate();
});

const firstDayOffset = computed(() => {
  const firstDay = new Date(viewDate.value.getFullYear(), viewDate.value.getMonth(), 1).getDay();
  return firstDay === 0 ? 6 : firstDay - 1; // Pielāgojam, lai nedēļa sākas ar Pirmdienu
});

const selectDate = (day) => {
  const year = viewDate.value.getFullYear();
  const month = String(viewDate.value.getMonth() + 1).padStart(2, '0');
  const d = String(day).padStart(2, '0');
  
  const dateStr = `${year}-${month}-${d}`;
  
  // Reactive objekts - bez .value
  bookingData.date = dateStr;
  
  console.log("Jaunais datums:", bookingData.date);
};

const isDateBusy = (day) => {
  const dateStr = `${currentYear.value}-${String(viewDate.value.getMonth() + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
  return busyDates.value.includes(dateStr);
};

const isSelected = (day) => {
  // 1. DROŠĪBAS PĀRBAUDE: Ja bookingData nav definēts, neko nedarām
  if (!bookingData || !bookingData.date) {  // ← Noņemiet .value
    return false;
  }

  try {
    const year = viewDate.value.getFullYear();
    const month = String(viewDate.value.getMonth() + 1).padStart(2, '0');
    const d = String(day).padStart(2, '0');
    const currentCellDate = `${year}-${month}-${d}`;

    return bookingData.value.date === currentCellDate;
  } catch (e) {
    // Ja nu gadījumā viewDate vēl nav ielādēts
    return false;
  }
};

const changeMonth = (offset) => {
  viewDate.value = new Date(viewDate.value.getFullYear(), viewDate.value.getMonth() + offset, 1);
};

const isPast = (day) => {
  const today = new Date();
  today.setHours(0, 0, 0, 0); // Atiestatām laiku uz dienas sākumu salīdzināšanai
  
  const checkDate = new Date(currentYear.value, viewDate.value.getMonth(), day);
  return checkDate < today;
};
</script>