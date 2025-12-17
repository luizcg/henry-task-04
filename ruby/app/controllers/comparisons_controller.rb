class ComparisonsController < ApplicationController
  before_action :set_comparison, only: [:show]

  def index
    @comparisons = Comparison.order(created_at: :desc)
  end

  def show
  end

  def new
    @comparison = Comparison.new
  end

  def create
    @comparison = Comparison.new(comparison_params)

    if @comparison.save
      redirect_to @comparison, notice: "Comparison queued for processing."
    else
      render :new, status: :unprocessable_entity
    end
  end

  private

  def set_comparison
    @comparison = Comparison.find(params[:id])
  end

  def comparison_params
    params.require(:comparison).permit(:original_document, :amendment_document)
  end
end
