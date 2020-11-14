FROM python:3.9-slim

# Create and set the working directory.
WORKDIR /usr/src/bot

# Configure pip to have cleaner logs and no saved cache.
ENV PIP_NO_CACHE_DIR=false \
    PIPENV_HIDE_EMOJIS=1 \
    PIPENV_IGNORE_VIRTUALENVS=1 \
    PIPENV_NOSPIN=1

# Update system and install dependencies.
RUN apt update && apt upgrade -y && apt install -y \
    git \
    libuv0.10-dev

# Install pipenv.
RUN pip install -U pipenv

# Install bot dependencies.
COPY Pipfile* .
RUN pipenv install --system --deploy

# Copy source code last to optimize rebuilding speed of the image.
COPY . .

# Launch the bot application through pipenv.
ENTRYPOINT ["pipenv"]
CMD ["run", "bot"]
