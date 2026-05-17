<template>
  <nav class="navbar">
    <div class="logo">
      <span class="logo-icon">☁️</span> UES
    </div>

    <div class="auth-buttons">
      <template v-if="user">
        <div class="user-menu">
          <NotificationBell v-if="user.roles === 2 || user.roles === 3" />

          <button class="profile-btn" @click="$emit('show-profile')" title="Profils">
            👤
          </button>

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
defineEmits(['logout', 'show-profile']);
</script>

<style scoped>
.profile-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0.3rem;
  border-radius: 50%;
  transition: background 0.2s;
  width: 35px;
  height: 35px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.profile-btn:hover {
  background: #e8f5e9;
}
</style>