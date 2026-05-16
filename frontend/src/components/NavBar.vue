<template>
  <nav class="navbar">
    <div class="logo">
      <span class="logo-icon">☁️</span> UES
    </div>

    <div class="auth-buttons">
      <template v-if="user">
        <div class="user-menu">
          <!-- Notification bell — only for clients (roles=3) -->
          <NotificationBell v-if="user.roles === 3" />

          <div class="user-info">
            <div class="avatar">{{ user.username[0].toUpperCase() }}</div>
            <div class="user-details">
              <span class="welcome-msg">{{ user.username }}</span>
              <span class="user-role">
                {{ user.roles === 2 ? 'Pakalpojuma sniedzējs' : 'Klients' }}
              </span>
            </div>
          </div>
          <button class="btn-logout" @click="$emit('logout')" title="Iziet">
            <span class="logout-icon">→</span>
          </button>
        </div>
      </template>
    </div>
  </nav>
</template>

<script setup>
import NotificationBell from './NotificationBell.vue';

defineProps({ user: Object });
defineEmits(['logout']);
</script>