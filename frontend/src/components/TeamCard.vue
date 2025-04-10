<template>
  <div class="card-body">
    <h4>{{ info.name }}</h4>
    <p>{{ info.email }}</p>
    <p>Skills: {{ info.skills.join(', ') }}</p>
    <p>Track: {{ info.primary_track }}</p>
    <p>Skill level: {{ info.avg_skill_level }}</p>
    <p>Looking for {{ info.team_size }} teammates!</p>
    <p>Looking for: {{ info.skills_wanted.join(', ') }}</p>
    <p>Score: {{ score.toFixed(2) }}</p>
  </div>
</template>

<script setup>
defineProps({
  info: Object,
  score: Number
})
</script>

<style scoped>
.card-body {
  text-align: center;
  align-content: center;
  width: 400px;
  background-color: white;
  border-radius: 10px;
  padding: 30px;
  text-align: left;
  margin: 30px 20px;
  display: inline-block;
  box-shadow: 0 6px 4px 0 rgba(0, 0, 0, 0.2);
  transition: box-shadow 0.3s ease, transform 0.3s ease;
}

.card-body:hover {
  box-shadow: 0 12px 16px 0 rgba(0, 0, 0, 0.3);
  transform: translateY(-10px);
}
</style>
