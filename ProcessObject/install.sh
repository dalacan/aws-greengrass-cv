#!/bin/bash
sudo apt-get install cifs-utils

python3 $1/install.py -s $2
sudo mv /tmp/win-credentials /etc/win-credentials
sudo chown root: /etc/win-credentials
sudo chmod 600 /etc/win-credentials

[ ! -d "$5" ] && mkdir $5

! mountpoint -q "$5" || umount "$5"

sudo mount -t cifs -o credentials=/etc/win-credentials,uid=1000,gid=1000,dir_mode=0777,file_mode=0777 //$3/$4 $5

python3 -m pip install --user awsiotsdk pyzbar boto3