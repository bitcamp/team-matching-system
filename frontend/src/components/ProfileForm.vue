<template>
  <div class="registration-page">
    <h1>
      {{
        props.mode === "edit" ? "Edit Your Profile!" : "Create Your Profile!"
      }}
    </h1>

    <b-form class="registration-form" @submit.prevent="registerUser">
      <b-form-group v-if="mode === 'register'">
          <b-form-group>
            <template #label>
              <span class="required-label">New Username</span>
            </template>
            <b-form-input
              v-model="form.username"
              placeholder="Enter username"
              required
            ></b-form-input>
          </b-form-group>

          <b-form-group>
            <template #label>
              <span class="required-label">New Password</span>
            </template>
            <b-form-input
              v-model="form.password"
              type = "password"
              placeholder="Enter password"
              required
            ></b-form-input>
          </b-form-group>
          <br><br>
      </b-form-group>

      <!-- <b-form-group v-if="mode === 'edit'">
        <template #label>
          <span class="required-label">Are you still looking for a team?</span>
        </template>
        <b-form-radio-group v-model="form.looking" name="looking">
          <b-form-radio value="looking">Yes</b-form-radio>
          <b-form-radio value="inteam">No</b-form-radio>
        </b-form-radio-group>
      </b-form-group> -->


      <b-row>
        <b-col md="6">
          <b-form-group>
            <template #label>
              <span :class="props.mode === 'edit' ? 'unrequired' : 'required-label'">First Name</span>
            </template>
            <b-form-input
              v-model="form.first_name"

              @blur="touched.first_name = true"
              placeholder="Enter first name"
              :required = "props.mode !== 'edit'"
            ></b-form-input>
          </b-form-group>
        </b-col>

        <b-col md="6">
          <b-form-group>
            <template #label>
              <span :class="props.mode === 'edit' ? 'unrequired' : 'required-label'">Last Name</span>
            </template>
            <b-form-input
              v-model="form.last_name"
   
              @blur="touched.last_name = true"
              placeholder="Enter last name"
              :required = "props.mode !== 'edit'"
            ></b-form-input>
          </b-form-group>
        </b-col>
      </b-row>

      <b-form-group>
        <template #label>
          <span :class="props.mode === 'edit' ? 'unrequired' : 'required-label'">Year at Bitcamp</span>
        </template>
        <b-form-input
          type="number"
          v-model="form.year"
    
          @blur="touched.year = true"
          placeholder="Enter year"
          :required = "props.mode !== 'edit'"
        ></b-form-input>
      </b-form-group>

      <b-form-group>
        <template #label>
          <span class="required-label">Contact Email</span>
        </template>
        <b-form-input
          type="email"
          v-model="form.email"
          :state="touched.email ? form.email !== '' : null"
          @blur="touched.email = true"
          placeholder="Enter email"
          required
        ></b-form-input>
      </b-form-group>
      <b-form-group>
        <template #label>
          <span :class="props.mode === 'edit' ? 'unrequired' : 'required-label'">What track are you in?</span>
        </template>
        <b-form-radio-group v-model="form.track" name="track" stacked>
          <b-form-radio value="general">General</b-form-radio>
          <b-form-radio value="quantum">Quantum</b-form-radio>
          <b-form-radio value="cybersecurity">Cybersecurity</b-form-radio>
          <b-form-radio value="ml">Machine Learning</b-form-radio>
          <b-form-radio value="app dev">App Development</b-form-radio>
        </b-form-radio-group>
      </b-form-group>

      <h4 class="header">Skills & Experience</h4>
      <div class="section-divider"></div>
      <b-form-group
        label="Have you participated in a hackathon before?"
        label-cols="5"
        label-class="required-label"
        label-for="hackathon"
      >
        <b-form-radio-group
          id="hackathon"
          v-model="form.hackathon"
          name="hackathon"
          class="d-flex gap-3"
        >
          <b-form-radio value="yes">Yes</b-form-radio>
          <b-form-radio value="no">No</b-form-radio>
        </b-form-radio-group>
      </b-form-group>

      <b-form-group>
        <template #label>
          <span :class="props.mode === 'edit' ? 'unrequired' : 'required-label'"
            >What programming languages and frameworks are you comfortable
            with?</span
          >
        </template>
        <b-form-checkbox-group v-model="form.languages" stacked>
          <b-form-checkbox value="html/css">HTML/CSS</b-form-checkbox>
          <b-form-checkbox value="javascript">Javascript</b-form-checkbox>
          <b-form-checkbox value="react/vue">React/Vue</b-form-checkbox>
          <b-form-checkbox value="python">Python</b-form-checkbox>
          <b-form-checkbox value="sql">SQL</b-form-checkbox>
          <b-form-checkbox value="flask">Flask</b-form-checkbox>
          <b-form-checkbox value="java">Java</b-form-checkbox>
        </b-form-checkbox-group>
      </b-form-group>

      <b-form-group>
        <template #label>
          <span :class="props.mode === 'edit' ? 'unrequired' : 'required-label'">What is your experience level?</span>
        </template>
        <b-form-radio-group v-model="form.experience" name="experience" stacked>
          <b-form-radio value="beginner"
            >Beginner (skill level 1-2)</b-form-radio
          >
          <b-form-radio value="inter"
            >Intermediate (skill level 3-4)</b-form-radio
          >
          <b-form-radio value="advanced">Advanced (skill level 5)</b-form-radio>
        </b-form-radio-group>
      </b-form-group>

      <b-form-group>
        <template #label>
          <span :class="props.mode === 'edit' ? 'unrequired' : 'required-label'"
            >Do you prefer working with someone with a similar skill
            level?</span
          >
        </template>
        <b-form-radio-group v-model="form.skill_level" name="skill-level">
          <b-form-radio value="yes">Yes</b-form-radio>
          <b-form-radio value="no">No</b-form-radio>
          <b-form-radio value="idc">Don't Care</b-form-radio>
        </b-form-radio-group>
      </b-form-group>

      <b-form-group>
        <template #label>
          <span :class="props.mode === 'edit' ? 'unrequired' : 'required-label'"
            >What kind of technologies do you want your teammates to have
            knowledge of?</span
          >
        </template>
        <b-form-checkbox-group v-model="form.skills_wanted" stacked>
          <b-form-checkbox value="html/css">HTML/CSS</b-form-checkbox>
          <b-form-checkbox value="javascript">Javascript</b-form-checkbox>
          <b-form-checkbox value="react/vue">React/Vue</b-form-checkbox>
          <b-form-checkbox value="python">Python</b-form-checkbox>
          <b-form-checkbox value="sql">SQL</b-form-checkbox>
          <b-form-checkbox value="flask">Flask</b-form-checkbox>
          <b-form-checkbox value="java">Java</b-form-checkbox>
        </b-form-checkbox-group>
      </b-form-group>

      <h4 class="header">Interests & Project Preferences</h4>
      <div class="section-divider"></div>
      <b-form-group>
        <template #label>
          <span :class="props.mode === 'edit' ? 'unrequired' : 'required-label'"
            >What kind of projects are you interested in (i.e. web, mobile, AI,
            etc.)?</span
          >
        </template>
        <b-form-checkbox-group v-model="form.projects" stacked>
          <b-form-checkbox value="web_dev">Web Development</b-form-checkbox>
          <b-form-checkbox value="mobile_app">Mobile App</b-form-checkbox>
          <b-form-checkbox value="ai/ml">AI/ML</b-form-checkbox>
        </b-form-checkbox-group>
      </b-form-group>

      <b-form-group>
        <template #label>
          <span :class="props.mode === 'edit' ? 'unrequired' : 'required-label'"
            >What Bitcamp prizes are you interested in catering your project
            towards?</span
          >
        </template>
        <b-form-checkbox-group v-model="form.prizes" stacked>
          <b-form-checkbox value="hardware">Best Hardware Hack</b-form-checkbox>
          <b-form-checkbox value="bitcamp">Best Bitcamp Hack</b-form-checkbox>
          <b-form-checkbox value="first_time">Best First Time Hack</b-form-checkbox>
          <b-form-checkbox value="ui/ux">Best UI/UX Hack</b-form-checkbox>
          <b-form-checkbox value="moonshot">Best Moonshot Hack</b-form-checkbox>
          <b-form-checkbox value="razzle_dazzle">Best Razzle Dazzle Hack</b-form-checkbox>
          <b-form-checkbox value="social_good">Best Social Good Hack</b-form-checkbox>
          <b-form-checkbox value="gamification">Best Gamification Hack</b-form-checkbox>
          <b-form-checkbox value="peoples_choice">People's Choice Hack</b-form-checkbox>
          <b-form-checkbox value="sustainability">Best Sustainability Hack</b-form-checkbox>
          <b-form-checkbox value="no_pref">No Preference</b-form-checkbox>
        </b-form-checkbox-group>
      </b-form-group>

      <h4 class="header">Working Preferences</h4>
      <div class="section-divider"></div>
      <b-form-group>
        <template #label>
          <span :class="props.mode === 'edit' ? 'unrequired' : 'required-label'">How serious are you?</span>
        </template>
        <b-form-radio-group v-model="form.serious" name="serious">
          <b-form-radio value="win">I want to win! (16-20 hours)</b-form-radio>
          <b-form-radio value="funsies"
            >I'm just doing this for fun (9-13 hours)</b-form-radio
          >
          <b-form-radio value="learning"
            >I want to learn, if I win that will be a plus (1-8
            hours)</b-form-radio
          >
        </b-form-radio-group>
      </b-form-group>

      <b-form-group>
        <template #label>
          <span :class="props.mode === 'edit' ? 'unrequired' : 'required-label'"
            >Which way would you prefer collaborating with your team?</span
          >
        </template>
        <b-form-checkbox-group v-model="form.collab" stacked>
          <b-form-checkbox value="remote">Remote</b-form-checkbox>
          <b-form-checkbox value="hybrid">Hybrid</b-form-checkbox>
          <b-form-checkbox value="in-person">In Person</b-form-checkbox>
        </b-form-checkbox-group>
      </b-form-group>

      <b-form-group>
        <template #label>
          <span class="props.mode === 'edit' ? 'unrequired' : 'required-label'"
            >How many team members do you already have?</span
          >
        </template>
        <b-form-radio-group v-model="form.num_team_members" name="team-members">
          <b-form-radio value="one">1</b-form-radio>
          <b-form-radio value="two">2</b-form-radio>
          <b-form-radio value="three">3</b-form-radio>
        </b-form-radio-group>
      </b-form-group>

      <div class="submit-wrapper">
        <b-button type="submit" variant="primary" class="submit-button">
          {{ mode === "edit" ? "Save" : "Submit" }}
        </b-button>
      </div>
    </b-form>
    <b-button
      variant="danger"
      class="delete-button"
      @click="deleteProfile"
      v-if="mode === 'edit'"
    >
      Delete My Profile
    </b-button>
  </div>
