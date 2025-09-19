FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt
COPY ocr.py .
EXPOSE 5003
CMD ["python","ocr.py"]
