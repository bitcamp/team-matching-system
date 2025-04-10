<template>
  <div class="matching-page">
    <h1>Other Hackers!</h1>

    <div v-if="matches">
      <div v-for="(teamMatches, teamName) in matches" :key="teamName" class="team-section">
        <h2>{{ teamName }}'s Top Matches</h2>
        <div class="team-matches">
          <TeamCard
            v-for="match in teamMatches"
            :key="match.email"
            :name="match.name"
            :email="match.email"
            :score="match.score"
            :info="match.info"
          />
        </div>
      </div>
    </div>

    <div v-else>
      <p>Loading matches...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import TeamCard from "./TeamCard.vue"

const matches = ref(null)

onMounted(async () => {
  try {
    const res = await fetch('https://akayuoljek.execute-api.us-east-1.amazonaws.com/dev/match-teams');

    if (!res.ok) {
      throw new Error(`Server responded with ${res.status}`);
    }

    const data = await res.json();
    matches.value = data.matches;
  } catch (err) {
    console.error("Failed to fetch matches:", err.message);
  }
});

</script>

<style scoped>
.matching-page {
  margin: auto;
  text-align: center;
  padding: 2rem;
}

.team-section {
  margin-bottom: 3rem;
}

.team-matches {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 1rem;
}
</style>
