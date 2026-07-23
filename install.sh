#!/bin/bash
#This script should be used to install the software as it ensures that an up to date management service
#is created and the app will be fault tolerant on server poweroff
systemctl disable management.service
docker compose down
if ! -e /etc/systemd/system/management.service; then
    rm /etc/systemd/system/management.service
fi
mv ./management.service /etc/systemd/system
systemctl start management.service
systemctl enable management.service
