FROM wordpress:latest

# 安装Redis扩展
RUN pecl install redis && docker-php-ext-enable redis

# 复制Redis插件
COPY redis-cache /usr/src/wordpress/wp-content/plugins/redis-cache
RUN chown -R www-data:www-data /usr/src/wordpress/wp-content/plugins/redis-cache