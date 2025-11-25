<script setup lang="ts">
import { ref } from "vue";
import VueRecaptcha from "vue3-recaptcha2";
import { RECAPTCHA_SITE_KEY } from "../config/captcha";

export interface RecaptchaExposed {
  reset: () => void;
}

const emit = defineEmits<{
  verify: [token: string];
  error: [];
  expired: [];
}>();

const loadingTimeout = ref(30000);
const showRecaptcha = ref(true);
const recaptchaRef = ref<InstanceType<typeof VueRecaptcha> | null>(null);

const onVerify = (response: string) => {
  emit("verify", response);
};

const onExpired = () => {
  emit("expired");
};

const onError = () => {
  emit("error");
};

defineExpose({
  reset: () => {
    recaptchaRef.value?.reset();
  },
});
</script>

<template>
  <div class="recaptcha-wrapper">
    <vue-recaptcha
      ref="recaptchaRef"
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
