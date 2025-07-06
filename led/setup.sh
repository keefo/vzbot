python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

./remove.sh || true

sudo cp led_service.service /etc/systemd/system/led_service.service
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable led_service.service
sudo systemctl start led_service.service
sudo systemctl status led_service.service
