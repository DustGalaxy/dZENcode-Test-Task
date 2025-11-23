<script setup lang="ts">
import { onMounted } from "vue";
import { useAuthStore } from "./stores/authStore";
import Header from "./components/Header.vue";

const authStore = useAuthStore();

onMounted(async () => {
  await authStore.initialize();
});
</script>

<template>
  <div id="app">
    <Header />
    <main class="bg-[#222222] text-white">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

main {
  flex: 1;
  padding: 2rem;
}
</style>
