#!/bin/bash

# 自动修复挂载目录的权限
chown -R gpuuser:gpuuser /home/gpuuser

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
