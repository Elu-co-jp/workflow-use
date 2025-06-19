FROM ghcr.io/keito4/config-base:1.0.13

# Install system dependencies
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
        curl \
        git \
        build-essential \
        libssl-dev \
        libffi-dev \
        python3-dev \
        chromium \
        chromium-driver \
        firefox \
        wget \
        gnupg \
        unzip \
        xvfb \
        libxi6 \
        libnss3 \
        libxss1 \
        libappindicator3-1 \
        libasound2t64 \
        libatk-bridge2.0-0 \
        libgtk-3-0 \
        ca-certificates \
        fonts-liberation \
        libgbm1 \
        # Japanese fonts
        fonts-ipafont-gothic \
        fonts-ipafont-mincho \
        fonts-noto-cjk \
        fonts-noto-color-emoji \
        # VNC and noVNC dependencies
        x11vnc \
        xvfb \
        fluxbox \
        novnc \
        websockify \
        supervisor \
    && apt-get clean -y && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv to PATH for all users
ENV PATH="/root/.cargo/bin:${PATH}"

# Create a non-root user
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN if ! getent group $USERNAME > /dev/null 2>&1; then \
        groupadd --gid $USER_GID $USERNAME; \
    fi \
    && if ! getent passwd $USERNAME > /dev/null 2>&1; then \
        useradd --uid $USER_UID --gid $USER_GID -m $USERNAME; \
    fi \
    && apt-get update \
    && apt-get install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# Switch to non-root user
USER $USERNAME

# Install uv for the non-root user
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv to PATH for the user
ENV PATH="/home/${USERNAME}/.cargo/bin:${PATH}"

# Create workspace directory
RUN mkdir -p /home/${USERNAME}/workspace

WORKDIR /home/${USERNAME}/workspace

# Set environment variables for browser automation
ENV DISPLAY=:99
ENV PYTHONUNBUFFERED=1

# Create VNC startup script
RUN mkdir -p /home/${USERNAME}/.vnc /home/${USERNAME}/.config/supervisor

# Configure supervisor for VNC and noVNC
RUN echo "[supervisord]\n\
nodaemon=true\n\
user=${USERNAME}\n\
\n\
[program:xvfb]\n\
command=/usr/bin/Xvfb :99 -screen 0 1280x1024x24\n\
autorestart=true\n\
user=${USERNAME}\n\
priority=100\n\
\n\
[program:x11vnc]\n\
command=/usr/bin/x11vnc -display :99 -nopw -listen localhost -xkb -ncache 10 -ncache_cr -forever\n\
autorestart=true\n\
user=${USERNAME}\n\
priority=200\n\
\n\
[program:fluxbox]\n\
command=/usr/bin/fluxbox\n\
autorestart=true\n\
user=${USERNAME}\n\
environment=DISPLAY=:99\n\
priority=300\n\
\n\
[program:novnc]\n\
command=/usr/bin/websockify --web /usr/share/novnc/ 6080 localhost:5900\n\
autorestart=true\n\
user=${USERNAME}\n\
priority=400" > /home/${USERNAME}/.config/supervisor/supervisord.conf

# Expose common ports
EXPOSE 8000 8080 5900 6080
