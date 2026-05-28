<template>
  <a-layout-footer class="app-footer">
    <div class="footer-inner">
      <div class="footer-links">
        <a href="#">{{ $t('footer.about') }}</a>
        <a-divider type="vertical" />
        <a href="#">{{ $t('footer.privacy') }}</a>
        <a-divider type="vertical" />
        <a href="#">{{ $t('footer.terms') }}</a>
      </div>
      <div class="footer-copyright">
        © {{ new Date().getFullYear() }} Temp Mail. All rights reserved.
      </div>
    </div>
  </a-layout-footer>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({ name: 'AppFooter' })
</script>

<style scoped>
.app-footer {
  text-align: center;
  background: #fafafa;
  padding: 24px;
}
.footer-inner { max-width: 1200px; margin: 0 auto; }
.footer-links { margin-bottom: 8px; }
.footer-links a { color: rgba(0, 0, 0, 0.65); text-decoration: none; }
.footer-links a:hover { color: #1677ff; }
.footer-copyright { color: rgba(0, 0, 0, 0.45); font-size: 12px; }
</style>
