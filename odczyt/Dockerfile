FROM public.ecr.aws/docker/library/python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 libgomp1 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
ENV PADDLE_PDX_MODEL_SOURCE=huggingface PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK=True
COPY czytaj.py .
# Importing the module downloads the models into the image.
RUN python -c "import czytaj"
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
