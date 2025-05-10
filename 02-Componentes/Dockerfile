FROM python:3.10
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r Tests/requirements.txt
ENV PYTHONPATH=/app
ENTRYPOINT ["python", "-m", "unittest", "-v"]