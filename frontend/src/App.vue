<script setup>
</script>
<template>
  <div>
    <!-- <a href="https://vite.dev" target="_blank">
      <img src="/vite.svg" class="logo" alt="Vite logo" />
    </a>
    <a href="https://vuejs.org/" target="_blank">
      <img src="./assets/vue.svg" class="logo vue" alt="Vue logo" />
    </a> -->
    <nav class="navbar">
      <router-link to="/">Home</router-link> |
      <router-link to="/login">Google SSO</router-link> |
      <router-link to="/phonebook">Phonebook</router-link> |
      <router-link to="/contacts">Contacts</router-link>
    </nav>
    <!-- Render the appropriate component for the current route -->
    <router-view />
  </div>
</template>
<style>
* {
  font-family: 'Kanit', sans-serif;
}
</style>
<style scoped>
nav {
  margin-top: 1em;
}

.logo {
  height: 6em;
  padding: 1.5em;
  will-change: filter;
  transition: filter 300ms;
}

.logo:hover {
  filter: drop-shadow(0 0 2em #646cffaa);
}

.logo.vue:hover {
  filter: drop-shadow(0 0 2em #42b883aa);
}
</style>