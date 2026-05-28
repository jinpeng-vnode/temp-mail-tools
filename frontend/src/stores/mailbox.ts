// frontend/src/stores/mailbox.ts — 邮箱状态管理
import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Mailbox, EmailSummary } from '../types'

export const useMailboxStore = defineStore('mailbox', () => {
  const mailbox = ref<Mailbox | null>(null)
  const emails = ref<EmailSummary[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const total = ref(0)

  // 生成新邮箱
  async function generate(domain?: string) {
    loading.value = true
    error.value = null
    try {
      const res = await fetch('/api/mailbox', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(domain ? { domain } : {}),
      })
      if (!res.ok) throw new Error('生成失败')
      const data = await res.json()
      mailbox.value = { address: data.address, token: data.token, expiresAt: data.expiresAt || data.expires_at }
      emails.value = []
      total.value = 0
      // 持久化到 localStorage
      localStorage.setItem('mailbox_token', data.token)
    } catch (e: unknown) {
      error.value = (e as Error).message
    } finally {
      loading.value = false
    }
  }

  // 恢复已有邮箱
  async function restore(token: string) {
    loading.value = true
    error.value = null
    try {
      const res = await fetch(`/api/mailbox/${token}`)
      if (!res.ok) {
        localStorage.removeItem('mailbox_token')
        return false
      }
      const data = await res.json()
      mailbox.value = { address: data.address, token: data.token, expiresAt: data.expiresAt || data.expires_at }
      return true
    } catch {
      localStorage.removeItem('mailbox_token')
      return false
    } finally {
      loading.value = false
    }
  }

  // 获取邮件列表
  async function fetchEmails(page = 1, size = 20) {
    if (!mailbox.value) return
    try {
      const res = await fetch(`/api/mailbox/${mailbox.value.token}/emails?page=${page}&size=${size}`)
      if (!res.ok) throw new Error('加载失败')
      const data = await res.json()
      if (page === 1) {
        emails.value = data.items
      } else {
        emails.value.push(...data.items)
      }
      total.value = data.total
    } catch (e: unknown) {
      error.value = (e as Error).message
    }
  }

  // 添加新邮件（WebSocket推送）
  function addEmail(email: EmailSummary) {
    emails.value.unshift(email)
    total.value++
  }

  // 清空状态
  function clear() {
    mailbox.value = null
    emails.value = []
    total.value = 0
    localStorage.removeItem('mailbox_token')
  }

  return { mailbox, emails, loading, error, total, generate, restore, fetchEmails, addEmail, clear }
})
