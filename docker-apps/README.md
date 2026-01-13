# Docker多容器应用运维文档

## 基础配置

### Nginx配置
```mkdir -p nginx/conf.d```

### Redis操作
#### 查看Redis键
```docker exec -it houjiasheng-redis-1 redis-cli keys '*' ```

## 性能测试

### 压测准备
```sudo apt install apache2-utils```

### 压测命令
```
ab -n 1000 -c 100 -k http://192.168.6.57/2026/01/10/hello-world/
```

### 压测结果对比

#### 未开缓存性能
>Concurrency Level:      100
Time taken for tests:   50.137 seconds
Complete requests:      1000
Failed requests:        0
Keep-Alive requests:    0
Total transferred:      92180000 bytes
HTML transferred:       91730000 bytes
Requests per second:    19.95 [#/sec] (mean)
Time per request:       5013.669 [ms] (mean)
Time per request:       50.137 [ms] (mean, across all concurrent requests)
Transfer rate:          1795.48 [Kbytes/sec] received

#### 开启缓存性能
>Concurrency Level:      100
Time taken for tests:   48.965 seconds
Complete requests:      1000
Failed requests:        0
Keep-Alive requests:    0
Total transferred:      92343000 bytes
HTML transferred:       91893000 bytes
Requests per second:    20.42 [#/sec] (mean)
Time per request:       4896.538 [ms] (mean)
Time per request:       48.965 [ms] (mean, across all concurrent requests)
Transfer rate:          1841.68 [Kbytes/sec] received

## Docker资源优化

### 优化前资源占用
```docker stats```
CONTAINER ID   NAME                      CPU %     MEM USAGE / LIMIT     MEM %     NET I/O          BLOCK I/O         PIDS
9d75d61c155f   houjiasheng-nginx-1       0.00%     9.863MiB / 7.406GiB   0.13%     312MB / 312MB    0B / 4.1kB        9
5ba562e6b499   houjiasheng-wordpress-1   0.01%     131.4MiB / 7.406GiB   1.73%     476MB / 392MB    65.5kB / 97.7MB   11
22ff92dfea63   houjiasheng-redis-1       0.57%     6.082MiB / 7.406GiB   0.08%     69.3MB / 355MB   2.75MB / 7.63MB   6
b55d8a610e35   houjiasheng-db-1          1.37%     496.1MiB / 7.406GiB   6.54%     15.8MB / 113MB   270kB / 682MB     46

### 优化后资源占用
CONTAINER ID   NAME                      CPU %     MEM USAGE / LIMIT     MEM %     NET I/O          BLOCK I/O        PIDS
e179600ecf03   houjiasheng-nginx-1       0.00%     7.93MiB / 7.406GiB    0.10%     95.5kB / 90kB    0B / 4.1kB       9
8426c5bfaeba   houjiasheng-wordpress-1   0.01%     78.93MiB / 7.406GiB   1.04%     2.13MB / 360kB   0B / 6.35MB      8
b8eebab25cc1   houjiasheng-redis-1       0.51%     4.836MiB / 7.406GiB   0.06%     6.1kB / 126B     0B / 0B          6
49b15fcd9d97   houjiasheng-db-1          0.02%     96.42MiB / 7.406GiB   1.27%     190kB / 722kB    14.7MB / 741kB   8

#### 优化结果
> 数据库 (DB)：内存使用从 496.1MiB 骤降至 96.42MiB，降幅高达 80.5%。这是本次优化中收益最明显的部分

## 数据备份与恢复

### 卷备份
```sql
docker run --rm \
  --mount type=volume,source=houjiasheng_db_data,target=/data,readonly \
  --mount type=bind,source="$(pwd)",target=/backup \
  busybox \
  sh -c "cd /data && tar -czf /backup/db_backup_$(date +%Y%m%d_%H%M%S).tar.gz ."
```

### 查看卷数据
```sql
docker run --rm \
  --mount type=volume,source=houjiasheng_db_data,target=/data,readonly \
  busybox \
  ls -la /data
```

### 清除卷数据
```
docker run --rm \
  --mount type=volume,source=houjiasheng_db_data,target=/data \
  busybox \
  sh -c "rm -rf /data/* /data/.[!.]* /data/..?*"
```

### 卷恢复
```sql
docker run --rm \
  --mount type=bind,source="$(pwd)",target=/backup,readonly \
  --mount type=volume,source=houjiasheng_db_data,target=/data \
  busybox \
  sh -c "cd /data && tar -xzf /backup/db_backup_"
```

## MySQL操作

### MySQL备份与恢复
#### 备份
```sql
docker exec -i houjiasheng-db-1 mysqldump -u root -prootpass123 --all-databases > backup.sql
```

#### 恢复
```sql
docker exec -i houjiasheng-db-1 mysql -u root -prootpass123 < backup.sql
```

## 数据库迁移：MySQL → MariaDB

### 备份MySQL数据
```sql
docker exec -i houjiasheng-db-1 mysqldump -u root -p'rootpass123' \
  --single-transaction --routines --triggers --events --quick \
  --no-tablespaces --skip-lock-tables \
  wordpress > wordpress_bak.sql
```

### 恢复到MariaDB（管道方式）
```cat wordpress_bak.sql | docker exec -i houjiasheng-db-1 mariadb -u root -p'rootpass123' wordpress```

**创建数据库并导入**
```sql
(echo "CREATE DATABASE IF NOT EXISTS wordpress CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" && cat wordpress_bak.sql) | \
  docker exec -i houjiasheng-db-1 mariadb -u root -p'rootpass123'
```

### 验证导入结果
```docker exec -it houjiasheng-db-1 mariadb -u root -p'rootpass123' -e "SHOW DATABASES;"```
