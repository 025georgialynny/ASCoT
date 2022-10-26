sudo apt update -y
sudo apt upgrade -y
sudo apt install  python3-mysql libgirepository1.0-dev openssl python3-pip  python3-dev build-essential -y
sudo apt install libcairo2 libcairo2-dev python3-cairo-dev python3-cairo default-mysql-server default-mysql-client --fix-broken --fix-missing -y
sudo apt install gcc musl-dev python3-dev libffi-dev libcurl4-openssl-dev cargo -y
sudo apt-get install libssl-dev
sudo /etc/init.d/mariadb  start
sudo bash mysql_install.sh flaskdb ascot asco
pip3 install -r requirements.txt 

