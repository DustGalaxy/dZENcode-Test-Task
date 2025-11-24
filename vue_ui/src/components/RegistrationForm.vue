<script setup lang="ts">
import { ref } from "vue";
import { useAuthStore } from "../stores/authStore";
import { useRouter } from "vue-router";

const authStore = useAuthStore();
const router = useRouter();

const username = ref("");
const password = ref("");
const password2 = ref("");
const email = ref("");
const errorMessage = ref("");

async function handleLogin() {
  errorMessage.value = "";

  try {
    await authStore.registration({
      username: username.value,
      password: password.value,
      password2: password2.value,
      email: email.value,
    });

    router.push("/");
  } catch (error) {
    errorMessage.value =
      error instanceof Error ? error.message : "Login failed";
  }
}
</script>

<template>
  <div
    class="max-w-[400px] mx-auto my-8 p-8 border border-gray-200 rounded-lg bg-gray-800"
  >
    <h2 class="text-2xl font-bold mb-6 text-white">Login</h2>

    <form @submit.prevent="handleLogin">
      <div class="mb-4">
        <label for="username" class="block mb-2 font-medium text-gray-200"
          >Username:</label
        >
        <input
          id="username"
          v-model="username"
          type="text"
          required
          :disabled="authStore.isLoading"
          class="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div class="mb-4">
        <label for="email" class="block mb-2 font-medium text-gray-200"
          >Email:</label
        >
        <input
          id="email"
          v-model="email"
          type="email"
          required
          :disabled="authStore.isLoading"
          class="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div class="mb-4">
        <label for="password" class="block mb-2 font-medium text-gray-200"
          >Password:</label
        >
        <input
          id="password"
          v-model="password"
          type="password"
          required
          :disabled="authStore.isLoading"
          class="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div class="mb-4">
        <label for="password2" class="block mb-2 font-medium text-gray-200"
          >Repeat password:</label
        >
        <input
          id="password2"
          v-model="password2"
          type="password"
          required
          :disabled="authStore.isLoading"
          class="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div v-if="errorMessage" class="text-red-600 my-4 p-2 bg-red-50 rounded">
        {{ errorMessage }}
      </div>

      <button
        type="submit"
        :disabled="authStore.isLoading"
        class="w-full p-3 bg-blue-600 text-white rounded cursor-pointer text-base hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
      >
        {{ authStore.isLoading ? "Logging in..." : "Login" }}
      </button>
    </form>
  </div>
</template>
