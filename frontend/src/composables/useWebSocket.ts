// frontend/src/composables/useWebSocket.ts — WebSocket 连接 hook
import { ref, onUnmounted } from 'vue'
import type { WsMessage } from '../types'

export function useWebSocket(token: string, onMessage: (msg: WsMessage) => void) {
  const status = ref<'connecting' | 'connected' | 'disconnected'>('disconnected')
  let ws: WebSocket | null = null
  let pingInterval: ReturnType<typeof setInterval> | null = null
  let reconnectTimeout: ReturnType<typeof setTimeout> | null = null

  function connect() {
    if (ws) close()
    const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:'
    ws = new WebSocket(`${protocol}//${location.host}/ws/${token}`)
    status.value = 'connecting'

    ws.onopen = () => {
      status.value = 'connected'
      // 每30秒发送心跳
      pingInterval = setInterval(() => {
        ws?.send(JSON.stringify({ type: 'ping' }))
      }, 30000)
    }

    ws.onmessage = (event) => {
      const msg: WsMessage = JSON.parse(event.data)
      if (msg.type !== 'pong') {
        onMessage(msg)
      }
    }

    ws.onclose = () => {
      status.value = 'disconnected'
      cleanup()
      // 自动重连
      reconnectTimeout = setTimeout(connect, 3000)
    }

    ws.onerror = () => {
      ws?.close()
    }
  }

  function cleanup() {
    if (pingInterval) { clearInterval(pingInterval); pingInterval = null }
  }

  function close() {
    if (reconnectTimeout) { clearTimeout(reconnectTimeout); reconnectTimeout = null }
    cleanup()
    if (ws) { ws.onclose = null; ws.close(); ws = null }
    status.value = 'disconnected'
  }

  onUnmounted(close)

  return { status, connect, close }
}
