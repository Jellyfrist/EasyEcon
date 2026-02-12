import { createRouter, createWebHistory } from 'vue-router';
import Home from '../components/HelloWorld.vue'; // Replace with your desired home component
import Phonebook from '../components/Phonebook.vue';
import Contact from "../components/Contact.vue";
import Login from '../views/Login.vue';

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/phonebook', name: 'Phonebook', component: Phonebook },
  { path: "/contacts", name: "Contact", component: Contact },
  { path: '/login', component: Login },
  { path: "/login-success", component: Login }, // Handles token parsing




];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;