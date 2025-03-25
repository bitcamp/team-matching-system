<template>
  <div>
    <NavBar />
    <!-- <Login /> -->
    <Registration />
  </div>
</template>

<script setup>
import Registration from "./components/ProfileForm.vue";
import Login from "./components/Login.vue";
import NavBar from "./components/NavBar.vue";
</script>
