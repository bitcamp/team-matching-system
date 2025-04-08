<!-- <template>
    <div class="card-body">
        <h4>Name</h4>
        <p>Email</p>
        <p>Skills:</p>
        <p>Track:</p>
        <p>Skill level:</p>
        <p>Looking for 3 teammates!</p>
        <p>Looking for (kinds of technology)</p>
    </div>
</template>

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
</style> -->

<template>
  <div>
    <div v-if="matches.length === 0">No matches found.</div>
    <div v-for="(match, index) in matches" :key="index" class="card-body">
      <h4>{{ match.first_name }} {{ match.last_name }}</h4>
      <p>{{ match.email }}</p>
      <p>Skills: {{ match.languages.join(', ') }}</p>
      <p>Track: {{ match.track }}</p>
      <p>Skill level: {{ match.skill_level }}</p>
      <p>Looking for {{ match.num_team_members }} teammates!</p>
      <p>Looking for: {{ match.skills_wanted.join(', ') }}</p>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      matches: [],
    };
  },
  async mounted() {
    const email = this.$route.params.email;
    console.log("Viewing matches for:", email);

    const res = await fetch(`http://localhost:5001/matches?email=${email}`);
    const data = await res.json();
    this.matches = data.matches;
  },
};
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