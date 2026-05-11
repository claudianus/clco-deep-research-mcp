import { defineI18nConfig } from '@nuxtjs/i18n'
import en from './i18n/en.json'
import ko from './i18n/ko.json'

export default defineI18nConfig(() => ({
  legacy: false,
  locale: 'en',
  fallbackLocale: 'en',
  messages: { en, ko },
}))
