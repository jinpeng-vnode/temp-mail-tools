<template>
  <div class="email-detail-view">
    <!-- 加载态 -->
    <a-skeleton v-if="loading" active :paragraph="{ rows: 6 }" />

    <!-- 错误态 -->
    <a-result v-else-if="error" status="error" :title="$t('error.load')">
      <template #extra>
        <a-button type="primary" @click="fetchDetail">{{ $t('error.retry') }}</a-button>
        <a-button @click="goBack">{{ $t('email.back') }}</a-button>
      </template>
    </a-result>

    <!-- 正常态 -->
    <template v-else-if="email">
      <div class="detail-actions">
        <a-button @click="goBack">
          <template #icon><ArrowLeftOutlined /></template>
          {{ $t('email.back') }}
        </a-button>
        <a-popconfirm :title="$t('email.deleteConfirm')" @confirm="handleDelete">
          <a-button danger>
            <template #icon><DeleteOutlined /></template>
            {{ $t('email.delete') }}
          </a-button>
        </a-popconfirm>
      </div>

      <a-card class="detail-card">
        <h2>{{ email.subject }}</h2>
        <a-descriptions :column="1" size="small" bordered>
          <a-descriptions-item :label="$t('email.from')">{{ email.fromAddr }}</a-descriptions-item>
          <a-descriptions-item :label="$t('email.to')">{{ email.toAddr }}</a-descriptions-item>
          <a-descriptions-item :label="$t('email.time')">{{ formatDate(email.receivedAt) }}</a-descriptions-item>
        </a-descriptions>

        <a-divider />

        <!-- 邮件正文 -->
        <div v-if="email.htmlBody" class="email-body" v-html="sanitizedHtml"></div>
        <pre v-else-if="email.textBody" class="email-text">{{ email.textBody }}</pre>
        <a-empty v-else description="无内容" />

        <!-- 附件 -->
        <template v-if="email.attachments.length > 0">
          <a-divider>{{ $t('email.attachment') }} ({{ email.attachments.length }})</a-divider>
          <a-row :gutter="[12, 12]">
            <a-col v-for="att in email.attachments" :key="att.filename" :xs="24" :sm="12" :md="8">
              <a-card size="small" hoverable>
                <div class="attachment-item">
                  <PaperClipOutlined />
                  <span class="att-name">{{ att.filename }}</span>
                  <span class="att-size">{{ formatSize(att.size) }}</span>
                  <a :href="att.downloadUrl" download>
                    <a-button size="small" type="link">{{ $t('email.download') }}</a-button>
                  </a>
                </div>
              </a-card>
            </a-col>
          </a-row>
        </template>
      </a-card>
    </template>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeftOutlined, DeleteOutlined, PaperClipOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import DOMPurify from 'dompurify'
import type { EmailDetail } from '../types'

export default defineComponent({
  name: 'EmailDetailView',
  components: { ArrowLeftOutlined, DeleteOutlined, PaperClipOutlined },
  setup() {
    const route = useRoute()
    const router = useRouter()
    const email = ref<EmailDetail | null>(null)
    const loading = ref(true)
    const error = ref(false)

    const sanitizedHtml = computed(() => {
      if (!email.value?.htmlBody) return ''
      return DOMPurify.sanitize(email.value.htmlBody, {
        ADD_ATTR: ['target'],
        FORBID_TAGS: ['script', 'style'],
      })
    })

    async function fetchDetail() {
      const { token, emailId } = route.params as { token: string; emailId: string }
      loading.value = true
      error.value = false
      try {
        const res = await fetch(`/api/mailbox/${token}/emails/${emailId}`)
        if (!res.ok) throw new Error('Not found')
        email.value = await res.json()
      } catch {
        error.value = true
      } finally {
        loading.value = false
      }
    }

    async function handleDelete() {
      const { token } = route.params as { token: string }
      try {
        await fetch(`/api/mailbox/${token}`, { method: 'DELETE' })
        message.success('已删除')
        localStorage.removeItem('mailbox_token')
        router.push('/')
      } catch {
        message.error('删除失败')
      }
    }

    function goBack() { router.push('/') }

    function formatDate(iso: string): string {
      return new Date(iso).toLocaleString()
    }

    function formatSize(bytes: number): string {
      if (bytes < 1024) return `${bytes} B`
      if (bytes < 1048576) return `${(bytes / 1024).toFixed(1)} KB`
      return `${(bytes / 1048576).toFixed(1)} MB`
    }

    onMounted(fetchDetail)

    return { email, loading, error, sanitizedHtml, fetchDetail, handleDelete, goBack, formatDate, formatSize }
  },
})
</script>

<style scoped>
.email-detail-view { max-width: 840px; margin: 0 auto; }
.detail-actions { display: flex; justify-content: space-between; margin-bottom: 16px; }
.detail-card h2 { margin-bottom: 16px; }
.email-body { overflow: auto; max-width: 100%; line-height: 1.6; }
.email-body :deep(img) { max-width: 100%; height: auto; }
.email-body :deep(a) { color: #1677ff; }
.email-text { white-space: pre-wrap; word-break: break-word; font-size: 14px; line-height: 1.6; background: #fafafa; padding: 16px; border-radius: 8px; }
.attachment-item { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.att-name { font-weight: 500; word-break: break-all; }
.att-size { color: rgba(0, 0, 0, 0.45); font-size: 12px; }
</style>
