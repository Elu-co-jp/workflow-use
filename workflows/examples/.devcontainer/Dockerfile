ARG VARIANT="3.12-bookworm"
FROM python:${VARIANT}

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
        firefox-esr \
        wget \
        gnupg \
        unzip \
        xvfb \
        libxi6 \
        libgconf-2-4 \
        libnss3 \
        libxss1 \
        libappindicator3-1 \
        libasound2 \
        libatk-bridge2.0-0 \
        libgtk-3-0 \
        ca-certificates \
        fonts-liberation \
        libgbm1 \
    && apt-get clean -y && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv to PATH for all users
ENV PATH="/root/.cargo/bin:${PATH}"

# Create a non-root user
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
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

# Expose common ports
EXPOSE 8000 8080