sudo systemctl stop killswitch_service.service
sudo systemctl disable killswitch_service.service
sudo rm /etc/systemd/system/killswitch_service.service
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
