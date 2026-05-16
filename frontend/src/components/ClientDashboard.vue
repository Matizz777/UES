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
    :service="selectedService"
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
const selectedService  = ref(null);

const onStartBooking = ({ provider, service }) => {
  selectedProvider.value = provider;
  selectedService.value  = service;
  showBooking.value      = true;
};
</script>