class ComparisonProgressChannel < ApplicationCable::Channel
  def subscribed
    comparison = Comparison.find(params[:comparison_id])
    stream_from "comparison_progress_#{comparison.id}"
  end

  def unsubscribed
    # Any cleanup needed when channel is unsubscribed
  end
end
