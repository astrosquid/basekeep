#!/bin/python3

import argparse
import json
import os
import psycopg2
import sys

from pathlib import Path

parser = argparse.ArgumentParser(description='Maintain your database structure using directories and files.')
parser.add_argument("-l", "--location", dest="dblocation", required=True, type=str, help="The top directory of your database. Required.")
args = parser.parse_args()

dblocation = args.dblocation
path = Path(dblocation)

if os.path.isdir(str(path)) == False:
    print("Specified directory does not exist or is not directory.")
    sys.exit(0)

dbname = str(Path(dblocation)).split('/')[-1]

confirm = input("Run updates on database \"%s\"? Some data may be lost.\n" % (dbname) ) 

if (confirm == "Yes") or (confirm == "yes") or (confirm == "y"):
    print("Updating " + dbname)
else:
    print("Aborting.")
    sys.exit(0)

basekeep_db_files = next(os.walk(dblocation))[2]

if ("%s.json" % (dbname)) not in basekeep_db_files:
    print("Aborting, please make sure there's a %s.json file in your db directory. See README." % (dbname))
elif ".secrets.json" not in basekeep_db_files:
    print("Aborting, no secrets file found for specified database. Add .secrets.json to db dir. See README.")

secretspath = ""
if (str(path).endswith('/')):
    secretspath = str(path) + '.secrets.json'
else:
    secretspath = str(path) + '/.secrets.json'

with open(secretspath) as secrets_file:
    secrets = json.load(secrets_file)
dbpassword = secrets["dbpass"]

schema_dirs = next(os.walk(dblocation))[1]
print(schema_dirs)

try:
    conn = psycopg2.connect("dbname='%s' user='basekeep' host='localhost' password='%s'" % (dbname, dbpassword))
except:
    print("Unable to make database connection to %s. Are you sure %s is a basekeep-operable tree?" % (dbname, dbname))