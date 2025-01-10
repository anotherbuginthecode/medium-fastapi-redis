# Use the official Python base image
FROM --platform=linux/x86_64 python:3.11-slim-buster
ENV PYTHONBUFFERED=1 \
  TZ=Europe/Rome \
  LOG_LEVEL=INFO
RUN apt-get update -y
RUN apt-get install -y gcc g++ build-essential unzip dos2unix
RUN apt-get install -y libpq-dev
RUN apt-get update && apt-get install -y libcurl4-openssl-dev libssl-dev
RUN pip install --upgrade pip
# Set the working directory inside the container
WORKDIR /app
# Copy the requirements file to the working directory
COPY requirements.txt .
# Install the application dependencies
RUN pip install wheel pybind11
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code to the working directory
COPY . .

# Expose the port that FastAPI will run on
EXPOSE 8000
# Set the command to run the application
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]