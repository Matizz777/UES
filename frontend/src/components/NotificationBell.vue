<template>
  <div class="notif-wrapper" ref="wrapperRef">
    <!-- Bell button -->
    <button class="bell-btn" @click="toggleOpen">
      🔔
      <span v-if="unreadCount > 0" class="badge">{{ unreadCount }}</span>
    </button>

    <!-- Dropdown -->
    <div v-if="open" class="notif-dropdown">
      <div class="notif-header">
        <span>Paziņojumi</span>
        <button v-if="unreadCount > 0" class="mark-read-btn" @click="markAllRead">
          Atzīmēt visus kā lasītus
        </button>
      </div>

      <div v-if="loading" class="notif-empty">Ielādē...</div>
      <div v-else-if="notifications.length === 0" class="notif-empty">
        Nav jaunu paziņojumu.
      </div>

      <div v-else class="notif-list">
        <div
          v-for="n in notifications"
          :key="n.id"
          class="notif-item"
          :class="{ unread: !n.is_read }"
        >
          <div class="notif-item-header">
            <strong>{{ n.title }}</strong>
            <button class="notif-delete" @click="deleteNotif(n.id)">✕</button>
          </div>
          <p class="notif-message">{{ n.message }}</p>
          <span class="notif-time">{{ n.created_at }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import axios from 'axios';

const open          = ref(false);
const notifications = ref([]);
const loading       = ref(false);
const wrapperRef    = ref(null);

const unreadCount = computed(() => notifications.value.filter(n => !n.is_read).length);

const load = async () => {
  loading.value = true;
  try {
    const { data } = await axios.get('http://127.0.0.1:8080/api/notifications/');
    notifications.value = data;
  } catch (e) {
    console.error('Kļūda ielādējot paziņojumus:', e);
  } finally {
    loading.value = false;
  }
};

const toggleOpen = async () => {
  open.value = !open.value;
  if (open.value) await load();
};

const markAllRead = async () => {
  try {
    await axios.post('http://127.0.0.1:8080/api/notifications/read/');
    notifications.value = notifications.value.map(n => ({ ...n, is_read: true }));
  } catch (e) {
    console.error(e);
  }
};

const deleteNotif = async (id) => {
  try {
    await axios.delete(`http://127.0.0.1:8080/api/notifications/delete/${id}/`);
    notifications.value = notifications.value.filter(n => n.id !== id);
  } catch (e) {
    console.error(e);
  }
};

// Close on outside click
const handleClickOutside = (e) => {
  if (wrapperRef.value && !wrapperRef.value.contains(e.target)) {
    open.value = false;
  }
};

// Poll for new notifications every 30s
let pollInterval = null;

onMounted(() => {
  load();
  pollInterval = setInterval(load, 30000);
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  clearInterval(pollInterval);
  document.removeEventListener('click', handleClickOutside);
});
</script>

<style scoped>
.notif-wrapper {
  position: relative;
  display: inline-block;
}

.bell-btn {
  background: none;
  border: none;
  font-size: 1.3rem;
  cursor: pointer;
  position: relative;
  padding: 0.3rem;
  line-height: 1;
}

.badge {
  position: absolute;
  top: -4px;
  right: -4px;
  background: #e53935;
  color: #fff;
  font-size: 0.65rem;
  font-weight: 700;
  border-radius: 50%;
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}

.notif-dropdown {
  position: absolute;
  right: 0;
  top: calc(100% + 8px);
  width: 320px;
  background: #fff;
  border-radius: 14px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.15);
  z-index: 999;
  overflow: hidden;
}

.notif-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #f0f0f0;
  font-weight: 600;
  font-size: 0.9rem;
}

.mark-read-btn {
  background: none;
  border: none;
  font-size: 0.78rem;
  color: #388e3c;
  cursor: pointer;
  font-weight: 500;
}

.notif-empty {
  padding: 1.25rem 1rem;
  color: #aaa;
  font-size: 0.9rem;
  text-align: center;
}

.notif-list {
  max-height: 380px;
  overflow-y: auto;
}

.notif-item {
  padding: 0.85rem 1rem;
  border-bottom: 1px solid #f5f5f5;
  transition: background 0.1s;
}

.notif-item:last-child { border-bottom: none; }
.notif-item.unread { background: #f1f8e9; }

.notif-item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.5rem;
  margin-bottom: 0.3rem;
}

.notif-item-header strong {
  font-size: 0.88rem;
  line-height: 1.3;
}

.notif-delete {
  background: none;
  border: none;
  color: #ccc;
  cursor: pointer;
  font-size: 0.8rem;
  padding: 0;
  flex-shrink: 0;
  line-height: 1;
}
.notif-delete:hover { color: #e53935; }

.notif-message {
  font-size: 0.83rem;
  color: #555;
  margin: 0 0 0.3rem;
  white-space: pre-line;
  line-height: 1.45;
}

.notif-time {
  font-size: 0.75rem;
  color: #bbb;
}
</style>