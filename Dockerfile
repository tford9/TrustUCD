FROM  nvcr.io/nvidia/rapidsai/base:25.02-cuda12.8-py3.12

# Set the working directory inside the container
WORKDIR /app

# Copy requirements.txt into the container
COPY requirements.txt /app/requirements.txt

# Install Python dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set default command (optional)
#CMD ["/bin/bash"]

