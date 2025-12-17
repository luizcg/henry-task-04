class CreateContractComparisons < ActiveRecord::Migration[8.0]
  def change
    create_table :contract_comparisons do |t|
      t.integer :status
      t.jsonb :result
      t.string :trace_id
      t.text :error_message
      t.integer :processing_time_ms

      t.timestamps
    end
  end
end
