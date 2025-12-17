class ComparisonJob < ApplicationJob
  queue_as :default
  retry_on StandardError, wait: 5.seconds, attempts: 3

  def perform(comparison_id)
    comparison = Comparison.find(comparison_id)
    comparison.processing!

    broadcast_progress(comparison, "processing", 0, "Starting comparison job...")

    progress_thread = start_progress_polling(comparison)

    begin
      client = ContractAgentClient.new
      
      response = client.compare(
        original_url: comparison.original_document_url,
        amendment_url: comparison.amendment_document_url,
        contract_id: comparison.id.to_s
      )

      if response[:status] == "success"
        comparison.update!(
          status: :completed,
          result: response[:result],
          trace_id: response[:trace_id],
          processing_time_ms: response[:processing_time_ms]
        )
        broadcast_progress(comparison, "completed", 100, "Processing complete!")
      else
        comparison.update!(
          status: :failed,
          error_message: response[:error],
          trace_id: response[:trace_id]
        )
        broadcast_progress(comparison, "failed", 100, "Processing failed")
      end
    ensure
      # Stop progress polling thread
      progress_thread&.kill
    end
  rescue StandardError => e
    comparison&.update!(status: :failed, error_message: e.message)
    broadcast_progress(comparison, "failed", 100, "Error: #{e.message}")
    raise
  end

  private

  def start_progress_polling(comparison)
    Thread.new do
      client = ContractAgentClient.new
      last_progress = 0

      loop do
        begin
          progress = client.get_progress(comparison.id.to_s)
          
          if progress && progress[:progress] != last_progress
            broadcast_progress(
              comparison,
              progress[:status],
              progress[:progress],
              progress[:message],
              progress[:step]
            )
            last_progress = progress[:progress]
          end
        rescue => e
          Rails.logger.error "Progress polling error: #{e.message}"
        end

        sleep 1
      end
    end
  end

  def broadcast_progress(comparison, status, progress, message, step = nil)
    ActionCable.server.broadcast(
      "comparison_progress_#{comparison.id}",
      {
        comparison_id: comparison.id,
        status: status,
        progress: progress,
        message: message,
        step: step
      }
    )
  end
end
