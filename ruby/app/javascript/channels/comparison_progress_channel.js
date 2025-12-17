import consumer from "channels/consumer"

// Wait for DOM to be ready and check for comparisonId
document.addEventListener('turbo:load', () => {
  const progressContainer = document.querySelector('[data-comparison-id]')
  const comparisonId = progressContainer?.dataset.comparisonId
  
  if (comparisonId) {
    consumer.subscriptions.create(
      { channel: "ComparisonProgressChannel", comparison_id: comparisonId },
      {
        connected() {
          // WebSocket connected
        },

        disconnected() {
          // WebSocket disconnected
        },

        received(data) {
          const progressBar = document.getElementById("progress-bar")
          const progressStatus = document.getElementById("progress-status")
          const progressMessage = document.getElementById("progress-message")
          const progressLog = document.getElementById("progress-log")
        
          if (progressBar && data.progress !== undefined) {
            progressBar.style.width = `${data.progress}%`
          }
        
          if (progressStatus && data.step) {
            progressStatus.textContent = data.step
          }
        
          if (progressMessage && data.message) {
            progressMessage.textContent = data.message
          }
        
          if (progressLog && data.message) {
            const logEntry = document.createElement("div")
            logEntry.textContent = `[${new Date().toLocaleTimeString()}] ${data.message}`
            progressLog.appendChild(logEntry)
            progressLog.scrollTop = progressLog.scrollHeight
          }
        
          if (data.status === "completed" || data.status === "failed") {
            setTimeout(() => {
              window.location.reload()
            }, 2000)
          }
        }
      }
    )
  }
})
