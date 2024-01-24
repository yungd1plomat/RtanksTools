#!/bin/bash
sudo NEEDRESTART_MODE=a apt update
sudo NEEDRESTART_MODE=a apt install python3-pip -y
pip install -r requirements.txt
crontab -r
crontab -l > mycron
echo "0 3 * * * /usr/bin/python3 /home/ubuntu/RtanksTools/nuker.py '/home/ubuntu/RtanksTools/data/errors.txt' >> /home/ubuntu/RtanksTools/cron.log 2>&1" >> mycron
crontab mycron
rm mycron
sudo nano data/accounts.txt