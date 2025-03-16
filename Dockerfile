FROM rapidsai/base:25.04a-cuda12.8-py3.10-amd64

# Set the working directory inside the container
WORKDIR /app

# Copy requirements.txt into the container
COPY requirements.txt /app/requirements.txt

# Update package lists and install system dependencies (optional)
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set default command (optional)
CMD ["/bin/bash"]