# Use the official Python image as a base
FROM python:3.11

# Set the working directory inside the container
WORKDIR /app

# Copy the application code to the container
COPY . .

# Install dependencies
RUN pip install -r requirements.txt

# RUN python manage.py collectstatic --noinput

EXPOSE 8000

# Define environment variables for RabbitMQ and Redis
# ENV RABBITMQ_HOST=rabbitmq
# ENV RABBITMQ_USER=user
# ENV RABBITMQ_PASS=password
# ENV REDIS_HOST=redis
# ENV DJANGO_SETTINGS_MODULE=chat_service.settings

# Run database migrations and start the Daphne ASGI server
CMD ["sh", "-c", "sleep 10 && python manage.py migrate && daphne -b 0.0.0.0 -p 8000 chat_service.asgi:application"]
