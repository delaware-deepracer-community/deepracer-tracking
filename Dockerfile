# From deepracer utils base image
FROM naveengh6/deepracer-utils:latest

# cd to user directory
WORKDIR /home/pyuser

# Create app directory
RUN mkdir tracking

# Copy all files
COPY . tracking/
RUN chown -R pyuser tracking

# changing user
USER pyuser

# Install pip requirements
RUN python -m pip install -r requirements.txt

# Run application
CMD ["python", "main.py"]