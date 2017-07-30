#!/bin/python

import json
from pathlib import Path
import psycopg2
import argparse

parser = argparse.ArgumentParser(description='Maintain your database structure using directories and files.')
parser.add_argument("-l", "--location", dest="dblocation", required=True, type=str, help="The top directory of your database. Required.")
args = parser.parse_args()

dblocation = args.dblocation
path = Path(dblocation)

dbname = str(Path(dblocation)).split('/')[-1]

confirm = input("Run updates on database " + dbname + "? Some data may be lost.\n")

if (confirm == "Yes") or (confirm == "yes") or (confirm == "y"):
    print("Updating " + dbname)
else:
    print("Aborting.")

