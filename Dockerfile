FROM  nvcr.io/nvidia/rapidsai/base:25.02-cuda12.0-py3.12

SHELL ["/bin/sh", "-c"]
USER root
RUN groupadd -g 50038 faislab && \
    useradd -u 260433 -g faislab -m twford

RUN usermod -aG sudo twford

# Set the working directory inside the container
WORKDIR /app

# Copy requirements.txt into the container
COPY requirements.txt /app/requirements.txt

# Install Python dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

USER root
RUN chmod -R 775 /home/ && chmod -R 775 /opt/conda/ && \
    chmod -R 775 /opt/conda/ && chmod -R 775 /usr/local/ && \
    chmod -R 775 /usr/sbin  && chmod -R 775 /usr/bin && chmod -R 775 /sbin && \
    chmod -R 775 /bin


# Set default command (optional)
#CMD ["/bin/bash"]

