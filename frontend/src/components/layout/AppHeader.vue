<template>
  <a-layout-header class="app-header">
    <div class="header-inner">
      <router-link to="/" class="logo">
        <span class="logo-icon">📧</span>
        <span class="logo-text">Temp Mail</span>
      </router-link>
      <div class="header-actions">
        <a-dropdown>
          <a-button size="small">
            {{ locale === 'zh-CN' ? '🇨🇳 中文' : '🇺🇸 English' }}
          </a-button>
          <template #overlay>
            <a-menu @click="handleLocaleChange">
              <a-menu-item key="zh-CN">🇨🇳 中文</a-menu-item>
              <a-menu-item key="en-US">🇺🇸 English</a-menu-item>
            </a-menu>
          </template>
        </a-dropdown>
      </div>
    </div>
  </a-layout-header>
</template>

<script lang="ts">
import { defineComponent, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useLocaleStore } from '../../stores/locale'
import type { LocaleType } from '../../stores/locale'

export default defineComponent({
  name: 'AppHeader',
  setup() {
    const localeStore = useLocaleStore()
    const { locale: i18nLocale } = useI18n()
    const locale = computed(() => localeStore.locale)

    function handleLocaleChange({ key }: { key: string }) {
      localeStore.setLocale(key as LocaleType)
      i18nLocale.value = key
    }

    return { locale, handleLocaleChange }
  },
})
</script>

<style scoped>
.app-header {
  background: #fff;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.06);
  position: sticky;
  top: 0;
  z-index: 100;
  padding: 0 24px;
  height: 64px;
  line-height: 64px;
}
.header-inner {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  color: #1677ff;
  font-size: 20px;
  font-weight: 600;
}
.logo-icon { font-size: 24px; }
.header-actions { display: flex; align-items: center; gap: 12px; }

@media (max-width: 768px) {
  .app-header { height: 56px; line-height: 56px; padding: 0 16px; }
  .logo-text { display: none; }
}
</style>