</template>

<script setup>
import { ref, reactive } from "vue";
import { useRouter } from "vue-router";
import axios from "axios";
import generalMixin from "../mixins/general.js";
import { useUserStore } from "../stores/user.js"; // Add this import

const router = useRouter();
const userStore = useUserStore(); // Add this to use the store

const touched = reactive({
  first_name: false,
  last_name: false,
  year: false,
  email: false,
});

const form = reactive({
  id: "",
  first_name: "",
  last_name: "",
  year: "",
  email: "",
  track: "",
  hackathon: null,
  languages: [],
  experience: "",
  skill_level: "",
  skills_wanted: [],
  projects: [],
  prizes: [],
  serious: "",
  collab: [],
  num_team_members: "",
  username: "",
  password: ""
});

const registerUser = async () => {
  try {
    const backendEndpoint = generalMixin.methods.getEnvVariable("BACKEND_ENDPOINT");
    const env = generalMixin.methods.getCurrentEnvironment();
    const url = `${backendEndpoint}/${env}/register`;

    console.log("Posting to:", url);
    const response = await axios.post(url, form);

    // Assuming the backend returns the email in the response
    const userEmail = response.data.email || form.email; // Fallback to form.email if not returned

    if (!userEmail) {
      throw new Error("No email returned from backend or form");
    }

    // Store the email in Pinia
    userStore.setUserEmail(userEmail);

    alert("Registration Successful!");
    console.log("Response:", response.data);

    // Redirect to matches page with email parameter
    router.push({ name: "Matches", params: { email: userEmail } });
  } catch (error) {
    alert("Error registering user");
    console.error(
      "Registration failed:",
      error.response?.data || error.message || error
    );
  }
};

