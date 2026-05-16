<template>
  <div class="dashboard-container">
    <header class="dashboard-nav">
      <div class="nav-tabs">
        <button
          :class="{ active: activeTab === 'main' }"
          @click="activeTab = 'main'"
        >
          {{ user.roles === 2 ? '🏢 Speciālista panelis' : '🔍 Atrast speciālistu' }}
        </button>

        <!-- Calendar tab — only for providers -->
        <button
          v-if="user.roles === 2"
          :class="{ active: activeTab === 'calendar' }"
          @click="activeTab = 'calendar'"
        >
          🗓️ Mans kalendārs
        </button>

        <button
          :class="{ active: activeTab === 'my-bookings' }"
          @click="activeTab = 'my-bookings'"
        >
          {{ user.roles === 2 ? '📅 Klientu pieraksti' : '📋 Mani pieraksti' }}
        </button>
      </div>
    </header>

    <main class="dashboard-content">
      <ProviderDashboard
        v-if="user.roles === 2"
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
import ProviderDashboard from './ProviderDashboard.vue';
import ClientDashboard   from './ClientDashboard.vue';

defineProps({ user: Object });

const activeTab = ref('main');
</script>