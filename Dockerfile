FROM python:3.11-slim

# Metadata
LABEL organization="Trend"
LABEL description="Trend backend service"

# Install system dependencies
RUN apt-get update
RUN apt-get install -y gettext

# Install GDAL dependencies
RUN apt-get install -y --no-install-recommends \
    gdal-bin \
    libgdal-dev \
    python3-gdal

# No need for byte code in the container.
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create a directory for our workspace.
RUN mkdir /workspace/
WORKDIR /workspace/

COPY ./requirements /requirements
RUN pip install --no-cache-dir -r /requirements/dev.txt \
    && rm -rf /requirements
RUN pip install --no-cache-dir --upgrade pip

# Copy project source to the container.
RUN mkdir ./trend-backend/
COPY . ./trend-backend/

# Use non-root user for safety.
RUN adduser --disabled-password --gecos "" django
RUN chown -R django:django /workspace/
USER django

# Change work directory to our project's directory.
WORKDIR ./trend-backend/
