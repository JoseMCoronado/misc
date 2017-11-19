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

##Authentication
common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
common.version()

##uid Routing
uid = common.authenticate(db, username, password, {})

##calling
models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))

for p in xrange(10000):
    try:
        models.execute_kw(db, uid, password, 'product.template', 'create', [{
            'name': 'product' + str(p),
            'default_code': 'sku' + str(p),
        }])        

        print str(p) + '/created'
    except:
        print  str(p) + '/error'

print '****IMPORT COMPLETED****'
close = raw_input("Press enter to close prompt")
