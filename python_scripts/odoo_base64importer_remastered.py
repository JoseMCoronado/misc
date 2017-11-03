# -*- coding: cp1252 -*-
print """
+-----------------------------------------------------------------+
|                                                                 |
|                  ODOO BASE64 FILE IMPORTER                      |
|                     By Jose M. Coronado                         |
+-----------------------------------------------------------------+
"""
file_type = raw_input("File Type (Local Path='local' or Online='url'): ")
if file_type != 'local' and file_type != 'url':
    close_type = raw_input("File type %s is not 'url' or 'local'." % (file_type))
    exit()

import_type = raw_input("Import Type (Product Image='product' or Multi-Image='multi'): ")
if import_type != 'product' and import_type != 'multi':
    close_type = raw_input("Import type %s is not 'product' or 'multi'." % (import_type))
    exit()

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

for row in reader:
    row_num += 1
    print str(round((float(row_num)/float(total_row))*100,2)) +"%"
    try:
        if file_type == 'url':
            g = urllib.urlopen(row[2])
            data = g.read()
        if file_type == 'local':
            with open(row[2], 'rb') as inf:
                data = inf.read()
        encoded = base64.b64encode(data)
        if import_type == 'product':
            models.execute_kw(db, uid, password, 'product.product', 'write', [int(row[0]), {
            'image': encoded
            }])
        if import_type == 'multi':
            models.execute_kw(db, uid, password, 'product.image', 'create', [{
            'image': encoded,
            'name': row[1],
            'product_tmpl_id': row[0],
            }])
        if file_type == 'url':
            time.sleep(1)
        continue
    except:
        print('error')
        error_list.append('Error @ row %s for id %s' % (row_num,row[0]))
        continue

for e in error_list:
    print e

print '****IMPORT COMPLETED****'
close = raw_input("Press enter to close prompt")
