<template>
  <div class="registration-page">
    <h1>Login</h1>

    <b-form class="registration-form" @submit.prevent="loginUser" ref="loginForm">
      <b-form-group>
        <template #label>
          <span class="required-label">Username</span>
        </template>
        <b-form-input v-model="form.username_name" required></b-form-input>
      </b-form-group>

      <b-form-group>
        <template #label>
          <span class="required-label">Password</span>
        </template>
        <b-form-input v-model="form.password" type="password" required></b-form-input>
      </b-form-group>

      <div class="login-button-wrapper">
        <b-button type="submit" variant="primary">Login</b-button>
      </div>
    </b-form>

    <div class="alternative">
      <h5><span style="color: white">or</span></h5>
      <h5>Don't have an account?</h5>
      <b-button variant="primary" @click="goToSignup">Sign Up</b-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import axios, { AxiosError } from "axios";
// @ts-ignore
import generalMixin from "../mixins/general.js";
import { useUserStore } from "../stores/user.js";

const router = useRouter();
const userStore = useUserStore();
const loginForm = ref<HTMLFormElement | null>(null);
const rawFormEl = ref<HTMLFormElement | null>(null);

onMounted(() => {
  rawFormEl.value = loginForm.value?.$el ?? null;
});

const form = ref({
  username_name: "",
  password: "",
});

const loginUser = async () => {
  try {
    const backendEndpoint = generalMixin.methods.getEnvVariable("VITE_BACKEND_ENDPOINT");
    const env = generalMixin.methods.getCurrentEnvironment();
    const url = `${backendEndpoint}/${env}/login`;

    // Send the username and password to the backend
    const response = await axios.post(url, {
      username: form.value.username_name,
      password: form.value.password,
    });

    console.log("Backend response:", response.data);
    // IMPORTANT: We expect the backend to return the user's email:
    // e.g. response.data = { username: "agijare", email: "agijare@123" }
    const userEmail = response.data.email;

    // If the backend did NOT return an email, throw an error:
    if (!userEmail) {
      throw new Error("Backend did not return an email. Cannot route to matches.");
    }

    // Store the email in Pinia
    userStore.setUserEmail(userEmail);

    alert("Login successful!");

    // Redirect to /matches/:email
    router.push({ name: "Matches", params: { email: userEmail } });
  } catch (err: unknown) {
    const error = err as AxiosError;

    if (error.response) {
      const data = error.response.data as { error: string };
      alert(data.error);
    } else {
      alert("Network error — please try again.");
    }

    console.error("Login error:", error);
  }
};

const goToSignup = () => {
  router.push("/create-profile");
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

.login-button-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 10px;
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
  border: none;
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
