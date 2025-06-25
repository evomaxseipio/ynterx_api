

# Use a Python base image
FROM python:3.11-slim


# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential

# Copy the requirements file into the container at /app
COPY ./requirements.txt /app/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container at /app
COPY . /app

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application using Uvicorn
# Adjust 'main:app' to your_module:your_fastapi_instance
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
