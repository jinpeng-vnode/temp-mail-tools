<template>
  <a-config-provider :locale="antLocale">
    <a-layout class="app-layout">
      <AppHeader />
      <a-layout-content class="app-content">
        <router-view />
      </a-layout-content>
      <AppFooter />
    </a-layout>
  </a-config-provider>
</template>

<script lang="ts">
import { defineComponent, computed } from 'vue'
import { useLocaleStore } from './stores/locale'
import zhCN from 'ant-design-vue/es/locale/zh_CN'
import enUS from 'ant-design-vue/es/locale/en_US'
import AppHeader from './components/layout/AppHeader.vue'
import AppFooter from './components/layout/AppFooter.vue'

export default defineComponent({
  name: 'App',
  components: { AppHeader, AppFooter },
  setup() {
    const localeStore = useLocaleStore()
    const antLocale = computed(() => localeStore.locale === 'zh-CN' ? zhCN : enUS)
    return { antLocale }
  },
})
</script>

<style>
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
}
.app-layout {
  min-height: 100vh;
}
.app-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px 16px;
  width: 100%;
}
</style>
