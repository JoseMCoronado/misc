# -*- coding: utf-8 -*-
##Configuration
url = raw_input("Database URL (e.g. https://mydatabase.odoo.com): ")
db = raw_input("Database Name (e.g. mydatabase): ")
username = raw_input("Login (e.g. admin@mydatabase.com): ")
password = raw_input("Password (e.g. admin): ")
model = raw_input("Model (e.g. product.product): ")
fields = raw_input("Fields (e.g. id,name,deafult_code,attribute_value_ids,sales_count): ")
listed_fields = [x.strip() for x in fields.split(',')]

##Importing Libraries
import xmlrpclib
import csv 
import sys
import base64
import urllib
import time
from datetime import date, datetime
now = time.strftime("%c")

try:
    ##Authentication
    common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
    common.version()

    ##uid Routing
    uid = common.authenticate(db, username, password, {})

    ##calling
    models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
except:
    print 'ERROR: Please check database credentials'
    
file_name = db + ' ' + model + ' 3extract '+ '.csv'

try:
    print '****Searching for IDs****'
    ids = models.execute_kw(db, uid, password,
        model, 'search',
        [[['id', '!=', False]]])
except:
    print 'ERROR: Error reading models, please make sure user has access rights to model or model is written correctly'
try:
    print '****Writing IDs****'
    record_values = models.execute_kw(db, uid, password,
            model, 'read',
            [ids], {'fields': listed_fields})
except:
    print 'ERROR: Error reading fields, please make sure your fields are correctly written'

try:
    fieldnames = sorted(list(set(k for d in record_values for k in d)))

    with open(file_name, 'w+') as out_file:
                writer = csv.DictWriter(out_file, fieldnames=fieldnames, dialect='excel')
                writer.writeheader()
                writer.writerows(record_values)
except:
    print 'ERROR: Something went wrong in the csv writing process, please find Jose'
    
print '****IMPORT COMPLETED****'
close = raw_input("Press enter to close prompt")
