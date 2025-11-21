<script setup lang="ts">
import { RouterLink } from "vue-router";
import { useAuthStore } from "../stores/authStore";

const authStore = useAuthStore();
</script>

<template>
  <header
    class="bg-gray-800 text-white p-4 flex justify-between items-center relative"
  >
    <h1 class="text-2xl font-bold">Comments App</h1>

    <div v-if="authStore.isAuthenticated" class="flex items-center gap-4">
      <span>Welcome, {{ authStore.user?.username }}!</span>
      <button
        @click="authStore.logout"
        class="px-4 py-2 bg-red-600 hover:bg-red-700 rounded transition-colors cursor-pointer border-none text-sm disabled:opacity-50 disabled:cursor-not-allowed"
      >
        Logout
      </button>
    </div>

    <div v-else class="flex gap-4">
      <RouterLink to="/login" class="hover:text-gray-300 transition-colors"
        >Login</RouterLink
      >
      <RouterLink to="/register" class="hover:text-gray-300 transition-colors">
        Register
      </RouterLink>
    </div>

    <!-- Индикатор загрузки -->
    <div
      v-if="authStore.isLoading"
      class="absolute top-0 left-0 right-0 h-1 bg-blue-500 animate-pulse"
    ></div>

    <!-- Сообщение об ошибке -->
    <div
      v-if="authStore.error"
      class="absolute top-full left-0 right-0 bg-red-500 text-white p-2 text-center"
    >
      {{ authStore.error }}
    </div>
  </header>
</template>
