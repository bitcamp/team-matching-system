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
        <span class="instructions-link" @mouseenter="showInstructions = true" @mouseleave = "showInstructions = false">ⓘ</span>
        <Instructions v-if="showInstructions" class="popup" />

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
import Instructions from './Instructions.vue';
import { ref } from 'vue';

const route = useRoute();
const router = useRouter();

const isMatchingPage = computed(() => route.path === "/app");

const goToEdit = () => {
  router.push("/edit-profile");
};

const showInstructions = ref(false);

</script>

<style scoped>
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
  color:#FF6B00
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
