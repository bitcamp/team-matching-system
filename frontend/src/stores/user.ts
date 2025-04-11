export const useUserStore = defineStore('user', {
  state: () => ({
    email: null as string | null,
  }),
  actions: {
    setUserEmail(email: string) {
      this.email = email;
    },
    clearUser() {
      this.email = null;
    },
  },
});
