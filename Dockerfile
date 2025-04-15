FROM python:3.11-slim

WORKDIR /app

# Copy requirements file from datafile directory and install dependencies
COPY datafile/requirement.txt ./requirement.txt
RUN pip install --no-cache-dir -r requirement.txt

# Copy the rest of the code
COPY . .

EXPOSE 8000

# Start FastAPI app (update the path if your FastAPI app is not datafile/main.py:app)
CMD ["uvicorn", "datafile.main:app", "--host", "0.0.0.0", "--port", "8000"]