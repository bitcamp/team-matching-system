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

      <div v-if="showProfile" class="profile-container" @click="goToEdit">
        <img :src="ProfileIcon" alt="Profile" class="profile-icon" />
        <span class="profile-label">Profile</span>
      </div>

      <button
        v-if="showLogout"
        @click="logout"
        class="logout-button"
      >
        Logout
      </button>
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

const showProfile = computed(() => route.path.startsWith("/matches"));
const showLogout = computed(() =>
  route.path.startsWith("/matches") || route.path === "/edit-profile"
);

const goToEdit = () => {
  router.push("/edit-profile");
};

const logout = () => {
  localStorage.clear();
  router.push("/login");
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

.logout-button {
  background-color: #ff6b00;
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 8px;
  cursor: pointer;
  font-family: Aleo, sans-serif;
}

.logout-button:hover {
  background-color: #e55d00;
}
</style>