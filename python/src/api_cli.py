"""CLI for starting the Contract Comparison API server."""
import typer
import uvicorn

app = typer.Typer(help="Contract Comparison API Server")


@app.command("start")
def start(
    host: str = typer.Option("0.0.0.0", help="Host to bind to"),
    port: int = typer.Option(8000, help="Port to bind to"),
    reload: bool = typer.Option(True, help="Enable auto-reload"),
    workers: int = typer.Option(1, help="Number of worker processes"),
):
    """Start the Contract Comparison API server."""
    typer.echo(f"🚀 Starting Contract Comparison API on {host}:{port}")
    typer.echo(f"📚 API docs available at: http://{host if host != '0.0.0.0' else 'localhost'}:{port}/docs")
    typer.echo(f"📖 ReDoc available at: http://{host if host != '0.0.0.0' else 'localhost'}:{port}/redoc")
    typer.echo()
    
    uvicorn.run(
        "src.adapters.rest_api:app",
        host=host,
        port=port,
        reload=reload,
        workers=workers if not reload else 1,
    )


if __name__ == "__main__":
    app()
