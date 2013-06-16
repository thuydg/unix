#!/usr/bin/env python

from datetime import date
import time
import datetime

test_dir_name = '20130618'

print test_dir_name
check_year = test_dir_name[0:4]
print "Y" + check_year
check_month = test_dir_name[4:6]
print "M" + check_month
check_day = test_dir_name[6:8]
print "D" + check_day

today = date.today()
check_date = datetime.date( int(check_year) , int(check_month) , int(check_day) )
print today
print "check is"
print check_date 
if today > check_date :
	print "today is bigger"
else:
    print "today is smaller"
#check_date = datetime.date(check_year, check_month, check_day)
#print check_date

