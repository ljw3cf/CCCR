#!/bin/bash

# 기존 wp 띄우기 위해 web서버엔 wp, apache, php가 필요했으나, wordpress 이미지에 해당 서비스 및 프로그램이 다 깔려있음
# 따라서 wp를 띄우기 위해 필요한 이미지는 wordpress 및 database

# 1) 서비스간 사용할 bridge 네트워크 생성
docker network create net1

# 2) Database 컨테이너 생성
docker run -d --name db \
-v wp-db-vol:/var/lib/mysql \
--network net1 \
-e MYSQL_ROOT_PASSWORD=dkagh1. \
-e MYSQL_USER=wp-admin \
-e MYSQL_PASSWORD=dkagh1. \
-e MYSQL_DATABASE=wordpress_db \
mariadb

# 4) 인스턴스 생성 후 지연시간 설정 (wordpress 컨테이너 너무 빨리 생성되면 db랑 안붙더라...)
sleep 1

# 5) Wordpress 컨테이너 생성
docker run -d --name wordpress \
-v wp-web-vol:/var/www/html \
--network net1 \
--link db \                          # db 컨테이너에 링크하여, 해당 ip를 컨테이너명으로 가져올 수 있도록 설정 
-e WORDPRESS_DB_HOST=db \            # HOST에 컨테이너명을 지정하여 호스트 ip를 가져온다.
-e WORDPRESS_DB_USER=wp-admin \
-e WORDPRESS_DB_PASSWORD=dkagh1. \
-e WORDPRESS_DB_NAME=wordpress_db \
-p 80:80 wordpress                   # 외부에서 80번 포트로 접속시, 인스턴스 80번 포트로 통신할 수 있도록 설정
