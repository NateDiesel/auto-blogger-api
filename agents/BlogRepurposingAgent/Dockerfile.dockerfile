#Dockerfile

# Use a lightweight Python image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy everything from your local folder to the container
COPY . .

# Install dependencies
RUN pip install flask requests keyring apscheduler requests_oauthlib

# Expose the Flask port (5000 by default)
EXPOSE 5000

# Run the Flask app
CMD ["python", "BlogRepurposingAgent.py"]
