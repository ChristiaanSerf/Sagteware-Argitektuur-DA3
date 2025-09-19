FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt
COPY app.py .
EXPOSE 5004
CMD ["python","app.py"]
