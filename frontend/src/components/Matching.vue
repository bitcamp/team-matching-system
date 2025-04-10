<template>
  <div class="matching-page">
    <h1>Other Hackers!</h1>
    <div v-if="loading">Loading matches...</div>
    <div v-else-if="error">{{ error }}</div>
    <div v-else-if="matches.length === 0">No matches found.</div>
    <div v-else>
      <TeamCard v-for="(match, index) in matches" :key="index" :match="match" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import { useUserStore } from '../stores/user';
import TeamCard from './TeamCard.vue';

const matches = ref([]);
const loading = ref(true);
const error = ref(null);

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();

const fetchMatches = async () => {
  try {
    // Use the userStore email if logged in; otherwise, use the route param
    const userEmail = userStore.email || route.params.email;

    if (!userEmail) {
      throw new Error(
        'User email not provided. Please log in or provide an email in the URL.'
      );
    }

    // If store.email is defined and does not match the route param, redirect
    if (userStore.email && route.params.email !== userStore.email) {
      router.replace({ name: 'Matches', params: { email: userStore.email } });
      return; // Avoid making the unnecessary request
    }

    const response = await axios.get('/matches.json');
    const allMatches = response.data.matches || {};
    const userMatches = allMatches[userEmail] || [];

    console.log('Fetching matches for:', userEmail);
    console.log('Matches for user:', userMatches);
    matches.value = userMatches;

  } catch (err) {
    console.error('Error fetching matches:', err);
    error.value = `Failed to load matches: ${err.message}`;
  } finally {
    loading.value = false;
  }
};

onMounted(fetchMatches);
</script>

<style scoped>
.matching-page {
  position: relative;
  margin: auto;
  text-align: center;
  padding: 2rem;
}
</style>
