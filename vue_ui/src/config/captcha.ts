export const RECAPTCHA_SITE_KEY = import.meta.env.VITE_RECAPTCHA_SITE_KEY || '';

if (!RECAPTCHA_SITE_KEY) {
  console.warn('RECAPTCHA_SITE_KEY is not configured. Please add VITE_RECAPTCHA_SITE_KEY to your .env file');
}
