FROM python:3.9-alpine

# Create and set the working directory.
WORKDIR /usr/src/bot

# Configure pip to have cleaner logs and no saved cache.
ENV PIP_NO_CACHE_DIR=false \
    PIPENV_HIDE_EMOJIS=1 \
    PIPENV_IGNORE_VIRTUALENVS=1 \
    PIPENV_NOSPIN=1

# Update system and install dependencies.
RUN apk add --no-cache gcc musl-dev make libffi-dev openssl-dev libuv postgresql-dev

# Install pipenv.
RUN pip install -U pipenv

# Install bot dependencies.
COPY Pipfile* .
RUN pipenv install --system --deploy

# Copy source code last to optimize rebuilding speed of the image.
COPY . .

# Launch the bot application through pipenv and run database migrations.
ENTRYPOINT ["pipenv"]
CMD ["run", "migrations"]
CMD ["run", "bot"]
