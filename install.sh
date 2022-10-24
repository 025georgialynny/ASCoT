sudo apt update
sudo apt upgrade
sudo apt install python3-pip
sudo apt install default-mysql-server default-mysql-client python-dev --fix-broken --fix-missing
sudo service mysql start
sudo bash mysql_install.sh flaskdb ascot asco
echo "alias python='python3'" >> ~/.bashrc
echo "alias pip='pip3'" >> ~/.bashrc
source ~/.bashrc
pip3 install -r requirements.txt

