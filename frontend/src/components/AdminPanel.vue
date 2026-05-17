<template>
  <div class="admin-panel">
    <div class="admin-header">
      <h1>👑 Admin Panelis</h1>
      <div class="admin-tabs">
        <button :class="{ active: activeTab === 'dashboard' }" @click="activeTab = 'dashboard'">
          📊 Panelis
        </button>
        <button :class="{ active: activeTab === 'users' }" @click="activeTab = 'users'">
          👥 Lietotāji
        </button>
        <button :class="{ active: activeTab === 'services' }" @click="activeTab = 'services'">
          🛠️ Pakalpojumi
        </button>
        <button :class="{ active: activeTab === 'bookings' }" @click="activeTab = 'bookings'">
          📅 Pieraksti
        </button>
      </div>
    </div>

    <div class="admin-content">
      <!-- Dashboard Tab -->
      <div v-if="activeTab === 'dashboard'" class="dashboard-tab">
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon">👥</div>
            <div class="stat-info">
              <h3>{{ stats.total_users || 0 }}</h3>
              <p>Kopā lietotāju</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">🏢</div>
            <div class="stat-info">
              <h3>{{ stats.providers || 0 }}</h3>
              <p>Pakalpojumu sniedzēji</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">👤</div>
            <div class="stat-info">
              <h3>{{ stats.clients || 0 }}</h3>
              <p>Klienti</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">📅</div>
            <div class="stat-info">
              <h3>{{ stats.total_bookings || 0 }}</h3>
              <p>Kopā pierakstu</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">⏳</div>
            <div class="stat-info">
              <h3>{{ stats.upcoming_bookings || 0 }}</h3>
              <p>Gaidāmie</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">💰</div>
            <div class="stat-info">
              <h3>{{ (stats.total_revenue || 0).toFixed(2) }} €</h3>
              <p>Kopējais apgrozījums</p>
            </div>
          </div>
        </div>

        <div class="charts-row">
          <div class="chart-card">
            <h3>🔥 Populārākie pakalpojumi</h3>
            <div class="bar-chart">
              <div v-for="service in stats.top_services" :key="service.name" class="bar-item">
                <span class="bar-label">{{ service.name }}</span>
                <div class="bar-bg">
                  <div class="bar-fill" :style="{ width: (service.count / maxCount * 100) + '%' }">
                    <span class="bar-count">{{ service.count }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          </div>

            <div class="chart-card">
            <h3>📊 Ikmēneša statistika</h3>
            <div class="monthly-stats-table">
                <div class="monthly-header">
                <span>Mēnesis</span>
                <span>Pieraksti</span>
                <span>Ieņēmumi</span>
                <span>Trends</span>
                </div>
                <div v-for="month in stats.monthly_stats" :key="month.month" class="monthly-row">
                <span class="month-name">{{ month.month.slice(5) }} / {{ month.month.slice(0,4) }}</span>
                <span class="month-count">
                    <span class="count-badge">{{ month.count }}</span>
                </span>
                <span class="month-revenue">{{ month.revenue }} €</span>
                <span class="month-trend">
                    <span :class="getTrendClass(month.count, stats.monthly_stats)">
                    {{ getTrendIcon(month.count, stats.monthly_stats) }}
                    </span>
                </span>
                </div>
            </div>
            
            <div class="quick-stats">
                <div class="quick-stat">
                <div class="quick-stat-icon">📈</div>
                <div class="quick-stat-info">
                    <div class="quick-stat-value">{{ totalBookingsCount }}</div>
                    <div class="quick-stat-label">Kopā pieraksti</div>
                </div>
                </div>
                <div class="quick-stat">
                <div class="quick-stat-icon">💰</div>
                <div class="quick-stat-info">
                    <div class="quick-stat-value">{{ totalRevenueMonthly }} €</div>
                    <div class="quick-stat-label">Kopējie ieņēmumi</div>
                </div>
                </div>
                <div class="quick-stat">
                <div class="quick-stat-icon">🏆</div>
                <div class="quick-stat-info">
                    <div class="quick-stat-value">{{ bestMonthName }}</div>
                    <div class="quick-stat-label">Populārākais</div>
                </div>
                </div>
            </div>
            </div>

        <div class="recent-card">
          <h3>🕐 Pēdējie pieraksti</h3>
          <div class="table-wrapper">
            <table class="data-table">
              <thead>
                <tr><th>ID</th><th>Pakalpojums</th><th>Klients</th><th>Sniedzējs</th><th>Datums</th><th>Laiks</th><th>Statuss</th><th>Cena</th></tr>
              </thead>
              <tbody>
                <tr v-for="b in stats.recent_bookings" :key="b.id">
                  <td>{{ b.id }}</td>
                  <td>{{ b.service }}</td>
                  <td>{{ b.client }}</td>
                  <td>{{ b.provider }}</td>
                  <td>{{ b.date }}</td>
                  <td>{{ b.time }}</td>
                  <td><span :class="'status-' + b.status">{{ b.status === 'upcoming' ? 'Gaidāms' : b.status === 'completed' ? 'Pabeigts' : 'Atcelts' }}</span></td>
                  <td>{{ b.price }} €</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Users Tab -->
      <div v-if="activeTab === 'users'" class="users-tab">
        <div class="table-header">
          <h3>👥 Lietotāji</h3>
          <div class="filters">
            <select v-model="userRoleFilter" @change="loadUsers">
              <option value="all">Visas lomas</option>
              <option value="1">Admins</option>
              <option value="2">Sniedzēji</option>
              <option value="3">Klienti</option>
            </select>
            <button class="btn-add" @click="openUserModal()">+ Pievienot</button>
          </div>
        </div>
        <div class="table-wrapper">
          <table class="data-table">
            <thead>
              <tr><th>ID</th><th>Lietotājvārds</th><th>E-pasts</th><th>Loma</th><th>Tālrunis</th><th>Statuss</th><th>Darbības</th></tr>
            </thead>
            <tbody>
              <tr v-for="u in paginatedUsers" :key="u.id">
                <td>{{ u.id }}</td>
                <td>{{ u.username }}</td>
                <td>{{ u.email }}</td>
                <td>{{ getRoleName(u.roles) }}</td>
                <td>{{ u.phone || '-' }}</td>
                <td><span :class="u.is_active ? 'status-active' : 'status-inactive'">{{ u.is_active ? 'Aktīvs' : 'Bloķēts' }}</span></td>
                <td class="actions">
                  <button class="btn-icon edit" @click="openUserModal(u)">✏️</button>
                  <button class="btn-icon delete" @click="deleteUser(u.id)">🗑️</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="pagination" v-if="totalUsersPages > 1">
          <button @click="usersPage--" :disabled="usersPage === 1">←</button>
          <div class="page-numbers">
            <button v-for="page in totalUsersPages" :key="page" @click="usersPage = page" :class="{ active: usersPage === page }">{{ page }}</button>
          </div>
          <button @click="usersPage++" :disabled="usersPage === totalUsersPages">→</button>
          <span class="page-info">{{ users.length }} kopā</span>
        </div>
      </div>

      <!-- Services Tab -->
      <div v-if="activeTab === 'services'" class="services-tab">
        <div class="table-header">
          <h3>🛠️ Pakalpojumi</h3>
        </div>
        <div class="table-wrapper">
          <table class="data-table">
            <thead>
              <tr><th>ID</th><th>Nosaukums</th><th>Cena</th><th>Sniedzējs</th><th>Ilgums</th><th>Darba laiks</th><th>Darbības</th></tr>
            </thead>
            <tbody>
              <tr v-for="s in paginatedServices" :key="s.id">
                <td>{{ s.id }}</td>
                <td>{{ s.name }}</td>
                <td>{{ s.price }} €</td>
                <td>{{ s.provider_name }}</td>
                <td>{{ s.duration_minutes }} min</td>
                <td>{{ s.work_start }} - {{ s.work_end }}</td>
                <td class="actions">
                  <button class="btn-icon delete" @click="deleteService(s.id)">🗑️</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="pagination" v-if="totalServicesPages > 1">
          <button @click="servicesPage--" :disabled="servicesPage === 1">←</button>
          <div class="page-numbers">
            <button v-for="page in totalServicesPages" :key="page" @click="servicesPage = page" :class="{ active: servicesPage === page }">{{ page }}</button>
          </div>
          <button @click="servicesPage++" :disabled="servicesPage === totalServicesPages">→</button>
          <span class="page-info">{{ services.length }} kopā</span>
        </div>
      </div>

      <!-- Bookings Tab -->
      <div v-if="activeTab === 'bookings'" class="bookings-tab">
        <div class="table-header">
          <h3>📅 Visi pieraksti</h3>
          <select v-model="bookingStatusFilter" @change="loadBookings">
            <option value="all">Visi</option>
            <option value="upcoming">Gaidāmie</option>
            <option value="completed">Pabeigtie</option>
            <option value="cancelled">Atceltie</option>
          </select>
        </div>
        <div class="table-wrapper">
          <table class="data-table">
            <thead>
              <tr><th>ID</th><th>Pakalpojums</th><th>Klients</th><th>Sniedzējs</th><th>Datums</th><th>Laiks</th><th>Statuss</th><th>Cena</th><th>Darbības</th></tr>
            </thead>
            <tbody>
              <tr v-for="b in paginatedBookings" :key="b.id">
                <td>{{ b.id }}</td>
                <td>{{ b.service }}</td>
                <td>{{ b.client }}</td>
                <td>{{ b.provider }}</td>
                <td>{{ b.date }}</td>
                <td>{{ b.time }}</td>
                <td><span :class="'status-' + b.status">{{ b.status === 'upcoming' ? 'Gaidāms' : b.status === 'completed' ? 'Pabeigts' : 'Atcelts' }}</span></td>
                <td>{{ b.price }} €</td>
                <td class="actions">
                  <button class="btn-icon edit" @click="openBookingModal(b)">✏️</button>
                  <button class="btn-icon delete" @click="deleteBooking(b.id)">🗑️</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="pagination" v-if="totalBookingsPages > 1">
          <button @click="bookingsPage--" :disabled="bookingsPage === 1">←</button>
          <div class="page-numbers">
            <button v-for="page in totalBookingsPages" :key="page" @click="bookingsPage = page" :class="{ active: bookingsPage === page }">{{ page }}</button>
          </div>
          <button @click="bookingsPage++" :disabled="bookingsPage === totalBookingsPages">→</button>
          <span class="page-info">{{ bookings.length }} kopā</span>
        </div>
      </div>
    </div>

    <!-- User Modal -->
    <div v-if="showUserModal" class="modal-overlay" @click.self="showUserModal = false">
      <div class="modal-card">
        <h3>{{ editingUser ? 'Labot lietotāju' : 'Pievienot lietotāju' }}</h3>
        <input v-model="userForm.username" placeholder="Lietotājvārds" />
        <input v-model="userForm.email" placeholder="E-pasts" />
        <input v-model="userForm.password" v-if="!editingUser" placeholder="Parole" type="password" />
        <select v-model="userForm.roles">
          <option value="1">Admin</option>
          <option value="2">Pakalpojumu sniedzējs</option>
          <option value="3">Klients</option>
        </select>
        <input v-model="userForm.phone" placeholder="Tālrunis" />
        <textarea v-model="userForm.description" placeholder="Apraksts" rows="2"></textarea>
        <div class="modal-footer">
          <button class="btn-cancel" @click="showUserModal = false">Atcelt</button>
          <button class="btn-save" @click="saveUser">Saglabāt</button>
        </div>
      </div>
    </div>

    <!-- Booking Modal -->
    <div v-if="showBookingModal" class="modal-overlay" @click.self="showBookingModal = false">
      <div class="modal-card">
        <h3>Labot pierakstu</h3>
        <input v-model="bookingForm.service" placeholder="Pakalpojums" />
        <input type="date" v-model="bookingForm.date" />
        <input type="time" v-model="bookingForm.time" />
        <input type="number" v-model="bookingForm.price" placeholder="Cena" step="0.01" />
        <select v-model="bookingForm.status">
          <option value="upcoming">Gaidāms</option>
          <option value="completed">Pabeigts</option>
          <option value="cancelled">Atcelts</option>
        </select>
        <div class="modal-footer">
          <button class="btn-cancel" @click="showBookingModal = false">Atcelt</button>
          <button class="btn-save" @click="saveBooking">Saglabāt</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';

const activeTab = ref('dashboard');
const stats = ref({});
const users = ref([]);
const services = ref([]);
const bookings = ref([]);
const userRoleFilter = ref('all');
const bookingStatusFilter = ref('all');
const showUserModal = ref(false);
const showBookingModal = ref(false);
const editingUser = ref(null);
const editingBooking = ref(null);
const maxCount = ref(1);
const maxMonthly = ref(1);

// Pagination
const usersPage = ref(1);
const servicesPage = ref(1);
const bookingsPage = ref(1);
const itemsPerPage = ref(10);

const paginatedUsers = computed(() => {
  const start = (usersPage.value - 1) * itemsPerPage.value;
  const end = start + itemsPerPage.value;
  return users.value.slice(start, end);
});

const totalUsersPages = computed(() => Math.ceil(users.value.length / itemsPerPage.value));

const paginatedServices = computed(() => {
  const start = (servicesPage.value - 1) * itemsPerPage.value;
  const end = start + itemsPerPage.value;
  return services.value.slice(start, end);
});

const totalServicesPages = computed(() => Math.ceil(services.value.length / itemsPerPage.value));

const paginatedBookings = computed(() => {
  const start = (bookingsPage.value - 1) * itemsPerPage.value;
  const end = start + itemsPerPage.value;
  return bookings.value.slice(start, end);
});

const totalBookingsPages = computed(() => Math.ceil(bookings.value.length / itemsPerPage.value));

const userForm = ref({ username: '', email: '', password: '', roles: '3', phone: '', description: '' });
const bookingForm = ref({ service: '', date: '', time: '', price: '', status: 'upcoming' });

const getRoleName = (role) => {
  if (role === 1) return 'Admin';
  if (role === 2) return 'Sniedzējs';
  return 'Klients';
};

const loadStats = async () => {
  try {
    const { data } = await axios.get('http://127.0.0.1:8080/api/admin/stats/');
    stats.value = data;
    if (data.top_services && data.top_services.length) {
      maxCount.value = Math.max(...data.top_services.map(s => s.count));
    }
    if (data.monthly_stats && data.monthly_stats.length) {
      maxMonthly.value = Math.max(...data.monthly_stats.map(m => m.count));
    }
  } catch (e) {
    console.error(e);
  }
};

const loadUsers = async () => {
  try {
    const { data } = await axios.get('http://127.0.0.1:8080/api/admin/users/', {
      params: { role: userRoleFilter.value }
    });
    users.value = data;
    usersPage.value = 1;
  } catch (e) {
    console.error(e);
  }
};

const loadServices = async () => {
  try {
    const { data } = await axios.get('http://127.0.0.1:8080/api/admin/services/');
    services.value = data;
    servicesPage.value = 1;
  } catch (e) {
    console.error(e);
  }
};

const loadBookings = async () => {
  try {
    const { data } = await axios.get('http://127.0.0.1:8080/api/admin/bookings/', {
      params: { status: bookingStatusFilter.value }
    });
    bookings.value = data;
    bookingsPage.value = 1;
  } catch (e) {
    console.error(e);
  }
};

const openUserModal = (user = null) => {
  editingUser.value = user;
  if (user) {
    userForm.value = { ...user, password: '' };
  } else {
    userForm.value = { username: '', email: '', password: '', roles: '3', phone: '', description: '' };
  }
  showUserModal.value = true;
};

const saveUser = async () => {
  try {
    if (editingUser.value) {
      await axios.put(`http://127.0.0.1:8080/api/admin/users/${editingUser.value.id}/`, userForm.value);
    } else {
      await axios.post('http://127.0.0.1:8080/api/register/', userForm.value);
    }
    showUserModal.value = false;
    await loadUsers();
    await loadStats();
  } catch (e) {
    alert('Kļūda saglabājot lietotāju');
  }
};

const deleteUser = async (id) => {
  if (!confirm('Vai tiešām dzēst šo lietotāju?')) return;
  try {
    await axios.delete(`http://127.0.0.1:8080/api/admin/users/delete/${id}/`);
    await loadUsers();
    await loadStats();
  } catch (e) {
    alert('Kļūda dzēšot lietotāju');
  }
};

const deleteService = async (id) => {
  if (!confirm('Vai tiešām dzēst šo pakalpojumu?')) return;
  try {
    await axios.delete(`http://127.0.0.1:8080/api/admin/services/delete/${id}/`);
    await loadServices();
    await loadStats();
  } catch (e) {
    alert('Kļūda dzēšot pakalpojumu');
  }
};

const openBookingModal = (booking) => {
  editingBooking.value = booking;
  bookingForm.value = { ...booking };
  showBookingModal.value = true;
};

const saveBooking = async () => {
  try {
    await axios.put(`http://127.0.0.1:8080/api/admin/bookings/${editingBooking.value.id}/`, bookingForm.value);
    showBookingModal.value = false;
    await loadBookings();
    await loadStats();
  } catch (e) {
    alert('Kļūda saglabājot pierakstu');
  }
};

const deleteBooking = async (id) => {
  if (!confirm('Vai tiešām dzēst šo pierakstu?')) return;
  try {
    await axios.delete(`http://127.0.0.1:8080/api/admin/bookings/delete/${id}/`);
    await loadBookings();
    await loadStats();
  } catch (e) {
    alert('Kļūda dzēšot pierakstu');
  }
};

onMounted(() => {
  loadStats();
  loadUsers();
  loadServices();
  loadBookings();
});

const totalRevenueMonthly = computed(() => {
  if (!stats.value.monthly_stats) return 0;
  return stats.value.monthly_stats.reduce((sum, m) => sum + (m.revenue || 0), 0).toFixed(2);
});

const bestMonthName = computed(() => {
  if (!stats.value.monthly_stats || stats.value.monthly_stats.length === 0) return '-';
  const best = [...stats.value.monthly_stats].sort((a, b) => b.count - a.count)[0];
  return best.month.slice(5);
});

const getTrendIcon = (count, months) => {
  const index = months.findIndex(m => m.count === count);
  if (index === 0) return '→';
  const prevCount = months[index - 1]?.count || count;
  if (count > prevCount) return '📈';
  if (count < prevCount) return '📉';
  return '→';
};

const getTrendClass = (count, months) => {
  const index = months.findIndex(m => m.count === count);
  if (index === 0) return 'trend-same';
  const prevCount = months[index - 1]?.count || count;
  if (count > prevCount) return 'trend-up';
  if (count < prevCount) return 'trend-down';
  return 'trend-same';
};
</script>

<style scoped>
.admin-panel {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1rem;
}

.admin-header {
  background: white;
  border-radius: 20px;
  padding: 1.2rem 1.8rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.admin-header h1 {
  margin: 0 0 1rem 0;
  font-size: 1.6rem;
  color: #2c3e50;
}

.admin-tabs {
  display: flex;
  gap: 0.6rem;
  flex-wrap: wrap;
}

.admin-tabs button {
  padding: 0.6rem 1.3rem;
  border: none;
  border-radius: 40px;
  cursor: pointer;
  font-weight: 600;
  background: #f0f2f5;
  color: #555;
  transition: all 0.2s;
  font-size: 0.9rem;
}

.admin-tabs button.active {
  background: #4a90e2;
  color: white;
  box-shadow: 0 2px 8px rgba(74, 144, 226, 0.3);
}

.admin-tabs button:hover:not(.active) {
  background: #e4e6e9;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  background: white;
  border-radius: 20px;
  padding: 1.2rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.stat-icon {
  font-size: 2rem;
}

.stat-info h3 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
  color: #2c3e50;
}

.stat-info p {
  margin: 0;
  color: #888;
  font-size: 0.75rem;
}

.charts-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.chart-card {
  background: white;
  border-radius: 20px;
  padding: 1.2rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  margin: 10px;
}

.chart-card h3 {
  margin: 0 0 1rem 0;
  font-size: 0.95rem;
  color: #2c3e50;
}

.bar-item {
  margin-bottom: 0.8rem;
}

.bar-label {
  font-size: 0.75rem;
  display: block;
  margin-bottom: 0.25rem;
  color: #555;
}

.bar-bg {
  background: #e8edf2;
  border-radius: 12px;
  overflow: hidden;
}

.bar-fill {
  background: linear-gradient(90deg, #4a90e2, #3b82f6);
  color: white;
  font-size: 0.65rem;
  padding: 0.2rem 0.5rem;
  text-align: right;
  border-radius: 12px;
  transition: width 0.3s ease;
}

.recent-card {
  background: white;
  border-radius: 20px;
  padding: 1.2rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.recent-card h3 {
  margin: 0 0 1rem 0;
  font-size: 0.95rem;
  color: #2c3e50;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.table-header h3 {
  margin: 0;
  font-size: 1rem;
  color: #2c3e50;
}

.filters {
  display: flex;
  gap: 0.6rem;
  align-items: center;
}

.filters select {
  padding: 0.5rem 1rem;
  border: 1px solid #e0e0e0;
  border-radius: 40px;
  background: white;
  font-family: inherit;
  font-size: 0.85rem;
  cursor: pointer;
  outline: none;
}

.btn-add {
  background: #4a90e2;
  color: white;
  border: none;
  padding: 0.5rem 1.2rem;
  border-radius: 40px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.85rem;
  transition: all 0.2s;
}

.btn-add:hover {
  background: #357abd;
  transform: translateY(-1px);
}

.table-wrapper {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 16px;
  overflow: hidden;
}

.data-table th,
.data-table td {
  padding: 0.8rem 0.6rem;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.data-table th {
  background: #f8f9fa;
  font-weight: 600;
  font-size: 0.8rem;
  color: #555;
}

.data-table td {
  font-size: 0.85rem;
}

.actions {
  display: flex;
  gap: 0.3rem;
}

.btn-icon {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1rem;
  padding: 0.3rem 0.5rem;
  border-radius: 10px;
  transition: all 0.2s;
}

.btn-icon.edit:hover {
  background: #e3f2fd;
  color: #4a90e2;
}

.btn-icon.delete:hover {
  background: #ffebee;
  color: #e53935;
}

.status-active {
  color: #2e7d32;
  background: #e8f5e9;
  padding: 0.2rem 0.6rem;
  border-radius: 20px;
  font-size: 0.7rem;
  display: inline-block;
}

.status-inactive {
  color: #c62828;
  background: #ffebee;
  padding: 0.2rem 0.6rem;
  border-radius: 20px;
  font-size: 0.7rem;
  display: inline-block;
}

.status-upcoming {
  color: #1565c0;
  background: #e3f2fd;
  padding: 0.2rem 0.6rem;
  border-radius: 20px;
  font-size: 0.7rem;
  display: inline-block;
}

.status-completed {
  color: #2e7d32;
  background: #e8f5e9;
  padding: 0.2rem 0.6rem;
  border-radius: 20px;
  font-size: 0.7rem;
  display: inline-block;
}

.status-cancelled {
  color: #c62828;
  background: #ffebee;
  padding: 0.2rem 0.6rem;
  border-radius: 20px;
  font-size: 0.7rem;
  display: inline-block;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1.5rem;
  flex-wrap: wrap;
}

.pagination button {
  width: 38px;
  height: 38px;
  padding: 0;
  border: none;
  background: white;
  border-radius: 14px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  color: #4a5568;
  transition: all 0.2s ease;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
  justify-content: center;
}

.pagination button:hover:not(:disabled) {
  background: #4a90e2;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(74, 144, 226, 0.25);
}

.pagination button.active {
  background: #4a90e2;
  color: white;
  box-shadow: 0 2px 8px rgba(74, 144, 226, 0.3);
}

.pagination button:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.page-numbers {
  display: flex;
  gap: 0.4rem;
  flex-wrap: wrap;
}

.page-info {
  font-size: 0.75rem;
  color: #888;
  background: #f5f5f5;
  padding: 0.3rem 0.8rem;
  border-radius: 30px;
  margin-left: 0.5rem;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-card {
  background: white;
  border-radius: 24px;
  padding: 1.5rem;
  width: 90%;
  max-width: 450px;
}

.modal-card h3 {
  margin: 0 0 1rem 0;
  font-size: 1.2rem;
}

.modal-card input,
.modal-card select,
.modal-card textarea {
  width: 100%;
  padding: 0.7rem;
  margin-bottom: 0.8rem;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  font-family: inherit;
  font-size: 0.9rem;
}

.modal-card input:focus,
.modal-card select:focus,
.modal-card textarea:focus {
  outline: none;
  border-color: #4a90e2;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.8rem;
  margin-top: 1rem;
}

.btn-cancel {
  background: #f0f2f5;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 40px;
  cursor: pointer;
  font-weight: 500;
}

.btn-save {
  background: #4a90e2;
  color: white;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 40px;
  cursor: pointer;
  font-weight: 500;
}

.btn-save:hover {
  background: #357abd;
}

@media (max-width: 768px) {
  .admin-panel {
    padding: 0.5rem;
  }
  
  .admin-header {
    padding: 1rem;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 0.6rem;
  }
  
  .stat-card {
    padding: 0.8rem;
  }
  
  .stat-icon {
    font-size: 1.5rem;
  }
  
  .stat-info h3 {
    font-size: 1.2rem;
  }
  
  .pagination button {
    width: 34px;
    height: 34px;
    font-size: 0.8rem;
    border-radius: 10px;
  }
  
  .data-table th,
  .data-table td {
    padding: 0.5rem 0.3rem;
    font-size: 0.7rem;
  }
  
  .admin-tabs button {
    padding: 0.4rem 1rem;
    font-size: 0.8rem;
  }
}

.enhanced-line-chart {
  position: relative;
  padding: 1rem 0 0.5rem 0;
}

.chart-container {
  position: relative;
  height: 200px;
  margin-bottom: 0.5rem;
}

.chart-svg {
  width: 100%;
  height: 100%;
}

.chart-line {
  stroke: #4a90e2;
  stroke-width: 3;
  fill: none;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.chart-area {
  fill: url(#areaGradient);
  opacity: 0.3;
}

.chart-dot {
  fill: #4a90e2;
  stroke: white;
  stroke-width: 2;
  cursor: pointer;
  transition: all 0.2s ease;
}

.chart-dot:hover {
  fill: #e74c3c;
  r: 8;
}

.month-labels {
  display: flex;
  justify-content: space-around;
  margin-top: 0.5rem;
  padding: 0 0.5rem;
}

.month-label {
  font-size: 0.7rem;
  color: #888;
  text-align: center;
  flex: 1;
}

.stats-summary {
  display: flex;
  justify-content: space-between;
  margin-top: 1rem;
  padding-top: 0.8rem;
  border-top: 1px solid #eee;
}

.stat-summary-item {
  text-align: center;
  flex: 1;
}

.stat-summary-value {
  font-size: 1.1rem;
  font-weight: 700;
  color: #2c3e50;
}

.stat-summary-label {
  font-size: 0.7rem;
  color: #888;
}
</style>