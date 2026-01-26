#!/bin/bash

# SSH 私钥获取和分发脚本
# 用途：自动获取容器生成的 SSH 私钥并生成用户使用说明

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
USER_ID="user001"
DATA_DIR="./data/${USER_ID}"
SSH_DIR="${DATA_DIR}/.ssh"
PRIVATE_KEY="${SSH_DIR}/id_rsa"
PUBLIC_KEY="${SSH_DIR}/id_rsa.pub"
OUTPUT_DIR="./ssh_keys"
SERVER_IP="localhost"  # 修改为实际服务器 IP
SSH_PORT="2222"

# 显示标题
echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}   SSH 私钥获取和分发工具${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# 检查容器是否运行
if ! docker ps | grep -q "${USER_ID}-workspace"; then
    echo -e "${RED}[错误] 容器未运行，请先启动容器：${NC}"
    echo "  docker-compose up -d"
    exit 1
fi

# 检查私钥是否存在
if [ ! -f "$PRIVATE_KEY" ]; then
    echo -e "${RED}[错误] 私钥文件不存在：${PRIVATE_KEY}${NC}"
    echo -e "${YELLOW}[提示] 请等待容器启动完成后再试${NC}"
    echo "  docker-compose logs -f"
    exit 1
fi

echo -e "${GREEN}[成功] 找到私钥文件${NC}"
echo ""

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

# 1. 复制私钥
PRIVATE_KEY_COPY="${OUTPUT_DIR}/${USER_ID}_id_rsa"
cp "$PRIVATE_KEY" "$PRIVATE_KEY_COPY"
chmod 600 "$PRIVATE_KEY_COPY"

echo -e "${GREEN}[完成] 私钥已复制到：${NC}"
echo "  ${PRIVATE_KEY_COPY}"
echo ""

# 2. 复制公钥
if [ -f "$PUBLIC_KEY" ]; then
    PUBLIC_KEY_COPY="${OUTPUT_DIR}/${USER_ID}_id_rsa.pub"
    cp "$PUBLIC_KEY" "$PUBLIC_KEY_COPY"
    echo -e "${GREEN}[完成] 公钥已复制到：${NC}"
    echo "  ${PUBLIC_KEY_COPY}"
    echo ""
fi

# 3. 生成用户使用说明
INSTRUCTIONS="${OUTPUT_DIR}/${USER_ID}_使用说明.txt"

cat > "$INSTRUCTIONS" << 'EOF'
╔══════════════════════════════════════════════════════════════╗
║            GPU Workspace SSH 登录说明                        ║
╚══════════════════════════════════════════════════════════════╝

【连接信息】
- 用户名: gpuuser
- 服务器: SERVER_IP
- 端口: SSH_PORT
- 私钥: USER_ID_id_rsa

【快速开始】

1. 保存私钥文件
   将 USER_ID_id_rsa 文件保存到本地，例如：
   - Windows: C:\Users\你的用户名\.ssh\workspace_key
   - Linux/Mac: ~/.ssh/workspace_key

2. 设置私钥权限（Linux/Mac）
   chmod 600 ~/.ssh/workspace_key

3. 使用 SSH 连接
   ssh -i ~/.ssh/workspace_key -p SSH_PORT gpuuser@SERVER_IP

【VSCode Remote SSH 配置】

1. 安装扩展
   在 VSCode 中搜索并安装 "Remote - SSH"

2. 配置 SSH
   按 F1 → 输入 "Remote-SSH: Open SSH Configuration File"
   添加以下配置：

   Host workspace-USER_ID
       HostName SERVER_IP
       Port SSH_PORT
       User gpuuser
       IdentityFile ~/.ssh/workspace_key
       StrictHostKeyChecking no

   Windows 用户 IdentityFile 示例：
       IdentityFile C:\Users\你的用户名\.ssh\workspace_key

3. 连接
   按 F1 → 输入 "Remote-SSH: Connect to Host"
   选择 "workspace-USER_ID"

【可用服务】

- SSH: ssh -p SSH_PORT gpuuser@SERVER_IP
- Jupyter Lab: http://SERVER_IP:18888
- VSCode Web: http://SERVER_IP:18080

【端口转发】

如果需要从远程容器访问本地服务：
ssh -i ~/.ssh/workspace_key -p SSH_PORT -L 本地端口:localhost:远程端口 gpuuser@SERVER_IP

示例（转发 TensorBoard）：
ssh -i ~/.ssh/workspace_key -p SSH_PORT -L 6006:localhost:6006 gpuuser@SERVER_IP

【故障排查】

1. 连接被拒绝
   - 检查服务器 IP 和端口是否正确
   - 检查防火墙设置
   - 确认容器是否运行：docker ps

2. Permission denied (publickey)
   - Linux/Mac: 确保私钥权限为 600
   - Windows: 右键私钥 → 属性 → 安全 → 只保留当前用户的完全控制权限

3. Host key verification failed
   删除已知主机记录：
   ssh-keygen -R [SERVER_IP]:SSH_PORT

【安全建议】

⚠️ 私钥文件非常重要，请：
  - 不要分享给其他人
  - 不要上传到公共仓库
  - 不要通过不安全的渠道传输
  - 定期备份

【支持】

如遇问题请联系管理员。

═══════════════════════════════════════════════════════════════
EOF

# 替换占位符
sed -i "s/SERVER_IP/${SERVER_IP}/g" "$INSTRUCTIONS"
sed -i "s/SSH_PORT/${SSH_PORT}/g" "$INSTRUCTIONS"
sed -i "s/USER_ID/${USER_ID}/g" "$INSTRUCTIONS"

echo -e "${GREEN}[完成] 用户说明已生成：${NC}"
echo "  ${INSTRUCTIONS}"
echo ""

# 4. 生成 VSCode SSH Config
SSH_CONFIG="${OUTPUT_DIR}/${USER_ID}_ssh_config"

cat > "$SSH_CONFIG" << EOF
# 将以下内容添加到你的 SSH 配置文件中
# Linux/Mac: ~/.ssh/config
# Windows: C:\Users\你的用户名\.ssh\config

Host workspace-${USER_ID}
    HostName ${SERVER_IP}
    Port ${SSH_PORT}
    User gpuuser
    IdentityFile ~/.ssh/workspace_key
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
EOF

echo -e "${GREEN}[完成] SSH Config 配置已生成：${NC}"
echo "  ${SSH_CONFIG}"
echo ""

# 5. 显示私钥内容（可选）
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}是否显示私钥内容？(可直接复制发送给用户) [y/N]${NC}"
read -r show_key

