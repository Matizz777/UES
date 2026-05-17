<template>
  <div :class="['dashboard-container', { 'admin-mode': user.roles === 1 }]">
    <header class="dashboard-nav" v-if="user.roles !== 1">
      <div class="nav-tabs">
        <button
          :class="{ active: activeTab === 'main' }"
          @click="activeTab = 'main'"
        >
          {{ user.roles === 2 ? '🏢 Speciālista panelis' : '🔍 Atrast speciālistu' }}
        </button>

        <button
          v-if="user.roles === 2"
          :class="{ active: activeTab === 'calendar' }"
          @click="activeTab = 'calendar'"
        >
          🗓️ Mans kalendārs
        </button>

        <button
          v-if="user.roles === 3"
          :class="{ active: activeTab === 'my-bookings' }"
          @click="activeTab = 'my-bookings'"
        >
          📋 Mani pieraksti
        </button>
      </div>
    </header>

    <main class="dashboard-content">
      <AdminPanel v-if="user.roles === 1" :user="user" />
      
      <ProviderDashboard
        v-else-if="user.roles === 2"
        :user="user"
        :active-tab="activeTab"
        @change-tab="activeTab = $event"
      />

      <ClientDashboard
        v-else-if="user.roles === 3"
        :user="user"
        :active-tab="activeTab"
      />
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import AdminPanel from './AdminPanel.vue';
import ProviderDashboard from './ProviderDashboard.vue';
import ClientDashboard from './ClientDashboard.vue';

defineProps({ user: Object });

const activeTab = ref('main');
</script>

<style scoped>
.dashboard-container.admin-mode {
  padding: 0;
  margin: 0;
  max-width: 100%;
}

.dashboard-container.admin-mode .dashboard-content {
  padding: 0;
  margin: 0;
}
</style>