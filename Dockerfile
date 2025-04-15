FROM python:3

# Install required packages (optional - based on what your main.py needs)
# RUN pip install -r requirements.txt

COPY . .

# Run the Python script
CMD ["python", "datafile/main.py"]
