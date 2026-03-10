// WebSocket Service for Real-time Data Streaming
class WebSocketService {
  constructor(url) {
    this.url = url
    this.ws = null
    this.listeners = new Map()
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.reconnectDelay = 3000
  }

  connect() {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.url)

        this.ws.onopen = () => {
          console.log('WebSocket connected')
          this.reconnectAttempts = 0
          resolve()
        }

        this.ws.onmessage = (event) => {
          const data = JSON.parse(event.data)
          this.emit(data.type, data.payload)
        }

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error)
          reject(error)
        }

        this.ws.onclose = () => {
          console.log('WebSocket disconnected')
          this.attemptReconnect()
        }
      } catch (error) {
        reject(error)
      }
    })
  }

  attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      console.log(`Attempting reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})`)
      
      setTimeout(() => {
        this.connect().catch(err => console.error('Reconnect failed:', err))
      }, this.reconnectDelay)
    }
  }

  subscribe(eventType, callback) {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, [])
    }
    this.listeners.get(eventType).push(callback)

    // Return unsubscribe function
    return () => {
      const callbacks = this.listeners.get(eventType)
      const index = callbacks.indexOf(callback)
      if (index > -1) {
        callbacks.splice(index, 1)
      }
    }
  }

  emit(eventType, data) {
    if (this.listeners.has(eventType)) {
      this.listeners.get(eventType).forEach(callback => {
        callback(data)
      })
    }
  }

  send(message) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message))
    } else {
      console.warn('WebSocket not connected')
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  isConnected() {
    return this.ws && this.ws.readyState === WebSocket.OPEN
  }
}

// Hook for WebSocket usage
export function useWebSocket(url) {
  const [isConnected, setIsConnected] = React.useState(false)
  const [lastMessage, setLastMessage] = React.useState(null)
  const wsRef = React.useRef(null)

  React.useEffect(() => {
    wsRef.current = new WebSocketService(url)
    
    wsRef.current.connect()
      .then(() => setIsConnected(true))
      .catch(err => console.error('Connection failed:', err))

    return () => {
      wsRef.current?.disconnect()
    }
  }, [url])

  const subscribe = React.useCallback((eventType, callback) => {
    return wsRef.current?.subscribe(eventType, (data) => {
      setLastMessage(data)
      callback(data)
    })
  }, [])

  const send = React.useCallback((message) => {
    wsRef.current?.send(message)
  }, [])

  return {
    isConnected,
    lastMessage,
    subscribe,
    send
  }
}

export default WebSocketService
