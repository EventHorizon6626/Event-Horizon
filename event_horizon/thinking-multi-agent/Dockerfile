FROM vllm/vllm-openai:latest

# Install app dependencies first (layer caching)
COPY event_horizon/thinking-multi-agent/app/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy the full event_horizon package (needed for Stage 1 agents, BullBearAnalyzer, etc.)
COPY event_horizon/ /opt/event_horizon/

# Copy the FastAPI app
COPY event_horizon/thinking-multi-agent/app/ /app/

# Copy the entrypoint script
COPY event_horizon/thinking-multi-agent/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# event_horizon package must be importable
ENV PYTHONPATH="/opt"

EXPOSE 8030

ENTRYPOINT ["/entrypoint.sh"]
