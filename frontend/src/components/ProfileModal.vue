<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="profile-modal">
      <button class="modal-close" @click="$emit('close')">✕</button>
      
      <div class="profile-tabs">
        <button :class="{ active: activeTab === 'info' }" @click="activeTab = 'info'">
          {{ $t('profile_info') }}
        </button>
        <button :class="{ active: activeTab === 'password' }" @click="activeTab = 'password'">
          {{ $t('change_password') }}
        </button>
        <button v-if="user.roles === 2" :class="{ active: activeTab === 'business' }" @click="activeTab = 'business'">
          {{ $t('business_info') }}
        </button>
      </div>
      
      <div class="profile-content">
        <div v-if="activeTab === 'info'" class="tab-pane">
          <div class="form-group">
            <label>{{ $t('username') }}</label>
            <input type="text" v-model="profile.username" disabled class="disabled-input" />
          </div>
          
          <div class="form-group">
            <label>{{ $t('email') }}</label>
            <input type="email" v-model="profile.email" />
          </div>
          
          <div class="form-row-2">
            <div class="form-group">
              <label>{{ $t('first_name') }}</label>
              <input type="text" v-model="profile.first_name" :placeholder="$t('first_name')" />
            </div>
            <div class="form-group">
              <label>{{ $t('last_name') }}</label>
              <input type="text" v-model="profile.last_name" :placeholder="$t('last_name')" />
            </div>
          </div>
          
          <div class="form-group">
            <label>{{ $t('phone') }}</label>
            <input type="tel" v-model="profile.phone" placeholder="+371 ..." />
          </div>
          
          <div v-if="user.roles === 2" class="form-group">
            <label>{{ $t('industry_field') }}</label>
            <select v-model="profile.industry">
              <option value="">{{ $t('industry_field') }}</option>
              <option value="Skaistumkopšana">Skaistumkopšana</option>
              <option value="Medicīna">Medicīna</option>
              <option value="IT pakalpojumi">IT pakalpojumi</option>
              <option value="Sports">Sports un Fitness</option>
              <option value="Cits">Cits</option>
            </select>
          </div>
          
          <div class="form-group">
            <label>{{ $t('description_label') }}</label>
            <textarea v-model="profile.description" rows="3" :placeholder="$t('service_description')"></textarea>
          </div>
          
          <button class="btn-primary" @click="saveProfile" :disabled="saving">
            {{ saving ? $t('loading') : $t('save') }}
          </button>
        </div>
        
        <div v-if="activeTab === 'password'" class="tab-pane">
          <div class="form-group">
            <label>{{ $t('old_password') }}</label>
            <input type="password" v-model="passwordData.old_password" />
          </div>
          
          <div class="form-group">
            <label>{{ $t('new_password') }}</label>
            <input type="password" v-model="passwordData.new_password" />
          </div>
          
          <div class="form-group">
            <label>{{ $t('confirm_password') }}</label>
            <input type="password" v-model="passwordData.confirm_password" />
          </div>
          
          <div v-if="passwordError" class="error-msg">{{ passwordError }}</div>
          
          <button class="btn-primary" @click="changePassword" :disabled="changingPassword">
            {{ changingPassword ? $t('loading') : $t('change_password') }}
          </button>
        </div>
        
        <div v-if="activeTab === 'business' && user.roles === 2" class="tab-pane">
          <div class="form-group">
            <label>{{ $t('registration_number') }}</label>
            <input type="text" v-model="profile.reg_number" placeholder="LV12345678901" />
          </div>
          
          <div class="form-group">
            <label>{{ $t('address') }}</label>
            <textarea v-model="profile.address" rows="2" :placeholder="$t('address')"></textarea>
          </div>
          
          <div class="info-note">
            <span>ℹ️</span>
            <p>{{ $t('business_info_note') || 'This information will be shown to clients in your profile.' }}</p>
          </div>
          
          <button class="btn-primary" @click="saveProfile" :disabled="saving">
            {{ saving ? $t('loading') : $t('save') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import axios from 'axios';

const props = defineProps({ user: Object });
const emit = defineEmits(['close', 'profile-updated']);

const activeTab = ref('info');
const saving = ref(false);
const changingPassword = ref(false);
const passwordError = ref('');

const profile = reactive({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  phone: '',
  industry: '',
  description: '',
  reg_number: '',
  address: '',
});

const passwordData = reactive({
  old_password: '',
  new_password: '',
  confirm_password: '',
});

const loadProfile = async () => {
  try {
    const { data } = await axios.get('http://127.0.0.1:8080/api/profile/');
    Object.assign(profile, data);
  } catch (e) {
    console.error('Kļūda ielādējot profilu:', e);
  }
};

const saveProfile = async () => {
  saving.value = true;
  try {
    await axios.put('http://127.0.0.1:8080/api/profile/update/', {
      email: profile.email,
      industry: profile.industry,
      description: profile.description,
      first_name: profile.first_name,
      last_name: profile.last_name,
      phone: profile.phone,
      address: profile.address,
      reg_number: profile.reg_number,
    });
    emit('profile-updated');
    alert('Profils veiksmīgi saglabāts!');
  } catch (e) {
    alert('Kļūda saglabājot profilu');
  } finally {
    saving.value = false;
  }
};

const changePassword = async () => {
  if (passwordData.new_password !== passwordData.confirm_password) {
    passwordError.value = 'Jaunās paroles nesakrīt';
    return;
  }
  if (passwordData.new_password.length < 6) {
    passwordError.value = 'Parolei jābūt vismaz 6 rakstzīmēm';
    return;
  }
  
  changingPassword.value = true;
  passwordError.value = '';
  
  try {
    await axios.put('http://127.0.0.1:8080/api/profile/change-password/', {
      old_password: passwordData.old_password,
      new_password: passwordData.new_password,
    });
    alert('Parole veiksmīgi mainīta!');
    passwordData.old_password = '';
    passwordData.new_password = '';
    passwordData.confirm_password = '';
  } catch (e) {
    passwordError.value = e.response?.data?.error || 'Kļūda mainot paroli';
  } finally {
    changingPassword.value = false;
  }
};

onMounted(loadProfile);
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.profile-modal {
  background: #fff;
  border-radius: 20px;
  width: 90%;
  max-width: 500px;
  max-height: 85vh;
  overflow-y: auto;
  position: relative;
  padding: 1.5rem;
}

.modal-close {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  color: #999;
}

.profile-tabs {
  display: flex;
  gap: 0.5rem;
  border-bottom: 1px solid #eee;
  margin-bottom: 1.5rem;
  padding-bottom: 0.5rem;
}

.profile-tabs button {
  background: none;
  border: none;
  padding: 0.5rem 1rem;
  cursor: pointer;
  font-size: 0.9rem;
  color: #666;
  border-radius: 8px;
}

.profile-tabs button.active {
  background: #e8f5e9;
  color: #2e7d32;
  font-weight: 600;
}

.tab-pane {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.form-group label {
  font-size: 0.85rem;
  color: #666;
  font-weight: 500;
}

.form-group input,
.form-group select,
.form-group textarea {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 0.6rem 0.8rem;
  font-size: 0.9rem;
  font-family: inherit;
}

.disabled-input {
  background: #f5f5f5;
  color: #888;
}

.form-row-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.info-note {
  background: #e3f2fd;
  border-radius: 8px;
  padding: 0.75rem;
  display: flex;
  gap: 0.5rem;
  font-size: 0.85rem;
  color: #1565c0;
}

.error-msg {
  color: #e53935;
  font-size: 0.85rem;
}
</style>