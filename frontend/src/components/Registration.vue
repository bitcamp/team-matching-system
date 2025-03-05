<template>
    <div class="registration-page">
      <h1>Register for Bitcamp</h1>
      <p>Sign up below to participate in the event!</p>
      
      <b-form class="registration-form" @submit.prevent="registerUser">
        <b-form-group label="First Name">
          <b-form-input v-model="form.first_name" placeholder="Enter first name" required></b-form-input>
        </b-form-group>
  
        <b-form-group label="Last Name">
          <b-form-input v-model="form.last_name" placeholder="Enter last name" required></b-form-input>
        </b-form-group>
  
        <b-form-group label="Email Address">
          <b-form-input type="email" v-model="form.email" placeholder="Enter email" required></b-form-input>
        </b-form-group>
  
        <b-button type="submit" variant="primary">Register</b-button>
      </b-form>
    </div>
  </template>
  
  <script setup>
  import { ref } from "vue";
  
  const form = ref({
    first_name: "",
    last_name: "",
    email: "",
  });
  
  const registerUser = () => {
    console.log("User Registered:", form.value);
  };
  </script>
  
  <style scoped>
  .registration-page {
    max-width: 600px;
    margin: auto;
    background: rgba(255, 255, 255, 0.9);
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0px 0px 16px rgba(0, 0, 0, 0.125);
  }
  
  h1 {
    color: var(--black);
    font-family: var(--bitcamp-font-title);
  }
  
  p {
    font-size: var(--bitcamp-fontsize-body);
    color: var(--asphalt-grey);
  }
  
  button {
    background-color: var(--light-orange);
    color: white;
  }
  
  button:hover {
    background-color: var(--mango-orange);
  }
  </style>
  