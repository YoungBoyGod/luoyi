package main

import (
	"bufio"
	"fmt"
	"os/exec"
	"strings"
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

	// 1. get need ban ip
	cmdGetNeedBanIP := "lastb | awk '{print $3}' |uniq | sort|uniq  | grep -v T "
	ipListStr, err := runCmd(cmdGetNeedBanIP)
	if err != nil {
		fmt.Printf("获取需要ban的ip列表失败 %v\n", err)
		return
	}

	// 2. ban it
	scanner := bufio.NewScanner(strings.NewReader(ipListStr))
	for scanner.Scan() {
		ip := strings.TrimSpace(scanner.Text())
		if ip == "" {
			continue
		}
		fmt.Printf("处理IP: %s\n", ip)
		// 验证是否为合法ip
		denyCmd := fmt.Sprintf("ufw deny from %s", ip)
		_, err := runCmd(denyCmd)
		if err != nil {
			fmt.Printf("封禁ip %s 失败: %v\n", ip, err)

		} else {
			fmt.Printf("成功封禁ip: %s\n", ip)
		}
	}
	if err := scanner.Err(); err != nil {
		fmt.Printf("读取IP时出错: %v\n", err)
	}
	// 3. check ufw status
	ufwStatus, err := runCmd("ufw status")
	if err != nil {
		fmt.Printf("获取ufw状态失败: %v\n", err)
	} else {
		fmt.Println("UFW 状态:\n", ufwStatus)
	}

}
