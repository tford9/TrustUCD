FROM  nvcr.io/nvidia/rapidsai/base:25.02-cuda12.8-py3.12

# Install sudo
RUN apt-get update && apt-get install -y sudo

# Create user 'myuser' and add to sudoers
RUN useradd -m -s /bin/bash 260433 && \
    echo "260433 ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Set the working directory inside the container
WORKDIR /app

# Copy requirements.txt into the container
COPY requirements.txt /app/requirements.txt

# Install Python dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set default command (optional)
#CMD ["/bin/bash"]

