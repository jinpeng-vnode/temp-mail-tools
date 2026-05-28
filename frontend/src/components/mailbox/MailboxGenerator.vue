<template>
  <a-card class="mailbox-generator">
    <h2 class="generator-title">{{ $t('mailbox.title') }}</h2>

    <!-- 加载态 -->
    <a-skeleton v-if="store.loading" active :paragraph="{ rows: 1, width: '60%' }" />

    <!-- 错误态 -->
    <a-alert v-else-if="store.error" type="error" :message="$t('error.generate')" show-icon>
      <template #action>
        <a-button size="small" @click="store.generate()">{{ $t('error.retry') }}</a-button>
      </template>
    </a-alert>

    <!-- 正常态 -->
    <div v-else-if="store.mailbox" class="address-display">
      <div class="address-row">
        <span class="address-text">{{ store.mailbox.address }}</span>
        <a-space>
          <a-tooltip :title="copied ? $t('mailbox.copied') : $t('mailbox.copy')">
            <a-button type="primary" @click="copyAddress">
              <template #icon><CopyOutlined v-if="!copied" /><CheckOutlined v-else /></template>
            </a-button>
          </a-tooltip>
          <a-tooltip :title="$t('mailbox.refresh')">
            <a-button @click="store.generate()">
              <template #icon><ReloadOutlined /></template>
            </a-button>
          </a-tooltip>
        </a-space>
      </div>
      <div class="address-meta">
        <a-statistic-countdown
          :value="expiresTimestamp"
          format="mm:ss"
          :title="$t('mailbox.expiresIn')"
          @finish="handleExpired"
        />
      </div>
    </div>
  </a-card>
</template>

<script lang="ts">
import { defineComponent, ref, computed } from 'vue'
import { CopyOutlined, CheckOutlined, ReloadOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import { useI18n } from 'vue-i18n'
import { useMailboxStore } from '../../stores/mailbox'

export default defineComponent({
  name: 'MailboxGenerator',
  components: { CopyOutlined, CheckOutlined, ReloadOutlined },
  setup() {
    const store = useMailboxStore()
    const { t } = useI18n()
    const copied = ref(false)

    const expiresTimestamp = computed(() => {
      if (!store.mailbox) return 0
      return new Date(store.mailbox.expiresAt).getTime()
    })

    async function copyAddress() {
      if (!store.mailbox) return
      await navigator.clipboard.writeText(store.mailbox.address)
      copied.value = true
      message.success(t('mailbox.copied'))
      setTimeout(() => { copied.value = false }, 2000)
    }

    function handleExpired() {
      message.warning(t('error.expired'))
      store.generate()
    }

    return { store, copied, expiresTimestamp, copyAddress, handleExpired }
  },
})
</script>

<style scoped>
.mailbox-generator { margin-bottom: 24px; }
.generator-title { margin-bottom: 16px; font-size: 20px; }
.address-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px 16px;
  background: #f5f5f5;
  border-radius: 8px;
}
.address-text {
  font-family: "SF Mono", "JetBrains Mono", "Fira Code", monospace;
  font-size: 20px;
  font-weight: 500;
  word-break: break-all;
}
.address-meta { margin-top: 12px; }

@media (max-width: 768px) {
  .address-row { flex-direction: column; align-items: stretch; }
  .address-text { font-size: 16px; text-align: center; margin-bottom: 8px; }
}
</style>
