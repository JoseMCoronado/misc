# -*- coding: cp1252 -*-
print """
+-----------------------------------------------------------------+
|                                                                 |
|                Creation of Lead & Customers                     |
|                                                                 |
+-----------------------------------------------------------------+
"""

##Configuration
url = 'https://mydatabase.odoo.com'
db = 'mydatabase'
username = 'myemail@mydatabase.com'
password = 'saHLfWymPBM9FPK'

##Web Form Fields
form_values = {
    'form_first_name' : 'Steve',
    'form_last_name' : 'Example',
    'form_industry' : 'Automotive',
    'form_country' : 'United States',
    'form_company' : 'Example Inc.',
    'form_note' : 'Requesting some information in regards to the m2',
    }

##Importing Libraries
import xmlrpclib

try:
    common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
    common.version()
    uid = common.authenticate(db, username, password, {})
    models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
except:
    print('Database Credentials are incorrect')
    exit()

##Searching Database Values
customer_country = models.execute_kw(db, uid, password, 'res.country', 'search',
                   [[['name', 'ilike', form_values['form_country']]]],{'limit': 1})
customer_industry = models.execute_kw(db, uid, password, 'x_industry', 'search',
                   [[['x_name', 'ilike', form_values['form_industry']]]],{'limit': 1})
##CREATION OF COMPANY##
company_contact = models.execute_kw(db, uid, password, 'res.partner', 'create',
                [{
                'name': form_values['form_company'],
                'is_company': True,
                }])

##CREATION OF MAIN CUSTOMER##
main_customer = models.execute_kw(db, uid, password, 'res.partner', 'create',
                [{
                'name': form_values['form_first_name'] + ' ' + form_values['form_last_name'],
                'parent_id': company_contact,
                }])
comments = form_values['form_note']
if customer_industry:
    models.execute_kw(db, uid, password, 'res.partner', 'write', [[main_customer], {'x_studio_field_T2Cci': customer_industry[0]}])
else:
    comments += ' Industry: ' + form_values['form_industry']

if customer_country:
    models.execute_kw(db, uid, password, 'res.partner', 'write', [[main_customer], {'country_id': customer_country[0]}])
else:
    comments += ' Country: ' + form_values['form_country']

models.execute_kw(db, uid, password, 'res.partner', 'write', [[main_customer], {'comment': comments}])

##CREATION OF OPPORTUNITY
opportunity_created = models.execute_kw(db, uid, password, 'crm.lead', 'create',
                [{
                'name': form_values['form_company'] + ' ' + form_values['form_first_name'] + ' ' + form_values['form_last_name'],
                'partner_id': main_customer,
                'type': 'opportunity',
                'description': comments,
                }])

