#!/bin/bash
mv ./management.service /etc/systemd/system
systemctl start management.service
systemctl enable management.service
