#!/bin/bash
# 监控CPU/内存/磁盘（用top/free/df），超过阈值邮件SMTP告警；自动清理旧日志。
LOG_DIR="/var/log/nginx"
THRESHOLD_CPU=90
THRESHOLD_MEM=80
THRESHOLD_DISK=90
EMAIL="245027231@qq.com"

# 获取当前使用率、处理百分号
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print int($2)}')
# %Cpu(s):  1.0 us,  1.0 sy,  0.0 ni, 98.0 id,  0.0 wa,  0.0 hi,  0.0 si,  0.0 st

MEM_USAGE=$(free | awk 'NR==2{printf "%.0f", $3*100/$2 }')
#               total        used        free      shared  buff/cache   available
#Mem:         7766180     1255160     5097952       70040     1745820     6511020
#Swap:              0           0           0

DISK_USAGE=$(df / | awk 'NR==2{print int($5)}')

# 日志清理
find $LOG_DIR -name "*.log" -mtime +7 -delete

# 告警
# -gt: "Greater Than" 
if [ $CPU_USAGE -gt $THRESHOLD_CPU ]; then
  echo "⚠️ CPU usage is ${CPU_USAGE}% (threshold: ${THRESHOLD_CPU}%)" | mail -s "[ALERT] High CPU Usage" $EMAIL
fi

if [ $MEM_USAGE -gt $THRESHOLD_MEM ]; then
  echo "⚠️ Memory usage is ${MEM_USAGE}% (threshold: ${THRESHOLD_MEM}%)" | mail -s "[ALERT] High Memory Usage" $EMAIL
fi

if [ $DISK_USAGE -gt $THRESHOLD_DISK ]; then
  echo "⚠️ Disk usage is ${DISK_USAGE}% (threshold: ${THRESHOLD_DISK}%)" | mail -s "[ALERT] High Disk Usage" $EMAIL
fi