# Client for communicating with the Python Contract Comparison Agent
class ContractAgentClient
  include HTTParty
  base_uri ENV.fetch("PYTHON_AGENT_URL", "http://localhost:8080")

  def compare(original_url:, amendment_url:, contract_id:)
    response = self.class.post(
      "/api/v1/contracts/compare",
      body: {
        original_image: original_url,
        amendment_image: amendment_url,
        contract_id: contract_id
      }.to_json,
      headers: { "Content-Type" => "application/json" },
      timeout: 300 # 5 minutes timeout for LLM processing
    )

    if response.success?
      parsed = response.parsed_response
      {
        status: parsed["status"],
        result: parsed["result"],
        trace_id: parsed["trace_id"],
        processing_time_ms: parsed["processing_time_ms"],
        error: parsed["error"]
      }
    else
      {
        status: "error",
        error: "HTTP #{response.code}: #{response.message}",
        result: nil,
        trace_id: nil
      }
    end
  rescue HTTParty::Error, Timeout::Error => e
    {
      status: "error",
      error: e.message,
      result: nil,
      trace_id: nil
    }
  end

  def get_progress(contract_id)
    response = self.class.get(
      "/api/v1/jobs/#{contract_id}/progress",
      timeout: 3,
      open_timeout: 3,
      read_timeout: 3
    )

    if response.success?
      parsed = response.parsed_response
      {
        status: parsed["status"],
        progress: parsed["progress"],
        step: parsed["step"],
        message: parsed["message"]
      }
    else
      nil
    end
  rescue HTTParty::Error, Timeout::Error, Net::ReadTimeout, Net::OpenTimeout
    nil
  end
end
