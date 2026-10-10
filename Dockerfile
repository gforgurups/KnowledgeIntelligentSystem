FROM public.ecr.aws/docker/library/python:3.10-slim-buster

WORKDIR /app

# Copy requirements and install packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir --upgrade pydantic pydantic-core langchain && \
    pip install --no-cache-dir pysqlite3-binary langchain-classic

# Copy all repository contents into the container
COPY . .

# Run main.py inside the app directory
CMD ["python3", "app/main.py"]