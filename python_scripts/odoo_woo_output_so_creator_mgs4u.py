# -*- coding: cp1252 -*-

##WOO COMMERCE TO ODOO ORDER CREATION SCRIPT v10.0 - VERY SPECIFIC TO A CLIENT'S NEEDS
##WORKS ON A CSV EXPORT OF WOO COMMERCE ORDERS

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

#first open of CSV
from Tkinter import Tk
from tkFileDialog import askopenfilename

Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
var = askopenfilename() # show an "Open" dialog box and return the path to the selected file
print "You Selected ", var
f = open(var)
reader = csv.reader(f)

##Checking existence of customers and creates one when not found
print "****Checking for existing customers****"
next(reader, None)  # skip the headers

##Translation Dictionary [woo_code,uom_id.id]
product_dictionary = {
                    'TESTTESTTEST': [7736,26]
                     }

unique_emails = []
for row in reader:
    if row[12] not in unique_emails:
            unique_emails.append(row[12])
            search_email = models.execute_kw(db, uid, password,
            'res.partner', 'search',
            [[['email', '=', row[12]], ['customer', '=', True]]])
            if len(search_email) > 0:
                   print 'Contact Found: ' + row[13] +" via Email: " + row[12]
                   continue
            else:
                   print row[13] + ' Contact Not Found' 
                   customer_state = models.execute_kw(db, uid, password,
                   'res.country.state', 'search',
                   [[['code', '=', row[18]]]],{'limit': 1})
                   customer_country = models.execute_kw(db, uid, password,
                   'res.country', 'search',
                   [[['code', '=', row[19]]]],{'limit': 1})
                   shipping_state = models.execute_kw(db, uid, password,
                   'res.country.state', 'search',
                   [[['code', '=', row[25]]]],{'limit': 1})
                   shipping_country = models.execute_kw(db, uid, password,
                   'res.country', 'search',
                   [[['code', '=', row[26]]]],{'limit': 1})
                   if not row[7]:
                       ##CREATION OF MAIN CUSTOMER##
                       main_customer = models.execute_kw(db, uid, password, 'res.partner', 'create', [{
                            'name': row[13], 'email': row[12], 'street': row[14],'street2': row[15],
                            'zip': row[16], 'city': row[17], 'state_id': customer_state[0],
                            'country_id': customer_country[0],'phone': row[34],
                        }])
                       print 'Contact Created: ' + row[13] +" with Email: " + row[12]
                       ##CREATION OF SHIPPING ADDRESS##
                       if row[14] != row[21] or row[15] != row[22]:
                           shipping_address = models.execute_kw(db, uid, password, 'res.partner', 'create', [{
                                'name': row[20], 'street': row[21],'street2': row[22],
                                'zip': row[23], 'city': row[24], 'state_id': shipping_state[0],
                                'country_id': shipping_country[0],'parent_id': main_customer, 'type': 'delivery',
                                'phone': row[34],
                            }])
                           print 'Shipping Address Created for ' + row[13]
                   else:
                       ##CREATION OF COMPANY##
                       company_contact = models.execute_kw(db, uid, password, 'res.partner', 'create', [{
                            'name': row[7],
                        }])
                       print 'Company Created: ' + row[7]
                       ##CREATION OF BILLING ADDRESS##
                       main_customer = models.execute_kw(db, uid, password, 'res.partner', 'create', [{
                            'name': row[13], 'email': row[12], 'street': row[14],'street2': row[15],
                            'zip': row[16], 'city': row[17], 'state_id': customer_state[0],
                            'country_id': customer_country[0],'phone': row[34], 'parent_id': company_contact,
                            'type': 'invoice',
                        }])
                       print 'Contact Created: ' + row[13] +" with Email: " + row[12]
                       ##CREATION OF SHIPPING ADDRESS##
                       if row[14] != row[21] or row[15] != row[22]:
                           shipping_address = models.execute_kw(db, uid, password, 'res.partner', 'create', [{
                                'name': row[20], 'street': row[21],'street2': row[22],
                                'zip': row[23], 'city': row[24], 'state_id': shipping_state[0],
                                'country_id': shipping_country[0],'parent_id': company_contact, 'type': 'delivery',
                                'phone': row[34],
                            }])
                           print 'Shipping Address Created for ' + row[7]           
                   continue
        
##Checking existence of customers and creates one when not found
print "****Creating Orders****"
o = open(var)
order_reader = csv.reader(o)
next(order_reader, None)  # skip the headers
unique_orders = []
for row in order_reader:
    if row[0] not in unique_orders:
        unique_orders.append(row[0])
        customer_email = models.execute_kw(db, uid, password,
        'res.partner', 'search',
        [[['email', '=', row[12]], ['customer', '=', True]]],{'limit': 1})
        creation_order = models.execute_kw(db, uid, password, 'sale.order', 'create', [{
                'partner_id': customer_email[0], 'client_order_ref': row[0],
                'note': row[29], 'x_woo_code': row[0],
            }])
        search_carrier = models.execute_kw(db, uid, password,
        'product.product', 'search',
        [[['name', '=', row[27]]]],{'limit': 1})
        models.execute_kw(db, uid, password, 'sale.order.line', 'create', [{
                'product_id': search_carrier[0], 'product_uom_qty': 1,
                'order_id': creation_order, 'price_unit': row[28], 'layout_category_id': 2,
            }])
        print 'Order created'

print "****Creating Order Lines****"
j = open(var)
order_line_reader = csv.reader(j)
next(order_line_reader, None)  # skip the headers
for row in order_line_reader:
    search_order = models.execute_kw(db, uid, password,
    'sale.order', 'search',
    [[['x_woo_code', '=', row[0]]]],{'limit': 1})

    if product_dictionary[row[31]]:
        print 'HEY!'
        print product_dictionary[row[31]][0]
        product_price = float(row[11]) / float(row[9])
        if float(row[32]) == 0:
            line_tax = [(6,0,[1])]
        else:
            line_tax = [(6,0,[5])]
        models.execute_kw(db, uid, password, 'sale.order.line', 'create', [{
                'product_id': product_dictionary[row[31]][0], 'product_uom': product_dictionary[row[31]][1], 'product_uom_qty': row[9],
                'order_id': search_order[0], 'price_unit': product_price, 'tax_id': line_tax,
                'layout_category_id': 1,
            }])
    else:
        search_product = models.execute_kw(db, uid, password,
        'product.product', 'search',
        [[['x_woo_code', '=', row[31]]]],{'limit': 1})
        search_product_2 = models.execute_kw(db, uid, password,
        'product.product', 'search',
        [[['name', '=', row[8]]]],{'limit': 1})
        if len(search_product) > 0:
            chosen_product = search_product
        else:
            chosen_product = search_product_2
        product_price = float(row[11]) / float(row[9])
        if float(row[32]) == 0:
            line_tax = [(6,0,[1])]
        else:
            line_tax = [(6,0,[5])]
        models.execute_kw(db, uid, password, 'sale.order.line', 'create', [{
                    'product_id': chosen_product[0], 'product_uom_qty': row[9],
                    'order_id': search_order[0], 'price_unit': product_price, 'tax_id': line_tax,
                    'layout_category_id': 1,
                }])
    print 'order line created'
       
print '****IMPORT COMPLETED****'
close = raw_input("Press enter to close prompt")
