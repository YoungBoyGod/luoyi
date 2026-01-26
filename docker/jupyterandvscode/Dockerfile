FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# 基础工具
RUN apt-get update && apt-get install -y \
    openssh-server \
    sudo \
    curl \
    git \
    vim \
    tmux \
    python3 \
    python3-pip \
    net-tools \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# SSH
RUN mkdir /var/run/sshd

# 创建用户
RUN useradd -m -s /bin/bash gpuuser && \
    echo "gpuuser ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Python
RUN pip3 install --no-cache-dir \
    jupyterlab \
    ipykernel

# VSCode Web
RUN curl -fsSL https://code-server.dev/install.sh | sh

# SSH 配置
RUN sed -i 's/#Port 22/Port 22/' /etc/ssh/sshd_config && \
    sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config && \
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config

EXPOSE 22 8888 8080 9000-9100

# 复制启动脚本
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

WORKDIR /home/gpuuser

# 启动脚本（以 root 运行，内部会切换到 gpuuser）
CMD ["/entrypoint.sh"]
