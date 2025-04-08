import { createRouter, createWebHistory } from 'vue-router'
import Login from '../components/Login.vue'
import ProfileForm from '../components/ProfileForm.vue'
import Matching from '../components/Matching.vue'
import EditProfile from '../views/EditProfile.vue' 


const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: Login },
  { path: '/create-profile', component: ProfileForm },
  { path: '/app', component: Matching },
  { path: '/edit-profile', component: EditProfile },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router