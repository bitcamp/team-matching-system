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

    <img
      v-if="isMatchingPage"
      :src="ProfileIcon"
      alt="Profile"
      class="profile-icon"
      @click="goToEdit"
    />
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
</script>

<style scoped>
.navbar {
  background-color: #7F6C5F;
  padding: 10px 20px;
  margin-bottom: 50px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  min-height: 70px;
}

.logo {
  height: 80px;
}

.profile-icon {
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
