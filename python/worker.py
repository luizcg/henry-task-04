"""RabbitMQ worker entrypoint."""
from src.adapters.rabbitmq_consumer import run_consumer

if __name__ == "__main__":
    print("Starting RabbitMQ worker...")
    run_consumer()
