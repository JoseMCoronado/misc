# -*- coding: cp1252 -*-
print """
+-----------------------------------------------------------------+
|                                                                 |
|                Res.partner Record Creator Script                |
|                                                                 |
+-----------------------------------------------------------------+
"""

##Configuration
url = raw_input("Database URL (e.g. https://mydatabase.odoo.com): ") 
db = raw_input("Database Name (e.g. mydatabase): ") 
username = raw_input("Login (e.g. admin@mydatabase.com): ") 
password = raw_input("Password (e.g. admin): ") 


##Importing Libraries
import xmlrpclib
import csv
import sys
import base64
import urllib
import time
import io

try:
    ##Authentication
    common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
    common.version()

    ##uid Routing
    uid = common.authenticate(db, username, password, {})

    ##calling
    models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
except:
    close_type = raw_input("Credentials for login %s are incorrect." % (username))
    exit()

#first open of CSV
from Tkinter import Tk
from tkFileDialog import askopenfilename

Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
var = askopenfilename() # show an "Open" dialog box and return the path to the selected file
print "You Selected ", var

count = open(var)
reader_count = csv.reader(count)
total_row = sum(1 for row in reader_count)
print "Total Rows in file:" + str(total_row)

f = open(var)
reader = csv.reader(f)
next(reader, None)  # skip the headers

row_num = 0
error_list = []
unique_ids = []
for row in reader:
    row_num += 1
    print str(round((float(row_num)/float(total_row))*100,2)) +"%"
    try:
        if str(row[0]) in unique_ids:
            continue
        else:
            if int(row[6]) == 0:
                line_tag = [(6,0,[])]
            else:
                line_tag = [(6,0,[int(row[6])])]
            if row[13] == '':
                state = False
            else:
                state = int(row[13])
            models.execute_kw(db, uid, password, 'crm.lead', 'create',
                    [{
                    'type':'lead',
                    'x_studio_field_7pF1f':str(row[0]),
                    'name':str(row[1]),
                    'contact_name':str(row[2]),
                    'x_studio_field_nkbZk':str(row[3]),
                    'company_id':int(row[4]),
                    'referred':str(row[5]),
                    'tag_ids':line_tag,
                    'phone':str(row[7]),
                    'email_from':str(row[8]),
                    'street':str(row[9]),
                    'street2':str(row[10]),
                    'x_studio_field_vGkHe':str(row[11]),
                    'city':str(row[12]),
                    'state_id':state,
                    'vat':str(row[14]),
                    'website':str(row[15]),
                    'function':str(row[16]),
                    'x_studio_field_PAgSK':str(row[17]),
                    'mobile':str(row[18]),
                    'fax':str(row[19]),
                    'description':str(row[20]),

                    }])
        unique_ids.append(str(row[0]))
        continue
    except:
        print('error')
        error_list.append('Error @ row %s for id:%s' % (row_num,row[0]))
        continue

for e in error_list:
    print e

print '****IMPORT COMPLETED****'
close = raw_input("Press enter to close prompt")
