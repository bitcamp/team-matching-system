<template>
  <div class="navbar">
    <img :src="Logo" alt="Bitcamp Logo" class="logo" />

    <div class="navbar-right">
      <span
        class="instructions-link"
        @mouseenter="showInstructions = true"
        @mouseleave="showInstructions = false"
      >
        ⓘ
      </span>
      <Instructions v-if="showInstructions" class="popup" />

      <div v-if="isMatchingPage" class="profile-container" @click="goToEdit">
        <img :src="ProfileIcon" alt="Profile" class="profile-icon" />
        <span class="profile-label">Profile</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import Logo from "../assets/Logo.svg";
import ProfileIcon from "../assets/icon.svg";
import Instructions from "./Instructions.vue";

const route = useRoute();
const router = useRouter();

const isMatchingPage = computed(() => route.path === "/app");

const goToEdit = () => {
  router.push("/edit-profile");
};

const showInstructions = ref(false);
</script>

<style scoped>
.navbar {
  background-color: #7f6c5f;
  padding: 10px 20px;
  margin-bottom: 50px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  min-height: 70px;
}

.navbar-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.instructions-link {
  cursor: pointer;
  font-size: 24px;
  font-family: Aleo, sans-serif;
  transition: text-decoration 0.2s ease;
  color: white;
}

.instructions-link:hover {
  color: #ff6b00;
}

.profile-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  color: white;
  font-family: Aleo, sans-serif;
  min-width: 50px;
}

.profile-icon {
  width: 60px;
  height: 60px;
}

.profile-label {
  font-size: 14px;
  margin-top: 4px;
}
</style>
