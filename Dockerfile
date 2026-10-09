FROM public.ecr.aws/docker/library/python:3.10-slim-buster

WORKDIR /app

# 1. Copy requirements first to leverage Docker layer caching efficiently
COPY requirements.txt .

# 2. Install dependencies (explicitly adding pysqlite3-binary as a safety net)
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir pysqlite3-binary

# 3. Copy the rest of the application code
COPY . .

# 4. FIX: Run main.py directly from the current working directory (/app)
CMD ["python3", "app/main.py"]
