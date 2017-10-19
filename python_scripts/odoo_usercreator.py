# -*- coding: cp1252 -*-
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


##Authentication
common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
common.version()

##uid Routing
uid = common.authenticate(db, username, password, {})

##calling
models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))

#first open of CSV
from Tkinter import Tk
from tkFileDialog import askopenfilename

Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
var = askopenfilename() # show an "Open" dialog box and return the path to the selected file
print "You Selected ", var
f = open(var)
reader = csv.reader(f)

next(reader, None)  # skip the headers
groups_attach = [(6,0,[9])]
for row in reader:
    try:
        user_created = models.execute_kw(db, uid, password, 'res.users','create', [{
                    'name': row[1],
                    'login': row[0],
                    'partner_id': int(row[2]),
                    'groups_id': groups_attach,
                    
                }])
        print(str(row[0]) +","+ str(row[1]) +","+  str(row[2]) +","+ 'SUCCESS')
        time.sleep(1)
        continue
    except:
        print(str(row[0]) +","+ str(row[1]) +","+  str(row[2]) +","+ 'ERROR')
        continue


print '****IMPORT COMPLETED****'
close = raw_input("Press enter to close prompt")
