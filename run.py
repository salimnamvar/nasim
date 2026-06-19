import logging
import sys

from interpreter import interpreter

# --- Configuration ---
OLLAMA_MODEL = "ollama/nemotron-3-nano:4b-bf16"
OLLAMA_API_BASE = "http://192.168.70.125:11434"


def setup_logging():
    """Configures logging for better verbosity."""
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    return logging.getLogger(__name__)


def initialize_ollama_connection(logger):
    """Initializes the interpreter connection with Ollama settings."""
    logger.info("Initializing Interpreter connection to Ollama...")
    try:
        interpreter.llm.model = OLLAMA_MODEL
        interpreter.llm.api_base = OLLAMA_API_BASE
        interpreter.auto_run = True
        interpreter.verbose = True
        logger.info(f"Model set to: {OLLAMA_MODEL}")
        logger.info(f"API Base set to: {OLLAMA_API_BASE}")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize Ollama connection: {e}")
        return False


def main():
    """Main execution function."""
    logger = setup_logging()
    logger.info("Starting Nasim Runner script.")

    if initialize_ollama_connection(logger):
        try:
            logger.info("Connection successful. Starting interactive chat session.")
            interpreter.chat()
        except Exception as e:
            logger.error(f"An error occurred during the chat session: {e}")
            sys.exit(1)
    else:
        logger.error("Initialization failed. Exiting script.")
        sys.exit(1)


if __name__ == "__main__":
    main()
