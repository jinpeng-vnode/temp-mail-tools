// frontend/src/stores/locale.ts — 语言切换状态
import { defineStore } from 'pinia'
import { ref } from 'vue'

export type LocaleType = 'zh-CN' | 'en-US'

export const useLocaleStore = defineStore('locale', () => {
  const locale = ref<LocaleType>(
    (localStorage.getItem('locale') as LocaleType) || 'zh-CN'
  )

  function setLocale(val: LocaleType) {
    locale.value = val
    localStorage.setItem('locale', val)
    document.documentElement.lang = val === 'zh-CN' ? 'zh-CN' : 'en'
  }

  return { locale, setLocale }
})
