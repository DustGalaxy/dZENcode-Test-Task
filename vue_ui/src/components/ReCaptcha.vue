<script setup lang="ts">
import { ref } from "vue";
import vueRecaptcha from "vue3-recaptcha2";
import { RECAPTCHA_SITE_KEY } from "../config/captcha";

const emit = defineEmits<{
  verify: [token: string];
  error: [];
  expired: [];
}>();

const loadingTimeout = ref(30000);
const showRecaptcha = ref(true);
const recaptchaRef = ref<InstanceType<typeof vueRecaptcha> | null>(null);

const onVerify = (response: string) => {
  emit("verify", response);
  recaptchaRef.reset();
};

const onExpired = () => {
  emit("expired");
  recaptchaRef.reset();
};

const onError = () => {
  emit("error");
};
</script>

<template>
  <div class="recaptcha-wrapper">
    <vue-recaptcha
      v-show="showRecaptcha"
      :sitekey="RECAPTCHA_SITE_KEY"
      size="normal"
      theme="light"
      hl="en"
      :loading-timeout="loadingTimeout"
      @verify="onVerify"
      @expire="onExpired"
      @fail="onError"
      @error="onError"
      :ref="recaptchaRef"
    >
    </vue-recaptcha>
  </div>
</template>

<style scoped>
.recaptcha-wrapper {
  display: flex;
  justify-content: flex-start;
  margin: 1rem 0;
}
</style>
