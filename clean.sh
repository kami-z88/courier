#!/bin/bash
args=("$@")

function goto
{
label=$1
cmd=$(sed -n "/$label:/{:a;n;p;ba};" $0 | grep -v ':$')
eval "$cmd"
exit
}

del db.sqlite3
rmdir courier\migrations /Q /S
rmdir account\migrations /Q /S
python manage.py makemigrations account
python manage.py makemigrations courier
python manage.py makemigrations settings
python manage.py migrate
python manage.py create-admin