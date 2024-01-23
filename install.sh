#!/bin/bash
sudo apt update
sudo apt install python3-pip -y
pip install PySocks
cd data
sudo nano accounts.txt
crontab -l > mycron
echo "0 3 * * * /usr/bin/python3 /home/ubuntu/RtanksTools/nuker.py '/home/ubuntu/RtanksTools/data/errors.txt' >> /home/ubuntu/RtanksTools/cron.log 2>&1" >> mycron
crontab mycron
rm mycron