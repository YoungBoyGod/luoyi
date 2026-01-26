#!/bin/bash

# 自动修复挂载目录的权限
chown -R gpuuser:gpuuser /home/gpuuser

# 配置 SSH 密钥认证
SSH_DIR="/home/gpuuser/.ssh"
PRIVATE_KEY="$SSH_DIR/id_rsa"
PUBLIC_KEY="$SSH_DIR/id_rsa.pub"
AUTHORIZED_KEYS="$SSH_DIR/authorized_keys"

# 如果 .ssh 目录不存在，创建它
if [ ! -d "$SSH_DIR" ]; then
    mkdir -p "$SSH_DIR"
    chown gpuuser:gpuuser "$SSH_DIR"
    chmod 700 "$SSH_DIR"
fi

# 如果密钥不存在，自动生成
if [ ! -f "$PRIVATE_KEY" ]; then
    echo "生成 SSH 密钥对..."
    su - gpuuser -c "ssh-keygen -t rsa -b 4096 -f $PRIVATE_KEY -N '' -C 'gpuuser@workspace'"
    cat "$PUBLIC_KEY" >> "$AUTHORIZED_KEYS"
    chmod 600 "$AUTHORIZED_KEYS"
    chown gpuuser:gpuuser "$AUTHORIZED_KEYS"
    echo "SSH 密钥已生成，私钥位置: $PRIVATE_KEY"
fi

# 如果 authorized_keys 不存在，从公钥创建
if [ ! -f "$AUTHORIZED_KEYS" ]; then
    if [ -f "$PUBLIC_KEY" ]; then
        cat "$PUBLIC_KEY" >> "$AUTHORIZED_KEYS"
        chmod 600 "$AUTHORIZED_KEYS"
        chown gpuuser:gpuuser "$AUTHORIZED_KEYS"
    fi
fi

# 启动 SSH
/usr/sbin/sshd

# 以 gpuuser 身份运行 Jupyter
su - gpuuser -c "jupyter lab \
  --ip=0.0.0.0 \
  --port=8888 \
  --no-browser \
  --NotebookApp.token='' \
  --NotebookApp.password='' \
  --NotebookApp.allow_origin='*' &"

# 以 gpuuser 身份运行 VSCode Web
su - gpuuser -c "code-server \
  --bind-addr 0.0.0.0:8080 \
  --auth none &"

# 容器保活
tail -f /dev/null
