<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script>
import { onMounted } from 'vue'
import { useStore } from 'vuex'

export default {
  name: 'App',
  setup() {
    const store = useStore()
    
    onMounted(async () => {
      if (store.getters['auth/isLoggedIn'] && !store.getters['auth/user']) {
        try {
          await store.dispatch('auth/fetchProfile')
        } catch (err) {
          console.error('Failed to fetch user profile on load', err)
        }
      }
    })
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>