<template>
    <div class="registration-page">
      <h1>Login</h1>
  
      <b-form class="registration-form" @submit.prevent="registerUser">
            <b-form-group>
              <template #label>
                <span class="required-label">Username</span>
              </template>
              <b-form-input
                v-model="form.username_name"
                required
              ></b-form-input>
            </b-form-group>

        <b-form-group>
          <template #label>
            <span class="required-label">Password</span>
          </template>
          <b-form-input
            v-model="form.password"
            required
          ></b-form-input>
        </b-form-group>
        
        <div class = "alternative">
            <h5 class><span style="color: white;">or</span></h5>
            <h5>Don't have an account?</h5>
            <b-button type="submit" variant="primary">Sign Up</b-button>
        </div>
      </b-form>
    </div>
  </template>
  
  <script setup>
  import { ref } from "vue";
  
  const form = ref({
    first_name: "",
    last_name: "",
    year: "",
    email: "",
  });
  
  const registerUser = () => {
    console.log("User Registered:", form.value);
  };
  
  </script>
  
  <style scoped>
  .registration-page {
    margin: auto;
    text-align: center;
    align-content: center;
  }
  
  .registration-form {
    width: 100%;
    max-width: 350px;
    margin: auto;
    text-align: left;
  }
  .b-form-group {
    margin-bottom: 20px;
  }
  
  .required-label::before {
    content: "*";
    color: red;
    margin-right: 4px;
    font-weight: bold;
  }
  
  .b-form-input {
    width: 100%;
    padding: 10px;
    border: none;
    border-radius: 5px;
  }
  
  .alternative {
    display: flex;             
    flex-direction: column;    
    justify-content: center;   
    align-items: center;       
    margin-top: 20px;
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
    border:none;
    padding: 5px 30px;
    border-radius: 10px;
    font-family: "Aleo", sans-serif;
    font-weight: 500;
    font-size: 1.2rem;
  }
  
  button:hover {
    background-color: var(--mango-orange);
  }
  </style>
  