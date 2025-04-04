import Axios from "axios";
import Config from "../config/general";

export default {
  methods: {
    sleep(ms) {
      return new Promise((resolve) => setTimeout(resolve, ms));
    },
    async performGetRequest(baseUrl, endpoint) {
      const stage = this.getCurrentEnvironment();
      try {
        const result = await Axios.get(`${baseUrl}/${stage}/${endpoint}`);
        return result.data;
      } catch (e) {
        console.error(e);
        return null;
      }
    },
    async performPostRequest(baseUrl, endpoint, params) {
      const stage = this.getCurrentEnvironment();
      try {
        console.log("PARAMS:");
        console.log(params);
        const result = await Axios.post(`${baseUrl}/${stage}/${endpoint}`, params);
        console.log("RESULT");
        console.log(result.data);
        return result.data;
      } catch (e) {
        console.error(e);
        return null;
      }
    },
    async performRawPostRequest(endpoint, params) {
      try {
        const result = await Axios.put(endpoint, params, {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        });
        return result;
      } catch (e) {
        console.error(e);
        return null;
      }
    },
    getCurrentEnvironment() {
      if (
        window.location.hostname === "register.bit.camp" ||
        window.location.hostname === "www.register.bit.camp"
      ) {
        return "prd";
      }
      if (window.location.hostname === "beta.register.bit.camp") {
        return "stg";
      }
      return "dev";
    },
    getEnvVariable(variableName) {
      if (Config.shared && Config.shared[variableName]) {
        return Config.shared[variableName];
      }
      const envConfig = Config[this.getCurrentEnvironment()];
      if (!envConfig || !envConfig[variableName]) {
        console.warn(`Environment variable ${variableName} not found for ${this.getCurrentEnvironment()}. Using default.`);
        return Config.dev[variableName]; // Fallback to dev
      }
      return envConfig[variableName];
    },
  },
};
