Rails.application.routes.draw do
  # Comparisons
  resources :comparisons, only: [:index, :show, :new, :create]
  root "comparisons#index"

  # Health check
  get "up" => "rails/health#show", as: :rails_health_check
end
