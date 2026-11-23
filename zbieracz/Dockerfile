FROM public.ecr.aws/docker/library/python:3.15-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "z_pliku.py", "przyklad.jsonl"]
