<template>
  <div class="home-view">
    <SeoHead :title="$t('mailbox.title') + ' - Temp Mail'" :description="$t('inbox.emptyHint')" />
    <MailboxGenerator />
    <AdSlot slot="header-banner" />
    <InboxList :ws-status="wsStatus" />
  </div>
</template>

<script lang="ts">
import { defineComponent, onMounted, watch, ref } from 'vue'
import { useMailboxStore } from '../stores/mailbox'
import { useWebSocket } from '../composables/useWebSocket'
import MailboxGenerator from '../components/mailbox/MailboxGenerator.vue'
import InboxList from '../components/mailbox/InboxList.vue'
import AdSlot from '../components/ads/AdSlot.vue'
import SeoHead from '../components/seo/SeoHead.vue'
import type { WsMessage } from '../types'

export default defineComponent({
  name: 'HomeView',
  components: { MailboxGenerator, InboxList, AdSlot, SeoHead },
  setup() {
    const store = useMailboxStore()
    const wsStatus = ref<'connecting' | 'connected' | 'disconnected'>('disconnected')
    let wsInstance: ReturnType<typeof useWebSocket> | null = null

    function handleWsMessage(msg: WsMessage) {
      if (msg.type === 'new_email' && msg.data) {
        store.addEmail(msg.data)
      } else if (msg.type === 'mailbox_expired') {
        store.generate()
      }
    }

    function connectWs(token: string) {
      if (wsInstance) wsInstance.close()
      wsInstance = useWebSocket(token, handleWsMessage)
      wsInstance.connect()
      // 同步状态
      watch(wsInstance.status, (val) => { wsStatus.value = val }, { immediate: true })
    }

    onMounted(async () => {
      // 尝试恢复已有邮箱
      const savedToken = localStorage.getItem('mailbox_token')
      if (savedToken) {
        const ok = await store.restore(savedToken)
        if (ok && store.mailbox) {
          connectWs(store.mailbox.token)
          await store.fetchEmails()
          return
        }
      }
      // 生成新邮箱
      await store.generate()
      if (store.mailbox) {
        connectWs(store.mailbox.token)
      }
    })

    // 监听邮箱变化，重连WS
    watch(() => store.mailbox?.token, (newToken) => {
      if (newToken) connectWs(newToken)
    })

    return { wsStatus }
  },
})
</script>

<style scoped>
.home-view { max-width: 840px; margin: 0 auto; }
</style>
