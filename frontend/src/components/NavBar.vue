<!-- <template>
    <div>
        <img :src="Logo" alt="Bitcamp Logo">
    </div>
</template>

<script setup>
    import Logo from "../assets/Logo.svg";
</script>

<style scoped>
    div {
        background-color:#7F6C5F;
        padding:10px;
        margin-bottom: 50px;
    }
</style> -->

<template>
    <div class="navbar">
      <img :src="Logo" alt="Bitcamp Logo" class="logo" />
  
      <div class="navbar-right">
        <span class="instructions-link" @click="goToInstructions">Instructions</span>
  
        <img
          v-if="isMatchingPage"
          :src="ProfileIcon"
          alt="Profile"
          class="profile-icon"
          @click="goToEdit"
        />
      </div>
    </div>
  </template>
  
<script setup>
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import Logo from "../assets/Logo.svg";
import ProfileIcon from "../assets/icon.svg"; // ✅ make sure this file exists

const route = useRoute();
const router = useRouter();

const isMatchingPage = computed(() => route.path === "/app");

const goToEdit = () => {
  router.push("/edit-profile");
};

const goToInstructions = () => {
  router.push("/instructions");
};

</script>

<style scoped>
.navbar-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.instructions-link {
  color: white;
  cursor: pointer;
  font-size: 18px;
  font-family: Aleo, sans-serif;
  transition: text-decoration 0.2s ease;
  color: #FF6B00;
}

.instructions-link:hover {
  text-decoration: underline;
}

.navbar {
  background-color: #7F6C5F;
  padding: 10px 20px;
  margin-bottom: 50px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  min-height: 70px;
}</style>
