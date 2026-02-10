FROM node:22-slim

# Install Python
RUN apt-get update && \
    apt-get install -y python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Install Claude CLI and Gemini CLI
RUN npm install -g @anthropic-ai/claude-code @google/gemini-cli

WORKDIR /app

# Python deps
COPY requirements.txt .
RUN python3 -m pip install --break-system-packages -r requirements.txt

# App code
COPY . .

EXPOSE 8501

# Auth is handled via env vars at runtime:
#   ANTHROPIC_API_KEY  — for Claude CLI
#   GEMINI_API_KEY     — for Gemini CLI
CMD ["python3", "-m", "streamlit", "run", "app.py", \
     "--server.headless", "true", \
     "--server.port", "8501", \
     "--server.address", "0.0.0.0"]
