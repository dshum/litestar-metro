# Stage 1: Build stage
FROM python:3.12-slim-bookworm AS builder

# Install PDM and system dependencies
RUN pip install pdm

# Set working directory
WORKDIR /workspace

# Copy only dependency files first
COPY pyproject.toml pdm.lock* ./

# Create a virtual environment and install dependencies
RUN pdm venv create && \
    pdm install -v --prod --no-self

# Copy the rest of the application code
COPY app /workspace/app

# Stage 2: Production stage
FROM python:3.12-slim-bookworm AS final

# Set working directory
WORKDIR /workspace

# Copy only necessary artifacts from the builder stage
COPY --from=builder /workspace/.venv /workspace/.venv
COPY --from=builder /workspace/app /workspace/app

# Set environment variables
ENV PATH="/workspace/.venv/bin:$PATH"
ENV LITESTAR_APP="app.main:app"

# Expose the application port
EXPOSE 8000

# Run the Litestar application
CMD ["litestar","run", "--host", "0.0.0.0", "--port", "8000"]