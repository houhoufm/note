# MySQL 自动备份到阿里云 OSS

import os
import subprocess
import tempfile
import argparse
import datetime
import gzip
import alibabacloud_oss_v2 as oss

# oss、sql配置
region = 'cn-shenzhen'
bucket = 'pic520'
endpoint = 'oss-cn-shenzhen.aliyuncs.com'

DB_USER = "admin"
DB_PASS = "123456"
DB_NAME = "testdb"  #"all-databases"，则备份全部

# ==================== 1. 执行 MySQL 备份 ====================
def backup_mysql():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if DB_NAME == "all-databases":
        filename = f"mysql_full_backup_{timestamp}.sql.gz"
        cmd = ["mysqldump", "-u", DB_USER, f"--password={DB_PASS}", "--all-databases"]
    else:
        filename = f"mysql_{DB_NAME}_{timestamp}.sql.gz"
        cmd = ["mysqldump", "-u", DB_USER, f"--password={DB_PASS}", DB_NAME]

    # 临时文件创建
    with tempfile.NamedTemporaryFile(mode='w+b', delete=False, suffix='.sql.gz') as tmp_file:
        try:
            # 执行mysqldump并捕获输出
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            
            # 压缩并写入临时文件
            with gzip.open(tmp_file, 'wb') as gz_file:
                gz_file.write(result.stdout)
            
            print(f"MySQL backup successful: {filename}")
            return tmp_file.name, filename

        except subprocess.CalledProcessError as e:
            # 删除可能已创建的临时文件
            if os.path.exists(tmp_file.name):
                os.unlink(tmp_file.name)
            raise RuntimeError(f"mysqldump failed: {e.stderr.decode()}")

# ==================== 2. 上传到 OSS 官方文档====================
def upload_to_oss(file_path, oss_key):

    # 从环境变量中加载凭证信息
    credentials_provider = oss.credentials.EnvironmentVariableCredentialsProvider()

    # 加载SDK的默认配置，并设置凭证提供者
    cfg = oss.config.load_default()
    cfg.credentials_provider = credentials_provider

    # 设置配置中的区域信息
    cfg.region = region

    # 如果提供了endpoint参数，则设置配置中的endpoint
    if endpoint is not None:
        cfg.endpoint = endpoint

    # 使用配置好的信息创建OSS客户端
    client = oss.Client(cfg)

    # 执行上传对象的请求，直接从文件上传
    result = client.put_object_from_file(
        oss.PutObjectRequest(
            bucket=bucket,  # 存储空间名称
            key=oss_key     # 对象名称
        ),
        file_path         # 本地文件路径
    )

    # 输出请求的结果信息
    print(f'status code: {result.status_code},'
          f' request id: {result.request_id},'
          f' content md5: {result.content_md5},'
          f' etag: {result.etag},'
          f' hash crc64: {result.hash_crc64},'
          f' version id: {result.version_id},'
          f' server time: {result.headers.get("x-oss-server-time")},'
    )

# ========================================
def main():
    local_file = None
    try:
        local_file, oss_key = backup_mysql()
        upload_to_oss(local_file, oss_key)
    finally:
        # 清理临时文件 避免在备份失败时尝试删除不存在的local_file文件
        if local_file is not None and os.path.exists(local_file):
            os.unlink(local_file)

if __name__ == "__main__":
    main()
