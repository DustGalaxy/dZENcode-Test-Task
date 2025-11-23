<script setup lang="ts">
import RegistrationForm from "../components/RegistrationForm.vue";
</script>

<template>
  <div class="register-page">
    <RegistrationForm />
  </div>
</template>

<style scoped>
.register-page {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
}
</style>
