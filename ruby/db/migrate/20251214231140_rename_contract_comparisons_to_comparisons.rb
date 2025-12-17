class RenameContractComparisonsToComparisons < ActiveRecord::Migration[8.0]
  def change
    rename_table :contract_comparisons, :comparisons
  end
end
