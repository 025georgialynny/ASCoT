#!/bin/bash

### from https://clubmate.fi/shell-script-to-create-mysql-database

green() {
  echo -e '\e[32m'$1'\e[m';
}

readonly EXPECTED_ARGS=3
readonly E_BADARGS=65
readonly MYSQL=`which mysql`

# Construct the MySQL query
readonly Q1="CREATE DATABASE IF NOT EXISTS $1;"
readonly Q2="GRANT ALL ON *.* TO '$2'@'localhost' IDENTIFIED BY '$3';"
readonly Q3="FLUSH PRIVILEGES;"
readonly SQL="${Q1}${Q2}${Q3}"


#readonly creattab="USE flaskdb; CREATE TABLE \`User\` ( \`id\` INT NOT NULL AUTO_INCREMENT,\`username\` VARCHAR(15) NOT NULL,\`email\` VARCHAR(50) NOT NULL,\`password\` VARCHAR(80) NOT NULL,PRIMARY KEY (`id`);"
#readonly createadmin="INSERT INTO `members` (`full_names`,`gender`,`physical_address`,`contact_number`)  VALUES ('Sheldon Cooper','Male','Woodcrest', '0976736763');"

# Do some parameter checking and bail if bad
if [ $# -ne $EXPECTED_ARGS ]
then
  echo "Usage: $0 dbname dbuser dbpass"
  exit $E_BADARGS
fi

# Run the actual command
sudo $MYSQL -e "$SQL"
sudo $MYSQL -e "$creattab"

# Let the user know the database was created
green "Database $1 and user $2 created with a password you chose"