FROM python:3.10-slim

# Avoid interactive prompts (timezone)
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update && \
    TZ=Etc/UTC apt install -y tzdata && \
    apt install -y ffmpeg git curl && \
    apt clean

# Set working directory
WORKDIR /app

ENV PYTHONPATH="/app"

# Install your app dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

RUN mkdir -p uploads outputs

# Copy your FastAPI app and frontend files
COPY app ./app
COPY static ./static
COPY uploads ./uploads

# Start FastAPI app using uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
