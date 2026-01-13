# 项目1：自动化监控与备份系统

> “搭建了一套轻量级运维监控系统，覆盖资源告警、简单日志分析和数据库备份，但通过模拟真实故障（如cpu持续满载、服务宕机），掌握了从发现问题到恢复的完整链路，这正是运维工程师的核心能力。”

## 难点与心得：
- 正则表达式匹配日志文件
- mysql备份时，临时文件的使用
- Counterer 的使用
- 查阅oss官方文档，完善文件上传代码
- 备份文件压缩
- 避免在备份失败时尝试删除不存在的文件
- 增量备份（未实现）

## 🎯 目标
实现 Linux 服务器的资源监控、Nginx 日志分析、MySQL 自动备份，具备基础故障告警能力。

## 🛠️ 部署步骤
1. 在 Ubuntu 22.04 上安装 Nginx、MySQL
2. 配置阿里云OSS、SMTP邮箱、环境变量
3. 设置 crontab 定时任务

## 📊 优化与调优
- oss认证采用环境变量，避免明文存储
- 日志解析正则优化
- 备份文件增加压缩（gzip）

## 🚨 故障恢复案例
**问题**： `system_monitor.sh` 发送邮件告警，CPU使用率达90%，系统变慢
**排查**：`top`和`docker ps` 发现CPU被docker进程占用
**解决**：docker stop   进程，CPU恢复正常
**改进**：增加docker资源限制，避免CPU占用过高

# 笔记
## 部署nginx
```
sudo apt update
sudo apt install -y nginx mysql-server python3 python3-pip
sudo systemctl start nginx mysql
```
```
systemctl status nginx
systemctl status mysql
```
访问日志文件
/var/log/nginx/access.log

## 配置msmtp
```
sudo apt-get install msmtp msmtp-mta mailutils
sudo nano /etc/msmtprc
```
# qq邮箱
```
defaults
logfile /tmp/msmtp.log

account qq
host smtp.qq.com
port 587
auth on
tls on
tls_starttls on
user 245027231@qq.com
password ******
from 245027231@qq.com

account default : qq
```
```
sudo chmod 644 /etc/msmtprc # 否则报错non-zero status
sudo nano /etc/mail.rc
```
set sendmail="/usr/bin/msmtp -t"
```echo "QQ邮件测试" | mail -s "测试标题" 245027231@qq.com```

## 添加定时任务
crontab -e
```
*/5 * * * * /home/houjiasheng/system_monitor.sh >> /home/houjiasheng/monitor.log 2>&1

0 8 * * * /usr/bin/python3 /home/houjiasheng/nginx_log_analyzer.py >> /home/houjiasheng/log_analyzer.log 2>&1
*/1 * * * * /usr/bin/python3 /home/houjiasheng/backup_mysql_to_oss.py >> /home/houjiasheng/backup_mysql_to_oss.log 2>&1
```

## oss配置
> 参考:https://www.alibabacloud.com/help/zh/oss/developer-reference/2-0-manual-preview-version/?spm=a2c63.p38356.help-menu-31815.d_1_1_2.48d12c27NvxkIN
## 虚拟环境
```
python3 -m venv .venv
source .venv/bin/activate
pip install alibabacloud-oss-v2
```

## 环境变量
```
echo "export OSS_ACCESS_KEY_ID='LTAI5tR5E5AWQXXwCg9Yc19q'" >> ~/.bashrc
echo "export OSS_ACCESS_KEY_SECRET='******'" >> ~/.bashrc
source ~/.bashrc

echo $OSS_ACCESS_KEY_ID
echo $OSS_ACCESS_KEY_SECRET
```