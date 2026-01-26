# 快速开始指南

## 1. 构建并启动容器

```bash
# 构建镜像
docker build -t gpu-workspace:latest .

# 启动容器（SSH 密钥会自动生成）
docker-compose up -d

# 查看启动日志
docker-compose logs -f
```

## 2. 获取 SSH 私钥（自动化）

运行脚本自动获取私钥：

```bash
./get_ssh_key.sh
```

脚本会自动：
- ✅ 提取私钥和公钥
- ✅ 生成用户使用说明
- ✅ 生成 SSH 配置文件
- ✅ 打包所有文件为压缩包

生成的文件在 `./ssh_keys/` 目录：
```
ssh_keys/
├── user001_id_rsa              # 私钥（发给用户）
├── user001_id_rsa.pub          # 公钥（仅供参考）
├── user001_使用说明.txt        # 详细使用说明
├── user001_ssh_config          # SSH 配置模板
└── user001_ssh_package.tar.gz  # 完整分发包
```

## 3. 分发给用户

### 方式1：发送压缩包（推荐）

```bash
# 将压缩包通过安全渠道发送给用户
./ssh_keys/user001_ssh_package.tar.gz
```

### 方式2：单独发送私钥

```bash
# 显示私钥内容（用户可直接复制）
cat ./ssh_keys/user001_id_rsa
```

## 4. 用户连接测试

用户收到私钥后，按照说明文档操作即可。

**快速测试命令：**
```bash
ssh -i ~/.ssh/workspace_key -p 2222 gpuuser@服务器IP
```

## 5. 多用户管理

如需创建多个用户工作空间，修改 `get_ssh_key.sh` 中的配置：

```bash
USER_ID="user002"        # 改为新的用户 ID
SSH_PORT="2223"          # 使用不同的端口
```

或复制整个目录结构：
```bash
cp -r allinone user002-workspace
cd user002-workspace
# 修改 docker-compose.yml 中的端口映射
```

## 访问服务

容器启动后可访问：

| 服务 | 地址 | 说明 |
|------|------|------|
| SSH | `localhost:2222` | 用于命令行和 VSCode Remote |
| Jupyter Lab | http://localhost:18888 | Web 界面，无需密码 |
| VSCode Web | http://localhost:18080 | 浏览器版 VSCode |

## 故障排查

### 私钥不存在
```bash
# 检查容器日志
docker-compose logs | grep "SSH 密钥"

# 重启容器
docker-compose restart
```

### 连接被拒绝
```bash
# 检查容器状态
docker-compose ps

# 检查 SSH 服务
docker exec user001-workspace ps aux | grep sshd
```

### 权限问题
```bash
# 修复数据目录权限
sudo chown -R 1000:1000 ./data/user001
docker-compose restart
```

## 安全建议

⚠️ **重要提醒：**

1. **私钥安全**
   - 通过加密渠道传输（加密邮件、企业 IM）
   - 不要上传到 Git 仓库
   - 不要通过明文聊天工具发送

2. **服务器安全**
   - 修改默认端口号
   - 配置防火墙规则
   - 定期更新容器镜像

3. **密钥轮换**
   ```bash
   # 删除旧密钥，重启容器会自动生成新密钥
   rm -rf ./data/user001/.ssh/
   docker-compose restart
   ```

## 自定义配置

### 修改服务器 IP 和端口

编辑 `get_ssh_key.sh`：
```bash
SERVER_IP="your-server-ip"  # 改为实际服务器 IP
SSH_PORT="2222"             # 改为实际映射端口
```

### 使用用户自己的公钥

```bash
# 将用户的公钥追加到 authorized_keys
cat user_public_key.pub >> ./data/user001/.ssh/authorized_keys

# 重启容器
docker-compose restart
```

## 完整工作流程示例

```bash
# 管理员操作
cd /path/to/allinone
docker-compose up -d
./get_ssh_key.sh
# 发送 ssh_keys/user001_ssh_package.tar.gz 给用户

# ─────────────────────────────

# 用户操作
tar -xzf user001_ssh_package.tar.gz
mv user001_id_rsa ~/.ssh/workspace_key
chmod 600 ~/.ssh/workspace_key
ssh -i ~/.ssh/workspace_key -p 2222 gpuuser@服务器IP
```

完成！
