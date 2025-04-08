<!-- <template>
    <div class="matching-page">
        <h1>Other Hackers!</h1>
        <TeamCard /><TeamCard /><TeamCard /><TeamCard /><TeamCard /><TeamCard />
    </div>

</template>

<script setup>
import TeamCard from "./TeamCard.vue";
</script>

<style scoped>
.matching-page {
  margin: auto;
  text-align: center;
  align-content: center;
}
</style> -->

<template>
  <div class="matching-page">
    <!-- Profile Image Icon -->
    <!-- <img
      class="profile-icon"
      src="../assets/icon.svg"
      alt="Profile"
      @click="goToEdit"
    /> -->

    <h1>Other Hackers!</h1>
    <TeamCard />
    <TeamCard />
    <TeamCard />
    <TeamCard />
    <TeamCard />
    <TeamCard />
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import TeamCard from "./TeamCard.vue"

const router = useRouter()

const goToEdit = () => {
  router.push('/edit-profile')
}
</script>

<style scoped>
.matching-page {
  position: relative;
  margin: auto;
  text-align: center;
  padding: 2rem;
}

.profile-icon {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: 50%;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.profile-icon:hover {
  transform: scale(1.1);
}
</style>

