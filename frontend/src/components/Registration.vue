<template>
  <div class="registration-page">
    <h1>Create Your Profile!</h1>

    <b-form class="registration-form" @submit.prevent="registerUser">
      <b-row>
        <b-col md="6">
          <b-form-group>
            <template #label>
              <span class="required-label">First Name</span>
            </template>
            <b-form-input
              v-model="form.first_name"
              placeholder="Enter first name"
              required
            ></b-form-input>
          </b-form-group>
        </b-col>

        <b-col md="6">
          <b-form-group>
            <template #label>
              <span class="required-label">Last Name</span>
            </template>
            <b-form-input
              v-model="form.last_name"
              placeholder="Enter last name"
              required
            ></b-form-input>
          </b-form-group>
        </b-col>
      </b-row>

      <b-form-group>
        <template #label>
          <span class="required-label">Year at Bitcamp</span>
        </template>
        <b-form-input
          type="number"
          v-model="form.year"
          placeholder="Enter year"
          required
        ></b-form-input>
      </b-form-group>

      <b-form-group>
        <template #label>
          <span class="required-label">Contact Email</span>
        </template>
        <b-form-input
          type="email"
          v-model="form.email"
          placeholder="Enter email"
          required
        ></b-form-input>
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
}

.registration-form {
  width: 100%;
  max-width: 1000px;
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
  border: 1px solid #ccc;
  border-radius: 5px;
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
