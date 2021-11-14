#!/bin/bash 

echo "DB_CONNECTION=${dbConnection}" >> /etc/profile
echo "DB_USERNAME=${dbUsername}" >> /etc/profile
echo "DB_PASSWORD=${dbPassword}" >> /etc/profile
echo "export DB_CONNECTION DB_USERNAME DB_PASSWORD" >> /etc/profile


