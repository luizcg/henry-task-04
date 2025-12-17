class AddDefaultStatusToComparisons < ActiveRecord::Migration[8.0]
  def change
    change_column_default :comparisons, :status, from: nil, to: 0
    
    # Update existing records
    reversible do |dir|
      dir.up do
        execute "UPDATE comparisons SET status = 0 WHERE status IS NULL"
      end
    end
  end
end
