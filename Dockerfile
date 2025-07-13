FROM debian:sid

# Add build argument for development dependencies
ARG INSTALL_DEV=false

# Use official Debian repositories instead of mirror
RUN rm -f /etc/apt/sources.list.d/* && \
    echo 'deb http://deb.debian.org/debian sid main' > /etc/apt/sources.list && \
    echo 'deb-src http://deb.debian.org/debian sid main' >> /etc/apt/sources.list

RUN apt update && apt upgrade -y && \
    apt install -y python3 python3-dev python3-pip python3-venv \
    locales git curl vim nano sqlite3 && \
    apt autoclean && apt -y autoremove && \
    rm -rf /var/lib/apt/lists/*

RUN sed -i '/th_TH.UTF-8/s/^# //g' /etc/locale.gen && locale-gen

# Create non-root user for development
RUN useradd --create-home --shell /bin/bash app

RUN python3 -m venv /venv
ENV PYTHON=/venv/bin/python3

RUN $PYTHON -m pip install wheel poetry

WORKDIR /app
COPY poetry.lock pyproject.toml README.md /app/

# Install dependencies - include dev dependencies if INSTALL_DEV is true
RUN . /venv/bin/activate \
    && poetry config virtualenvs.create false \
    && if [ "$INSTALL_DEV" = "true" ]; then \
    poetry install --no-interaction --no-root; \
    else \
    poetry install --no-interaction --only main --no-root; \
    fi

COPY . /app

# Change ownership to app user for development
RUN if [ "$INSTALL_DEV" = "true" ]; then chown -R app:app /app /venv; fi

EXPOSE 8000

# Use different command for development vs production
CMD if [ "$INSTALL_DEV" = "true" ]; then \
    su app -c "/venv/bin/python3 -m fastapi dev flasx/main.py --host 0.0.0.0 --port 8000"; \
    else \
    /venv/bin/python3 -m fastapi run flasx/main.py; \
    fi
