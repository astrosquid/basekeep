#!/bin/python3

import argparse
import json
import os
import psycopg2
import sys

from pathlib import Path

def analyze_schemas(conn, schema_dirs):
    
    cursor = conn.cursor()
    cursor.execute("""SELECT schema_name FROM information_schema.schemata
        WHERE schema_owner != 'postgres';""")
    existing_schemas = cursor.fetchall()

    schema_additions = []
    schema_removals = []

    for schema in schema_dirs:
        if schema not in existing_schemas:
            schema_additions.append(schema)

    for schema in existing_schemas:
        if schema not in schema_dirs:
            schema_removals.append(schema)

    print("Schemata to be added: " + str(schema_additions))
    print("Schemata to be removed: " + str(schema_removals))

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
    print("Analyzing file tree for " + dbname)
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

try:
    conn = psycopg2.connect("dbname='%s' user='basekeep' host='localhost' password='%s'" % (dbname, dbpassword))
    analyze_schemas(conn, schema_dirs)
except Exception as e:
    print("Unable to connect to %s. Are you sure %s is a basekeep-operable tree?" % (dbname, dbname))
    print(e)
