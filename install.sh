#!/bin/bash
systemctl disable management.service
docker compose down
if ! -e /etc/systemd/system/management.service; then
    rm /etc/systemd/system/management.service
fi
mv ./management.service /etc/systemd/system
systemctl start management.service
systemctl enable management.service
