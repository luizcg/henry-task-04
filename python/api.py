"""REST API entrypoint."""
import uvicorn
from src.adapters.rest_api import app
from src.config.settings import settings

if __name__ == "__main__":
    uvicorn.run(
        "src.adapters.rest_api:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        workers=1,  # Single worker but with proper async handling
        timeout_keep_alive=300,  # Keep connections alive for long requests
    )
