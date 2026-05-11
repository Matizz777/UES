<template>
  <!-- Catalog -->
  <ProviderCatalog
    v-if="activeTab === 'main' && !showBooking"
    @start-booking="onStartBooking"
  />

  <!-- Booking wizard -->
  <BookingWizard
    v-if="showBooking"
    :provider="selectedProvider"
    :service-name="pendingService"
    @done="showBooking = false"
    @cancel="showBooking = false"
  />

  <!-- My reservations -->
  <ReservationList
    v-if="activeTab === 'my-bookings'"
    :user="user"
  />
</template>

<script setup>
import { ref } from 'vue';
import ProviderCatalog from './ProviderCatalog.vue';
import BookingWizard   from './BookingWizard.vue';
import ReservationList from './ReservationList.vue';

defineProps({ user: Object, activeTab: String });

const showBooking      = ref(false);
const selectedProvider = ref(null);
const pendingService   = ref('');

const onStartBooking = ({ provider, service }) => {
  selectedProvider.value = provider;
  pendingService.value   = service.name;
  showBooking.value      = true;
};
</script>
