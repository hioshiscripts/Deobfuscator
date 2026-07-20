FROM python:3.10-slim

# Install Lua 5.1
RUN apt-get update && apt-get install -y \
    lua5.1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
