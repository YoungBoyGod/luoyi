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

func runCmd(cmdStr string) (string, error) {
	cmd := exec.Command("sh", "-c", cmdStr)
	output, err := cmd.Output()
	if err != nil {
		return "", err
	}
	return string(output), nil
}

func main() {
	// 设置循环
	interval := 20 //5min

	// 记录一下已经ban的ip
	bannedIPs := make(map[string]bool)

	// 如果被中断就退出
	ctx, cancel := context.WithCancel((context.Background()))
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)
	go func() {
		<-sigChan
		fmt.Println("\n 收到了中断信号，正在退出。。。")
		cancel()
	}()
	fmt.Printf("开始监控 lastb 日志，每 %d 秒运行一次...\n", interval)

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
			fmt.Printf("获取需要ban的ip列表失败 %v\n", err)
			return
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
				newBanCount++
				fmt.Printf("成功封禁ip: %s\n", ip)
			}
		}
		if err := scanner.Err(); err != nil {
			fmt.Printf("读取IP时出错: %v\n", err)
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
		time.Sleep(time.Duration(interval) * time.Second)

	}
}
