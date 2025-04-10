// src/stores/user.js
import { defineStore } from 'pinia';

export const useUserStore = defineStore('user', {
  state: () => ({
    email: null, // Store the logged-in user's email
  }),
  actions: {
    setUserEmail(email) {
      this.email = email;
    },
    clearUser() {
      this.email = null;
    },
  },
});
