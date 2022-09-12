#!/bin/bash
sudo apt-get install cifs-utils

python3 $1/install.py -s $2
sudo mv /tmp/win-credentials /etc/win-credentials
sudo chown root: /etc/win-credentials
sudo chmod 600 /etc/win-credentials

if ! grep -q 'objectdetector-fileshare' /etc/fstab ; then
    echo "Creating fstab entry."
    echo "# objectdetector-fileshare" >> /etc/fstab
    echo "//$3/$4  $5  cifs  credentials=/etc/win-credentials,uid=1000,gid=1000,dir_mode=0777,file_mode=0777 0       0" >> /etc/fstab
    sudo mount $5
else
    echo "Entry in fstab exists."
fi

pip3 install awsiotsdk pyzbar boto3