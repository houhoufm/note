import re
import subprocess
from collections import Counter
from datetime import datetime

# 解析Nginx日志，统计Top IP/错误码，生成日报发送邮件

LOG_FILE = "/var/log/nginx/access.log"
EMAIL_TO = "245027231@qq.com"

LOG_PATTERN = re.compile(r'^(\d+\.\d+\.\d+\.\d+).*?" (\d{3})')
# ^(\d+\.\d+\.\d+\.\d+)匹配开头 IP 地址，（匹配值）1
# .*?中间随便是什么字符，非贪婪匹配
# " 匹配一个引号加空格
# (\d{3})匹配 3 位数字（状态码），（匹配值）2

def get_report():
    ip_counter = Counter() # “数数”的超级字典，统计 IP 出现次数
    error_counter = Counter()

    with open(LOG_FILE, 'r') as f:
        for line in f:
            match = LOG_PATTERN.search(line)
            if match:
                ip, status = match.groups() # 例('192.168.1.1', '200')
                ip_counter[ip] += 1
                if status.startswith(('4', '5')):
                    error_counter[status] += 1

    # 格式化报告
    date_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    report = f"Nginx 日报 ({date_str})\n"
    report += "Top IP:\n"
    for ip, count in ip_counter.most_common(10):
        report += f"  {ip}: {count}\n"
    
    report += "\nErrors:\n"
    for code, count in error_counter.most_common(5):
        report += f"  {code}: {count}\n"
        
    return report

def send_email(content):
    # 系统配置msmtp/mailutil
    subject = f"Report {datetime.now().date()}"
    cmd = f'echo "{content}" | mail -s "{subject}" {EMAIL_TO}'
    # 拼装工 echo "Top...." | mail -s "Report 2026-1-8" xx@qq.com
    # subprocess，启动并控制外部的系统命令
    try:
        subprocess.run(cmd, shell=True, check=True)
        print("邮件发送成功")
    except subprocess.CalledProcessError as e:
        print(f"邮件发送失败: {e}")

if __name__ == "__main__":
    report = get_report()
    print(report) 
    send_email(report) 


'''
192.168.6.200 - - [08/Jan/2026:20:23:11 +0800] "GET / HTTP/1.1" 304 0 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
192.168.6.200 - - [08/Jan/2026:20:34:48 +0800] "GET / HTTP/1.1" 304 0 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
192.168.6.148 - - [08/Jan/2026:20:35:01 +0800] "GET / HTTP/1.1" 200 409 "-" "Mozilla/5.0 (Linux; Android 16; RMX6699 Build/AP3A.240617.008; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/116.0.0.0 Mobile Safari/537.36 XWEB/1160117 MMWEBSDK/20250904 MMWEBID/2118 MicroMessenger/8.0.65.2941(0x28004141) WeChat/arm64 Weixin GPVersion/1 NetType/WIFI Language/zh_CN ABI/arm64"
'''