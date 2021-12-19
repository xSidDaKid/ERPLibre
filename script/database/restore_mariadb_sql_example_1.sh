#!/usr/bin/env bash

SQL_PATH=./script/database/mariadb_sql_example_1.sql

echo "Create database and user"
sudo mysql -u root << EOF
DROP DATABASE IF EXISTS mariadb_sql_example_1;
CREATE USER IF NOT EXISTS 'organization'@'localhost' IDENTIFIED BY 'organization';
GRANT ALL PRIVILEGES ON *.* TO 'organization'@'localhost' IDENTIFIED BY 'organization';
FLUSH PRIVILEGES;
CREATE DATABASE mariadb_sql_example_1;
EOF

echo "Fix SQL file"
sed -i "s/'0000-00-00'/NULL/g" ${SQL_PATH}

echo "Import SQL file"
mysql -u organization -porganization mariadb_sql_example_1 < ${SQL_PATH}

echo "Fix SQL in database"
./.venv/bin/python ./script/database/fix_mariadb_sql_example_1.py
