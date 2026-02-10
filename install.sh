#!/bin/bash
systemctl disable management.service
rm /etc/systemd/system/management.service
mv ./management.service /etc/systemd/system
systemctl start management.service
systemctl enable management.service
