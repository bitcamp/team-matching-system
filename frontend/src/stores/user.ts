import { defineStore } from 'pinia';

export const useUserStore = defineStore('user', {
  state: () => ({
    email
  }),
  actions: {
    setUserEmail(email: any) {
      this.email = email;
    },
    clearUser() {
      this.email = null;
    },
  },
});