const deleteProfile = async () => {
  const confirmDelete = confirm(
    "Are you sure you want to delete your profile?"
  );
  if (!confirmDelete) return;

  try {
    const backendEndpoint = generalMixin.methods.getEnvVariable("BACKEND_ENDPOINT");
    const env = generalMixin.methods.getCurrentEnvironment();
    const url = `${backendEndpoint}/${env}/delete`;

    await axios.delete(url, {
      data: {
        id: form.email,
      },
    });

    alert("Profile deleted successfully.");
    router.push("/login");
  } catch (error) {
    alert("Error deleting profile");
    console.error(
      "Deletion failed:",
      error.response?.data || error.message || error
    );
  }
};

const props = defineProps({
  mode: {
    type: String,
    default: "register",
  },
});
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

.unrequired{
  font-size: var(--bitcamp-fontsize-body);
  font-family: var(--bitcamp-font-title);
  margin-right: 4px;

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

.submit-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 2rem;
}

.submit-button {
  background-color: var(--light-orange);
  color: white;
  padding: 14px 10rem;
  margin-top: 2rem;
  margin-bottom: 5rem;
  font-size: 1.25rem;
  font-family: var(--bitcamp-font-title);
  border: none;
  border-radius: 15px;
  transition: background-color 0.3s ease;
}

.submit-button:hover {
  background-color: var(--mango-orange);
}

.section-divider {
  height: 2px;
  background-color: #ffeac7;
  margin: 0.5rem auto 1.5rem;
  border-radius: 2px;
}

.header {
  margin-top: 4rem;
}
</style>