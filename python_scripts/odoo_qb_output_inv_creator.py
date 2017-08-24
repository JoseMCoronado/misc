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
import time
from datetime import date, datetime
from Tkinter import Tk
from tkFileDialog import askopenfilename

log= open("script_log.txt","w+")

##Defining Time of Import
now = time.strftime("%c")

log.write('*** Start of ' + str(("%s"  % now )) + ' Import ***' + '\n')
##Checking for correct credentials
#try:
##Authentication
common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
common.version()

##uid Routing
uid = common.authenticate(db, username, password, {})

##calling
models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))

##testing

lockdateraw = models.execute_kw(db, uid, password,
            'res.company', 'read',[1], {'fields': ['period_lock_date']})
lockdatedis = datetime.strptime(lockdateraw[0]['period_lock_date'], '%Y-%m-%d')
lockdate = lockdatedis.date()
log.write('Database Lock Date: ' + str(lockdateraw[0]['period_lock_date']) + '\n')
#except:
#    log.write(str(("%s"  % now )) + " ERROR: USER CREDENTIALS NOT VALID. PLEASE CHECK SCRIPT'S USERNAME AND PASSWORD" + '\n')

try:
    Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
    var = askopenfilename() # show an "Open" dialog box and return the path to the selected file
    log.write('File Location: ' + str(("%s"  % var )) + '\n')
    f = open(var)
    #f = open('C:\static_file_location')
    reader = csv.reader(f)
except:
    log.write(str(("%s"  % now )) + " ERROR: FILE LOCATION NOT VALID. MAKE SURE FILE IS AVAILABLE" + '\n')
next(reader, None)  # skip the headers
unique_vendors = []
for row in reader:
    if row[4] not in (None, ""):
        try:
            ##Determining Line Date
            datetime_object = datetime.strptime(row[2], '%m/%d/%Y')
            predt = datetime_object.date()
            dt=str(datetime_object.date())
            date_error = False
        except:
            log.write(str(("%s"  % now )) + " ERROR: SKIP LINE DATE FORMATTING ERROR FOR: " + row[4] + " " + row[8] + '\n')
            date_error = True
        if predt > lockdate:
            try:
                parsed = row[8].split('|')
                job_code = parsed[0].split('-')
                job_code_concat = str(job_code[0]+'-'+job_code[1])
                wbs_code = str(parsed[0])
                search_aa = models.execute_kw(db, uid, password,
                    'account.analytic.account', 'search',
                    [[['name', 'ilike', job_code_concat]]])
                search_ats = models.execute_kw(db, uid, password,
                'account.analytic.tag', 'search',
                [[['name', 'ilike', wbs_code]]])
                test_aa=search_aa[0]
                test_ats=search_ats[0]
                memo_error = False
            except:
                log.write(str(("%s"  % now )) + " ERROR: SKIP LINE - MAYBE MISSING JOB CODE OR INCORRECT MEMO FORMATTING FOR: " + row[4] + " " + row[8] + '\n')
                memo_error = True
            try:
                purchase_order = str(parsed[1])
                search_po = models.execute_kw(db, uid, password,
                    'purchase.order', 'search',
                    [[['name', 'ilike', purchase_order]]])

                test_po = search_po[0]
                no_po = False
            except:
                no_po = True


            if memo_error == False and date_error == False:
                if row[6] not in unique_vendors:
                    unique_vendors.append(row[6])
                    search_vendor = models.execute_kw(db, uid, password,
                        'res.partner', 'search',
                        [[['name', '=', row[6]], ['supplier', '=', True]]])
                    if len(search_vendor) == 0:
                        supplier = models.execute_kw(db, uid, password, 'res.partner', 'create', [{
                                                    'name': row[6], 'supplier': True,
                                                }])
                        log.write(str(("%s"  % now )) + " RECORD CREATED: CONTACT NOT FOUND, NEW CONTACT CREATED " + row[6] + '\n')
                search_invoice = models.execute_kw(db, uid, password,
                            'account.invoice', 'search',
                            [[['x_qb_number', '=', row[4]]]])
                if len(search_invoice) == 0:
                    invoice_vendor = models.execute_kw(db, uid, password,
                        'res.partner', 'search',
                        [[['name', '=', row[6]], ['supplier', '=', True]]])
                    if no_po == True:
                        creation_invoice = models.execute_kw(db, uid, password, 'account.invoice', 'create', [{
                                        'partner_id': invoice_vendor[0], 'comment': row[8], 'type': 'in_invoice',
                                        'journal_id': 2, 'x_qb_number': row[4], 'date_invoice': dt,
                                    }])
                        creation_line = models.execute_kw(db, uid, password, 'account.invoice.line', 'create', [{
                                        'name': row[4], 'account_id': 19,
                                        'price_unit': float(row[10].replace(',', '')), 'quantity': 1,
                                        'invoice_id': creation_invoice, 'account_analytic_id': int(search_aa[0]),
                                        'analytic_tag_ids': [(6, 0,[search_ats[0]])],
                                    }])

                        models.execute_kw(db, uid, password, 'account.invoice', 'action_invoice_open', [[int(creation_invoice)]])
                    if no_po == False:
                        poname = models.execute_kw(db, uid, password,
                            'purchase.order', 'search_read',
                            [[['id', '=', int(test_po)]]],
                            {'fields': ['name','partner_id']})
                        polines = models.execute_kw(db, uid, password,
                            'purchase.order.line', 'search_read',
                            [[['order_id', '=', int(test_po)]]],{'fields': [
                            'id',
                            'name',
                            'product_uom',
                            'product_id',
                            'product_qty',
                            'price_unit',
                            #'account_analytic_id',
                            #'analytic_tag_ids',
                            ]})
                        createdamount = 0
                        creation_invoice = models.execute_kw(db, uid, password, 'account.invoice', 'create', [{
                                        'partner_id': invoice_vendor[0], 'comment': row[8], 'type': 'in_invoice',
                                        'journal_id': 2, 'x_qb_number': row[4], 'date_invoice': dt, 'origin': poname[0]['name'],
                                    }])
                        log.write(str(("%s"  % creation_invoice )) + '\n')
                        for l in polines:
                            createdamount += float(l['price_unit']) * float(l['product_qty'])
                            invline = models.execute_kw(db, uid, password, 'account.invoice.line', 'create', [{
                                            'purchase_line_id': l['id'],
                                            'name': l['name'],
                                            'origin': poname[0]['name'],
                                            'uom_id': l['product_uom'][0],
                                            'product_id': l['product_id'][0],
                                            'account_id': 19,
                                            'price_unit': l['price_unit'],
                                            'quantity': l['product_qty'],
                                            'account_analytic_id': int(search_aa[0]),
                                            'analytic_tag_ids': [(6, 0,[search_ats[0]])],
                                            'invoice_id': creation_invoice,
                                        }])
                        if createdamount != float(row[10].replace(',', '')):
                            creation_line = models.execute_kw(db, uid, password, 'account.invoice.line', 'create', [{
                                            'name': 'difference', 'account_id': 19,
                                            'price_unit': float(row[10].replace(',', '')) - createdamount, 'quantity': 1,
                                            'invoice_id': creation_invoice, 'account_analytic_id': int(search_aa[0]),
                                            'analytic_tag_ids': [(6, 0,[search_ats[0]])],
                                        }])
                        models.execute_kw(db, uid, password, 'account.invoice', 'action_invoice_open', [[int(creation_invoice)]])
log.write('*** End of ' + str(("%s"  % now )) + ' Import ***' + '\n')
log.close()
sys.exit()
