package main

import (
	"bufio"
	"context"
	"fmt"
	"os"
	"os/exec"
	"os/signal"
	"strings"
	"syscall"
	"time"
)

const logFile = "ban_ip.txt"

func runCmd(cmdStr string) (string, error) {
	cmd := exec.Command("sh", "-c", cmdStr)
	output, err := cmd.Output()
	if err != nil {
		return "", err
	}
	return string(output), nil
}

func logBan(ip string) error {
	f, err := os.OpenFile(logFile, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0644)
	if err != nil {
		return err
	}
	defer f.Close()

	timestamp := time.Now().Format("2006-01-02 15:04:05")
	line := fmt.Sprintf("[%s] BANNED IP: %s\n", timestamp, ip)
	_, err = f.WriteString(line)
	return err
}

func main() {
	// 设置循环
	interval := 20 //5min

	// 记录一下已经ban的ip
	bannedIPs := make(map[string]bool)

	// 从日志中加载。
	if file, err := os.Open(logFile); err != nil {
		scanner := bufio.NewScanner(file)
		for scanner.Scan() {
			line := scanner.Text()
			// 解析日志
			if strings.Contains(line, "BANNED IP: ") {
				parts := strings.Split(line, "BANNED IP: ")
				if len(parts) == 2 {
					ip := strings.TrimSpace(parts[1])
					bannedIPs[ip] = true
				}
			}
		}
		file.Close()
		fmt.Printf("✅ 已从日志加载 %d 个历史封禁IP\n", len(bannedIPs))
	}

	// 如果被中断就退出
	ctx, cancel := context.WithCancel((context.Background()))
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)
	go func() {
		<-sigChan
		fmt.Println("\n 收到了中断信号，正在退出。。。")
		cancel()
	}()
	fmt.Printf("🚀 启动暴力破解IP自动封禁监控（每 %d 秒检查一次）\n", interval)
	fmt.Printf("📝 日志文件: %s\n\n", logFile)
	// 主循环
	for {
		select {
		case <-ctx.Done():
			fmt.Println("程序已经退出")
			return
		default:
		}
		fmt.Println("🔍 开始获取需封禁的IP列表...")

		// 1. get need ban ip
		cmdGetNeedBanIP := "lastb | awk '{print $3}' |uniq | sort|uniq  | grep -v T "
		ipListStr, err := runCmd(cmdGetNeedBanIP)
		if err != nil {
			fmt.Printf("⚠️ 获取IP失败: %v\n", err)
			time.Sleep(time.Duration(interval) * time.Second)
			continue
		}

		// 2. ban it
		scanner := bufio.NewScanner(strings.NewReader(ipListStr))
		newBanCount := 0

		for scanner.Scan() {
			ip := strings.TrimSpace(scanner.Text())
			if ip == "" || bannedIPs[ip] {
				continue
			}
			fmt.Printf("处理IP: %s\n", ip)
			// 验证是否为合法ip
			denyCmd := fmt.Sprintf("ufw deny from %s", ip)
			_, err := runCmd(denyCmd)
			if err != nil {
				fmt.Printf("封禁ip %s 失败: %v\n", ip, err)

			} else {
				bannedIPs[ip] = true
				if err := logBan(ip); err != nil {
					fmt.Printf("❗ 写入日志失败 %s: %v\n", ip, err)
				} else {
					newBanCount++
					fmt.Printf("✅ 成功封禁并记录日志: %s\n", ip)
				}

			}
		}

		if newBanCount == 0 {
			fmt.Println("本轮没有新的IP需要封禁")
		} else {
			fmt.Printf("本轮共封禁 %d 个 新的ip。\n", newBanCount)
		}

		// 3. check ufw status
		ufwStatus, err := runCmd("ufw status")
		if err != nil {
			fmt.Printf("获取ufw状态失败: %v\n", err)
		} else {
			fmt.Println("UFW 状态:\n", ufwStatus)
		}
		//  把已经ban的写入到log中

		fmt.Printf("⏳ 等待 %d 秒后下一轮检查...\n\n", interval)
		fmt.Println()
		countdown(interval)
		fmt.Println()
	}
}

func countdown(seconds int) {
	for i := seconds; i > 0; i-- {
		fmt.Printf("\r⏳ 下一轮检查将在 %d 秒后开始... ", i)
		time.Sleep(1 * time.Second)
	}
	fmt.Println("\r✅ 立即开始下一轮检查！           ") // 清除倒计时行
}
