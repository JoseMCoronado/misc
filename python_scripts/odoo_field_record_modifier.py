# -*- coding: cp1252 -*-
##Configuration
url = raw_input("Database URL (e.g. https://mydatabase.odoo.com): ")
db = raw_input("Database Name (e.g. mydatabase): ")
username = raw_input("Login (e.g. admin@mydatabase.com): ")
password = raw_input("Password (e.g. admin): ")
#model = raw_input("Model (e.g. res.partner): ")

##Importing Libraries
import xmlrpclib
import csv
import sys

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
        models.execute_kw(db, uid, password, 'res.partner', 'write', [[int(row[0])], {
        'email': row[1],
    }])
        print row[0] + '/updated'
    except:
        print  row[0] + '/error'

print '****IMPORT COMPLETED****'
close = raw_input("Press enter to close prompt")
