<template>
  <div v-if="visible" class="ad-slot" :class="`ad-slot--${slot}`" :style="slotStyle">
    <div class="ad-placeholder">
      <span class="ad-label">AD</span>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed } from 'vue'

// 广告位尺寸配置
const SLOT_SIZES: Record<string, { desktop: string; mobile: string; hideOnMobile?: boolean }> = {
  'header-banner': { desktop: '728px / 90px', mobile: '320px / 100px' },
  'sidebar-1': { desktop: '300px / 250px', mobile: '', hideOnMobile: true },
  'sidebar-2': { desktop: '300px / 250px', mobile: '', hideOnMobile: true },
  'footer-banner': { desktop: '728px / 90px', mobile: '320px / 100px' },
  'inbox-between': { desktop: '728px / 90px', mobile: '320px / 100px' },
}

export default defineComponent({
  name: 'AdSlot',
  props: {
    slot: { type: String, required: true },
    fallback: { type: Boolean, default: true },
  },
  setup(props) {
    const config = computed(() => SLOT_SIZES[props.slot] || { desktop: '728px / 90px', mobile: '320px / 100px' })
    const visible = computed(() => props.fallback)

    const slotStyle = computed(() => {
      const [w, h] = config.value.desktop.split('/').map(s => s.trim())
      return { maxWidth: w, height: h }
    })

    return { visible, slotStyle }
  },
})
</script>

<style scoped>
.ad-slot {
  margin: 16px auto;
  display: flex;
  align-items: center;
  justify-content: center;
}
.ad-placeholder {
  width: 100%;
  height: 100%;
  background: #fafafa;
  border: 1px dashed #d9d9d9;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.ad-label {
  color: rgba(0, 0, 0, 0.25);
  font-size: 12px;
  font-weight: 500;
}

/* 侧边栏广告在移动端隐藏 */
.ad-slot--sidebar-1,
.ad-slot--sidebar-2 {
  display: none;
}
@media (min-width: 1024px) {
  .ad-slot--sidebar-1,
  .ad-slot--sidebar-2 {
    display: flex;
  }
}

/* 移动端尺寸适配 */
@media (max-width: 768px) {
  .ad-slot { max-width: 320px !important; height: 100px !important; }
}
</style>
