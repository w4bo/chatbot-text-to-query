#!/bin/sh
set -e

MODEL_NAME="llama3"

# Start Ollama server in the background
ollama serve &
OLLAMA_PID=$!

# Wait for the server to be ready
echo "Waiting for Ollama server to start..."
until curl -s http://127.0.0.1:11434/api/version > /dev/null; do
  sleep 2
done

# Pull the model if not already present
if ! curl -s http://127.0.0.1:11434/api/tags | grep -q "$MODEL_NAME"; then
  echo "Pulling model $MODEL_NAME..."
  curl -X POST http://127.0.0.1:11434/api/pull -d "{\"name\":\"$MODEL_NAME\"}"
else
  echo "Model $MODEL_NAME already exists."
fi

# Wait for Ollama server process (keeps container alive)
wait $OLLAMA_PID
