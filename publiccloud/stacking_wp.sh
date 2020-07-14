#!/bin/bash

# 기존 wp 띄우기 위해 web서버엔 wp, apache, php가 필요했으나, wordpress 이미지에 해당 서비스 및 프로그램이 다 깔려있음
# 따라서 wp를 띄우기 위해 필요한 이미지는 wordpress 및 database

# 1) 서비스간 사용할 bridge 네트워크 생성
docker network create net1

# 2) Database 컨테이너 생성
docker run -d --name db \
-v wp-db-vol:/var/lib/myql \
-e MYSQL_ROOT_PASSWORD=dkagh1. \
-e MYSQL_USER=wp-admin \
-e MYSQL_PASSWORD=dkagh1. \
-e MYSQL_DATABASE=wordpress_db \
--network net1 mariadb

# 3) Wordpress 컨테이너 생성
docker run -d --name wordpress \
-v wp-web-vol:/var/www/html \
--network net1 \
--link db \
-e WORDPRESS_DB_HOST=db \
-e WORDPRESS_DB_USER=wp-admin \
-e WORDPRESS_DB_PASSWORD=dkagh1. \
-e WORDPRESS_DB_NAME=wordpress_db -p 8080:80 wordpress
