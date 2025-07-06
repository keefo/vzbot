sudo systemctl stop led_service.service
sudo systemctl disable led_service.service
sudo rm /etc/systemd/system/led_service.service
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
