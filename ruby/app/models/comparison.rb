class Comparison < ApplicationRecord
  # Attachments
  has_one_attached :original_document
  has_one_attached :amendment_document

  # Status enum
  enum :status, { pending: 0, processing: 1, completed: 2, failed: 3 }

  # Validations
  validates :original_document, presence: true, on: :create
  validates :amendment_document, presence: true, on: :create

  # Callbacks
  after_create_commit :enqueue_comparison_job

  # Result accessors
  def sections_changed
    result&.dig("sections_changed") || []
  end

  def topics_touched
    result&.dig("topics_touched") || []
  end

  def summary
    result&.dig("summary_of_the_change")
  end

  # Generate pre-signed URLs for the Python agent
  def original_document_url(expires_in: 1.hour)
    return nil unless original_document.attached?
    original_document.url(expires_in: expires_in)
  end

  def amendment_document_url(expires_in: 1.hour)
    return nil unless amendment_document.attached?
    amendment_document.url(expires_in: expires_in)
  end

  private

  def enqueue_comparison_job
    ComparisonJob.perform_later(id)
  end
end
