import { createApp } from "vue";
import App from "./App.vue";
import { BButton, BForm, BFormInput, BFormGroup } from "bootstrap-vue-next";
import "bootstrap/dist/css/bootstrap.css";
import "bootstrap-vue-next/dist/bootstrap-vue-next.css";
import "./assets/global.css";

const app = createApp(App);

app.component("BButton", BButton);
app.component("BForm", BForm);
app.component("BFormInput", BFormInput);
app.component("BFormGroup", BFormGroup);

app.mount("#app");