// frontend/src/types/index.ts — 全局类型定义

export interface Mailbox {
  address: string
  token: string
  expiresAt: string
}

export interface EmailAttachment {
  filename: string
  contentType: string
  size: number
  downloadUrl: string
}

export interface EmailSummary {
  id: string
  fromAddr: string
  subject: string
  receivedAt: string
  hasAttachments: boolean
  preview: string
}

export interface EmailDetail {
  id: string
  fromAddr: string
  toAddr: string
  subject: string
  textBody: string | null
  htmlBody: string | null
  receivedAt: string
  attachments: EmailAttachment[]
}

export interface WsMessage {
  type: 'new_email' | 'mailbox_expired' | 'pong'
  data?: EmailSummary
}

export interface ApiError {
  error: {
    code: string
    message: string
  }
}
