<script setup lang="ts">
import LoginForm from "../components/LoginForm.vue";
</script>

<template>
  <div class="login-page">
    <LoginForm />
  </div>
</template>

<style scoped>
.login-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
}
</style>
