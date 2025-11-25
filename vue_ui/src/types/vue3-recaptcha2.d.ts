declare module 'vue3-recaptcha2' {
  import type { DefineComponent, ComponentPublicInstance } from 'vue';

  export interface VueRecaptchaProps {
    sitekey: string;
    size?: 'compact' | 'normal' | 'invisible';
    theme?: 'light' | 'dark';
    hl?: string;
    loadingTimeout?: number;
    tabindex?: number;
  }

  export interface VueRecaptchaMethods {
    reset(): void;
    execute(): void;
  }

  export type VueRecaptchaInstance = ComponentPublicInstance<VueRecaptchaProps, VueRecaptchaMethods>;

  const VueRecaptcha: DefineComponent<VueRecaptchaProps, {}, {}, {}, VueRecaptchaMethods>;
  export default VueRecaptcha;
}
