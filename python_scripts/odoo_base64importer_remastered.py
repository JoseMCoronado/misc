# -*- coding: cp1252 -*-
# Importing Libraries
import xmlrpc.client as xmlrpclib
import urllib.request
import csv
import base64
import time

print(
    """
+-----------------------------------------------------------------+
|                                                                 |
|                  ODOO BASE64 FILE IMPORTER                      |
|                     By Jose M. Coronado                         |
+-----------------------------------------------------------------+
"""
)
file_type = input("File Type (Local Path='local' or Online='url'): ")
if file_type != "local" and file_type != "url":
    close_type = input("File type %s is not 'url' or 'local'." % (file_type))
    exit()

import_type = input("Import Type (Product Image='product' or Multi-Image='multi'): ")
if import_type != "product" and import_type != "multi":
    close_type = input("Import type %s is not 'product' or 'multi'." % (import_type))
    exit()

# Configuration
url = input("Database URL (e.g. https://mydatabase.odoo.com): ")
db = input("Database Name (e.g. mydatabase): ")
username = input("Login (e.g. admin@mydatabase.com): ")
password = input("Password (e.g. admin): ")
var = input("Import File (e.g. /Users/gfp/Desktop/test_url.csv): ")


try:
    # Authentication
    common = xmlrpclib.ServerProxy("{}/xmlrpc/2/common".format(url))
    common.version()

    # uid Routing
    uid = common.authenticate(db, username, password, {})

    # calling
    models = xmlrpclib.ServerProxy("{}/xmlrpc/2/object".format(url))
except Exception:
    close_type = input("Credentials for login %s are incorrect." % (username))
    exit()


count = open(var)
reader_count = csv.reader(count)
total_row = sum(1 for row in reader_count)
print("Total Rows in file:" + str(total_row))

f = open(var)
reader = csv.reader(f)
next(reader, None)  # skip the headers

row_num = 0
error_list = []

for row in reader:
    row_num += 1
    print(str(round((float(row_num) / float(total_row)) * 100, 2)) + "%")
    try:
        if file_type == "url":
            g = urllib.request.urlopen(row[1])
            data = g.read()
        if file_type == "local":
            with open(row[1], "rb") as inf:
                data = inf.read()
        image = base64.b64encode(data).decode()

        if import_type == "product":
            prod_dict = models.execute_kw(
                db,
                uid,
                password,
                "product.product",
                "read",
                [int(row[0])],
                {"fields": ["product_tmpl_id"]},
            )
            models.execute_kw(
                db,
                uid,
                password,
                "product.product",
                "write",
                [[int(row[0])], {"image_variant_1920": image}],
            )
            models.execute_kw(
                db,
                uid,
                password,
                "product.template",
                "write",
                [[prod_dict[0]["product_tmpl_id"][0]], {"image_1920": image}],
            )
        if import_type == "multi":
            models.execute_kw(
                db,
                uid,
                password,
                "product.image",
                "create",
                [{"image": image, "name": row[1], "product_tmpl_id": row[0]}],
            )
        if file_type == "url":
            time.sleep(1)
        continue
    except Exception:
        print("error")
        error_list.append("Error @ row %s for id %s" % (row_num, row[0]))
        continue

for e in error_list:
    print(e)

print("****IMPORT COMPLETED****")
close = input("Press enter to close prompt")
