<script setup lang="ts">
import { ref } from "vue";
import { useAuthStore } from "../stores/authStore";

const authStore = useAuthStore();

const username = ref("");
const password = ref("");
const errorMessage = ref("");

async function handleLogin() {
  errorMessage.value = "";

  try {
    await authStore.login({
      username: username.value,
      password: password.value,
    });

    // Успешный логин - можно перенаправить или закрыть форму
    console.log("Login successful!");
  } catch (error) {
    errorMessage.value =
      error instanceof Error ? error.message : "Login failed";
  }
}
</script>

<template>
  <div class="login-form">
    <h2>Login</h2>

    <form @submit.prevent="handleLogin">
      <div class="form-group">
        <label for="username">Username:</label>
        <input
          id="username"
          v-model="username"
          type="text"
          required
          :disabled="authStore.isLoading"
        />
      </div>

      <div class="form-group">
        <label for="password">Password:</label>
        <input
          id="password"
          v-model="password"
          type="password"
          required
          :disabled="authStore.isLoading"
        />
      </div>

      <div v-if="errorMessage" class="error">
        {{ errorMessage }}
      </div>

      <button type="submit" :disabled="authStore.isLoading">
        {{ authStore.isLoading ? "Logging in..." : "Login" }}
      </button>
    </form>
  </div>
</template>

<style scoped>
.login-form {
  max-width: 400px;
  margin: 2rem auto;
  padding: 2rem;
  border: 1px solid #ddd;
  border-radius: 8px;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.form-group input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.error {
  color: red;
  margin: 1rem 0;
  padding: 0.5rem;
  background: #fee;
  border-radius: 4px;
}

button {
  width: 100%;
  padding: 0.75rem;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
}

button:hover:not(:disabled) {
  background: #0056b3;
}

button:disabled {
  background: #ccc;
  cursor: not-allowed;
}
</style>
