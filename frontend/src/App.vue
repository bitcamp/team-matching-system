<!-- <template>
  <div>
    <NavBar />
    <Matching />
    <Login />
    <Registration />
  </div>
</template>

<script setup>
import Registration from "./components/ProfileForm.vue";
import Login from "./components/Login.vue";
import NavBar from "./components/NavBar.vue";
import Matching from "./components/Matching.vue";
</script> -->

<template>
  <div>
    <NavBar />
    <router-view />
  </div>
</template>

<script setup lang="ts">
import NavBar from "./components/NavBar.vue";
</script>
