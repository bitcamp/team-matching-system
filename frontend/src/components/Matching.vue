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
import { useRoute } from 'vue-router';
import axios from 'axios';
import TeamCard from './TeamCard.vue';

const matches = ref([]);
const loading = ref(true);
const error = ref(null);

// run algo every time
// run something like this http://localhost:5173/matches/ivorytea.leaf@gmail.com to make it work
const fetchMatches = async () => {
  try {
    const route = useRoute();
    const userEmail = route.params.email; // make this dynamic so that you don't have to put in the route everywhere

    if (!userEmail) {
      throw new Error('User email not provided');
    }

    // Fetch from public folder
    const response = await axios.get('/matches.json');
    const allMatches = response.data.matches;
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