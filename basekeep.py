#!/usr/local/bin/python3

import argparse
import json
import operator
import os
from pathlib import Path
import psycopg2
import sys

schema_additions = []
schema_removals = []

#def execute_changes()

def analyze_schemas(conn, schema_dirs):
    existing_schemas = get_existing_schemata(conn)

    for schema in schema_dirs:
        if schema not in existing_schemas:
            schema_additions.append(schema)

    for schema in existing_schemas:
        if schema not in schema_dirs:
            schema_removals.append(schema)

    print("Schemata to be added: " + str(schema_additions))
    print("Schemata to be removed: " + str(schema_removals))

    confirm = yes_no_prompt("Is this okay?", "Continuing...", "Aborting.")

    if (confirm is False):
        sys.exit(0)

def analyze_tables(conn, schema_dirs, dblocation):
    cur = conn.cursor()
    file_table_list = []
    sql = "select table_name from information_schema.tables where table_schema = '{}'"
    for schema in schema_dirs:
        # this will eventually need to account for triggers.
        # when the time comes, we can probably use os.path.isdir
        table_names = next(os.walk(dblocation+"/"+schema))[2]
        sql = sql.format(schema)
        cur.execute(sql)
        db_tables = cur.fetchall()
        table_additions, table_removals = [], []
        schema_table_additions, schema_table_removals = (), ()
        
        for table in db_tables:
            if table not in table_names:
                table_removals.append(table[:-5])

        for table in table_names:
            if table not in db_tables:
                table_additions.append(table[:-5])

        schema_table_additions += (schema, table_additions,)
        schema_table_removals += (schema, table_removals,)

        print('Tables to be added: {}'.format(schema_table_additions))
        print('Tables to be removed: {}'.format(schema_table_removals))

    return [schema_table_additions, schema_table_removals]

def get_existing_schemata(conn):
    # there's most likely a more elegant way of going about this,
    # but this is a good place to start.
    sql = """SELECT schema_name FROM information_schema.schemata WHERE schema_owner != 'postgres';"""

    cursor = conn.cursor()
    cursor.execute(sql)
    existing_schemas = cursor.fetchall()
    schema_list = list(map(operator.itemgetter(0), existing_schemas))
    cursor.close()

    return schema_list

def yes_no_prompt(question, continue_message, abort_message):
    answer = input(question + " (y/n) ")
    if (answer != "Yes") and (answer != "yes") and (answer != "y"):
        confirm = False
        print(abort_message)
    else:
        confirm = True
        print(continue_message)

    return confirm

def startup():
    parser = argparse.ArgumentParser(description='Maintain your database structure using directories and files.')
    parser.add_argument("-l", "--location", dest="dblocation", required=False, type=str, help="The top directory of your database.")
    parser.add_argument("-a", "--analyze", dest="analyze_flag", required=False, type=bool, help="Build an analysis of the data.")
    args = parser.parse_args()

    dblocation = args.dblocation
    path = Path(dblocation)

    if os.path.isdir(str(path)) is not True:
        print("Specified directory does not exist or is not directory.")
        sys.exit(0)

    dbname = str(Path(dblocation)).split('/')[-1]

    confirm = yes_no_prompt("Look for updates on database \"%s\"?" % (dbname), "Analyzing file tree for %s." % (dbname), "Aborting.")
    if confirm is not True:
        sys.exit(0)

    basekeep_db_files = next(os.walk(dblocation))[2]

    if ("%s.json" % (dbname)) not in basekeep_db_files:
        print("Aborting, please make sure there's a %s.json file in your db directory. See README." % (dbname))
    elif ".secrets.json" not in basekeep_db_files:
        print("Aborting, no secrets file found for specified database. Add .secrets.json to db dir. See README.")

    secretspath = ""
    if str(path).endswith('/'):
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
        analyze_tables(conn, schema_dirs, dblocation)
        confirm = yes_no_prompt("Execute these changes against the database?", "Making changes...", "Aborting.")
        #execute_changes = 
        analyze_columns(conn, schema_dirs, dblocation)
        conn.close()
    except Exception as exception:
        print("Connection lost. Stack trace: ")
        print(exception)

startup()
