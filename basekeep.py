#!/usr/local/bin/python3

import argparse
import json
import operator
import os
from pathlib import Path
import psycopg2
import sys

#def execute_changes()

def analyze_database(conn, dbname, path):
    current_database_model = build_database_model(conn, dbname)
    user_database_model = get_user_json(path)

    schema_changes, table_changes, column_changes = [], [], []

    # first look for things missing from the current database model
    for schema in user_database_model:
        if schema not in current_database_model:
            schema_changes.append(['+', schema])

        for table in user_database_model[schema]:
            if table not in current_database_model[schema]:
                table_changes.append(['+', schema, table])

            for column in user_database_model[schema][table]:
                if column not in current_database_model[schema]:
                    column_changes.append(['+', schema, table, column])

    # then we'll look for extra things that the model has and we don't
    # in order to find removals
    for schema in current_database_model:
        if schema not in user_database_model:
            schema_changes.append(['-', schema])

        for table in current_database_model[schema]:
            if user_database_model[schema] and table not in user_database_model[schema]:
                table_changes.append(['-', schema, table])

            for column in current_database_model[schema][table]:
                if user_database_model[schema]:
                    if user_database_model[schema][table] and column not in user_database_model[schema][table]:
                        column_changes.append(['-', schema, table, column])

    print()

    print_changes('Schemas', schema_changes)
    print_changes('Tables', table_changes)
    print_changes('Columns', column_changes)

# returns a dictionary representation of the database
def build_database_model(conn, dbname):
    schemas = get_existing_schemata(conn)

    db_model = {}
    for schema in schemas:
        table_list = get_existing_tables(conn, schema)
        tables = {}
        for table in table_list:
            columns = get_existing_columns(conn, schema, table)
            tables[table] = columns
        db_model[schema] = tables

    return db_model

def get_existing_columns(conn, schema, table):
    sql = """select column_name from information_schema.columns where table_schema = '%s' and table_name = '%s' """ % (schema, table)
    cursor = conn.cursor()
    cursor.execute(sql)
    existing_columns = cursor.fetchall()
    column_list = list(map(operator.itemgetter(0), existing_columns))
    return column_list

def get_existing_tables(conn, schema):
    sql = """select table_name from information_schema.tables where table_schema = '%s' """ % (schema)
    cursor = conn.cursor()
    cursor.execute(sql)
    existing_tables = cursor.fetchall()
    table_list = list(map(operator.itemgetter(0), existing_tables))
    return table_list

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

def get_user_json(path):
    print("Getting user's JSON file...")
    with open(str(path), "r") as json_file:
        json_data = json.load(json_file)

    return json_data

def print_changes(relation_changing, relations):
    print(relation_changing + ':')
    
    for relation in relations:
        if relation_changing is 'Schemas':
            print(' {} {}'.format(relation[0], relation[1]))
        elif relation_changing is 'Tables':
            print(' {} {}.{}'.format(relation[0], relation[1], relation[2]))
        elif relation_changing is 'Columns':
            # will need to account for column type eventually
            print(' {} {}.{}.{}'.format(relation[0], relation[1], relation[2], relation[3]))

    print()

def write_json_to_file(dbname, db_model):
    print('Outputting to %s_current_state.json' % (dbname))
    file = open('%s_current_state.json' % (dbname), 'w')
    file.write(db_model)
    file.close()

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
    # These flags are not being used the way they should be.
    # TODO: read up on the right way to do this.
    # Might be able to use docopt
    parser = argparse.ArgumentParser(description='Maintain your database structure using directories and files.')
    parser.add_argument("-b", "--build-model", dest="build_flag", required=False, type=str, help="Build an analysis of the database.")
    parser.add_argument("-e", "--execute", dest="dblocation", required=False, type=str, help="The top directory of your database.")
    parser.add_argument("-n", "--name", dest="dbname", required=False, type=str, help="Name of your database.")
    args = parser.parse_args()

    if args.dblocation:
        dblocation = args.dblocation
        path = Path(dblocation)
        #make_db_edits(dblocation, path, args)
        dbname = args.dbname
        conn = psycopg2.connect("dbname='%s'" % (dbname))
        analyze_database(conn, dbname, path)

    if args.build_flag:
        conn = psycopg2.connect("dbname='%s'" % (dbname))
        dbname = args.build_flag
        database_model = build_database_model(conn, dbname)
        write_json_to_file(dbname, json.dumps(database_model, sort_keys=False, indent=4))

startup()
