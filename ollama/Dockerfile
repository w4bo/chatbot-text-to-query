FROM ollama/ollama:0.13.0

# Install curl
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy startup script
COPY start-ollama.sh /start-ollama.sh
RUN chmod +x /start-ollama.sh

# Use script as entrypoint
ENTRYPOINT ["/bin/sh", "/start-ollama.sh"]