if [[ "$show_key" =~ ^[Yy]$ ]]; then
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━ 私钥内容 ━━━━━━━━━━━━━━━━${NC}"
    cat "$PRIVATE_KEY"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
fi

# 6. 生成分发包
PACKAGE="${OUTPUT_DIR}/${USER_ID}_ssh_package.tar.gz"
cd "$OUTPUT_DIR"
tar -czf "${USER_ID}_ssh_package.tar.gz" "${USER_ID}_id_rsa" "${USER_ID}_使用说明.txt" "${USER_ID}_ssh_config" 2>/dev/null || true
cd - > /dev/null

if [ -f "$PACKAGE" ]; then
    echo -e "${GREEN}[完成] 分发包已生成：${NC}"
    echo "  ${PACKAGE}"
    echo ""
    echo -e "${YELLOW}[提示] 可以直接将此压缩包发送给用户${NC}"
fi

# 总结
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✓ 私钥获取完成！${NC}"
echo ""
echo -e "${YELLOW}【下一步操作】${NC}"
echo ""
echo -e "1. 发送给用户："
echo -e "   ${GREEN}整个目录：${NC} ${OUTPUT_DIR}/"
echo -e "   ${GREEN}或压缩包：${NC} ${PACKAGE}"
echo ""
echo -e "2. 测试连接："
echo -e "   ${GREEN}ssh -i ${PRIVATE_KEY_COPY} -p ${SSH_PORT} gpuuser@${SERVER_IP}${NC}"
echo ""
echo -e "3. 查看所有文件："
echo -e "   ${GREEN}ls -lh ${OUTPUT_DIR}/${NC}"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
