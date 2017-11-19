# -*- coding: cp1252 -*-
print """
+-----------------------------------------------------------------+
|                                                                 |
|                sale.order Record Creator Script                 |
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
unique_orders = []
for row in reader:
    row_num += 1
    print str(round((float(row_num)/float(total_row))*100,2)) +"%"
    try:
        if row[0] not in unique_orders:
            unique_orders.append(row[0])
            creation_order = models.execute_kw(db, uid, password, 'sale.order', 'create', [{
                'name':str(row[0]),
                'date_order':str(row[1]),
                'x_studio_field_Y4jOD':str(row[2]),
                'partner_id':int(row[3]),
                'x_studio_field_pPNY3':str(row[4]),
                'company_id':int(row[5]),
                'currency_id': 3,
            }])
        sale_order = models.execute_kw(db, uid, password,'sale.order', 'search',
        [[['name', '=', row[0]]]],{'limit': 1})
        models.execute_kw(db, uid, password, 'sale.order.line', 'create', [{
                'product_id':int(row[6]),
                'name':str(row[7]),
                'product_uom_qty':float(row[8]),
                'product_uom':int(row[9]),
                'price_unit':float(row[10]),
                'order_id': sale_order[0],
                'taxes_id': [(6,0,[1])],
            }])
        continue
    except:
        print('error')
        error_list.append('Error @ row %s for id:%s' % (row_num,row[0]))
        continue

for e in error_list:
    print e

print '****IMPORT COMPLETED****'
close = raw_input("Press enter to close prompt")
