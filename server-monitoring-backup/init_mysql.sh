#!/bin/bash

# ==========================================
# MySQL 初始化脚本 (适用于已安装 MySQL 的环境)
# 功能：修改 Root 密码、创建数据库、创建专用用户并授权
# ==========================================

# --- 配置区 (请根据需要修改) ---
DB_ROOT_PASS='rootpass'        # 设置 Root 密码
DB_NAME='testdb'             # 目标数据库名
DB_ADMIN_USER='admin'        # 新建的管理员用户名
DB_ADMIN_PASS='123456'   # 新建的管理员密码
# -------------------------------

echo ">>> [1/3] 启动 MySQL 服务..."
sudo systemctl start mysql
sudo systemctl enable mysql

echo ">>> [2/3] 正在修改 Root 密码为 ${DB_ROOT_PASS}..."
# 使用 sudo mysql 登录（默认 auth_socket 插件允许无密码登录）
# 修改 Root 密码并使用 mysql_native_password 插件以确保兼容性
sudo mysql -u root -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '${DB_ROOT_PASS}';"

echo ">>> [3/3] 正在创建数据库 ${DB_NAME} 和用户 ${DB_ADMIN_USER}..."
# 使用新设置的 Root 密码登录并执行 SQL
sudo mysql -u root -p${DB_ROOT_PASS} <<EOF
-- 1. 创建数据库 (如果不存在)
CREATE DATABASE IF NOT EXISTS ${DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 2. 创建用户 (如果不存在)
CREATE USER IF NOT EXISTS '${DB_ADMIN_USER}'@'localhost' IDENTIFIED BY '${DB_ADMIN_PASS}';

-- 3. 授权 (授予 testdb 的所有权限)
GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${DB_ADMIN_USER}'@'localhost';

-- 4. 刷新权限 (立即生效)
FLUSH PRIVILEGES;

-- 5. 显示结果
SELECT "Database created successfully." AS "Status";
SHOW DATABASES LIKE '${DB_NAME}';
SELECT "User created and granted successfully." AS "Status";
EOF

echo "--------------------------------------------------"
echo ">>> 初始化完成!"
echo ">>> 数据库名: ${DB_NAME}"
echo ">>> Root 密码: ${DB_ROOT_PASS}"
echo ">>> 新用户名: ${DB_ADMIN_USER}"
echo ">>> 新用户密码: ${DB_ADMIN_PASS}"
echo "--------------------------------------------------"
