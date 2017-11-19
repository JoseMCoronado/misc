# -*- coding: cp1252 -*-
##Configuration
url = raw_input("Database URL (e.g. https://mydatabase.odoo.com): ")
db = raw_input("Database Name (e.g. mydatabase): ")
username = raw_input("Login (e.g. admin@mydatabase.com): ")
password = raw_input("Password (e.g. admin): ")
model = raw_input("Model (e.g. product.template): ")

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
for row in reader:
    try:
        with open(row[1], 'rb') as inf:
            filedata = inf.read()
        encoded = base64.b64encode(filedata)

        file_completed = models.execute_kw(db, uid, password, 'ir.attachment', 'create', [{
            'name': str(row[2]),
            'type': 'binary',
            'datas': encoded,
            'res_model': model,
            'res_id': row[0],
            'datas_fname': row[3],
        }])
        print(row[0])
        continue
    except:
        print('error' + str(row[0]))
        continue
        
print '****IMPORT COMPLETED****'
close = raw_input("Press enter to close prompt")
