<template>
  <div class="inbox-list">
    <div class="inbox-header">
      <h3>{{ $t('inbox.title') }}</h3>
      <a-badge :status="wsStatus === 'connected' ? 'success' : 'error'" />
      <a-tag :color="wsStatus === 'connected' ? 'green' : 'red'" size="small">
        {{ wsStatus === 'connected' ? $t('inbox.connected') : $t('inbox.disconnected') }}
      </a-tag>
    </div>

    <!-- WS断开警告 -->
    <a-alert
      v-if="wsStatus === 'disconnected'"
      type="warning"
      :message="$t('inbox.reconnecting')"
      banner
      class="ws-alert"
    />

    <!-- 加载态 -->
    <div v-if="loading" class="inbox-skeleton">
      <a-skeleton v-for="i in 3" :key="i" active avatar :paragraph="{ rows: 2 }" />
    </div>

    <!-- 空数据态 -->
    <a-empty v-else-if="store.emails.length === 0" class="inbox-empty">
      <template #description>
        <div>
          <p class="empty-title">{{ $t('inbox.empty') }}</p>
          <p class="empty-hint">{{ $t('inbox.emptyHint') }}</p>
        </div>
      </template>
    </a-empty>

    <!-- 邮件列表 -->
    <a-list v-else :data-source="store.emails" item-layout="horizontal">
      <template #renderItem="{ item }">
        <a-list-item class="email-item" @click="openEmail(item)">
          <a-list-item-meta>
            <template #avatar>
              <a-avatar :style="{ backgroundColor: avatarColor(item.fromAddr) }">
                {{ item.fromAddr.charAt(0).toUpperCase() }}
              </a-avatar>
            </template>
            <template #title>
              <div class="email-title-row">
                <span class="email-from">{{ item.fromAddr }}</span>
                <span class="email-time">{{ formatTime(item.receivedAt) }}</span>
              </div>
            </template>
            <template #description>
              <div class="email-desc">
                <span class="email-subject">{{ item.subject }}</span>
                <PaperClipOutlined v-if="item.hasAttachments" class="attachment-icon" />
              </div>
              <div class="email-preview">{{ item.preview }}</div>
            </template>
          </a-list-item-meta>
        </a-list-item>
      </template>
    </a-list>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, type PropType } from 'vue'
import { useRouter } from 'vue-router'
import { PaperClipOutlined } from '@ant-design/icons-vue'
import { useMailboxStore } from '../../stores/mailbox'
import type { EmailSummary } from '../../types'

export default defineComponent({
  name: 'InboxList',
  components: { PaperClipOutlined },
  props: {
    wsStatus: { type: String as PropType<'connecting' | 'connected' | 'disconnected'>, default: 'disconnected' },
  },
  setup() {
    const store = useMailboxStore()
    const router = useRouter()
    const loading = ref(false)

    onMounted(async () => {
      if (store.mailbox) {
        loading.value = true
        await store.fetchEmails()
        loading.value = false
      }
    })

    function openEmail(item: EmailSummary) {
      if (store.mailbox) {
        router.push({ name: 'email-detail', params: { token: store.mailbox.token, emailId: item.id } })
      }
    }

    function avatarColor(email: string): string {
      // 根据邮箱地址生成稳定颜色
      let hash = 0
      for (let i = 0; i < email.length; i++) {
        hash = email.charCodeAt(i) + ((hash << 5) - hash)
      }
      const colors = ['#1677ff', '#52c41a', '#faad14', '#ff4d4f', '#722ed1', '#13c2c2']
      return colors[Math.abs(hash) % colors.length]
    }

    function formatTime(iso: string): string {
      const diff = Date.now() - new Date(iso).getTime()
      const minutes = Math.floor(diff / 60000)
      if (minutes < 1) return '刚刚'
      if (minutes < 60) return `${minutes}分钟前`
      const hours = Math.floor(minutes / 60)
      if (hours < 24) return `${hours}小时前`
      return new Date(iso).toLocaleDateString()
    }

    return { store, loading, openEmail, avatarColor, formatTime }
  },
})
</script>

<style scoped>
.inbox-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}
.inbox-header h3 { margin: 0; }
.ws-alert { margin-bottom: 12px; }
.inbox-skeleton { display: flex; flex-direction: column; gap: 16px; }
.inbox-empty { padding: 48px 0; }
.empty-title { font-size: 16px; color: rgba(0, 0, 0, 0.65); }
.empty-hint { font-size: 14px; color: rgba(0, 0, 0, 0.45); }
.email-item { cursor: pointer; transition: background 0.2s; }
.email-item:hover { background: #f5f5f5; }
.email-title-row { display: flex; justify-content: space-between; align-items: center; }
.email-from { font-weight: 500; }
.email-time { font-size: 12px; color: rgba(0, 0, 0, 0.45); }
.email-desc { display: flex; align-items: center; gap: 4px; }
.email-subject { font-weight: 500; color: rgba(0, 0, 0, 0.88); }
.attachment-icon { color: rgba(0, 0, 0, 0.45); }
.email-preview { color: rgba(0, 0, 0, 0.45); font-size: 13px; margin-top: 4px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
</style>
