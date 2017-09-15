# basekeep
A utility for maintaining your PostgreSQL database through files and tracking its history in version control.

## Release notes

⚠️ **This repo is a work-in-progress.** The only feature that's currently working and stable is the `-b` flag, which will build and output a database model in the JSON format.

## Motivation

`basekeep` is intended to make database structure maintainance easy. Databases are difficult to edit consistently because they do not use simple files to imitate their structure and are not tracked by version control. Therefore, this utility will make changes to a Postgres database by using a file tree as a reference. It is only UNIX compatible, and does not have a Windows port planned (yet).

**⚠️ Warning:** basekeep will destroy things that are no longer represented in the file structure. It is highly recommended to create a pg_dump of your entire database before running basekeep against it.

In the future, `basekeep` will help first-time setup by generating a file tree based on the current state of the database. (✅ `basekeep` can now generate a JSON file representation of the database.)

Talk to your DBA. If you're not sure, don't.

## Setup

###Models

If you only want a database model, there are no further steps! Simply invoke with the `-b` flag and specify the database you'd like to analyze.

###Comparators (incomplete)

After you've decided on which database you'd like to track, you'll need to make a folder that has the same name as your database. For instance if you had an app with a database called "myappdb", your database folder will also be called "myappdb".

Inside this folder should be a list of important settings ("myappdb.json"), such as users and user permissions (TODO. For now, the only required entry is `"is_basekeep_db": "true"`). The db folder should also contain directories named after schemas. 

Schema folders should include a JSON file with the same name and having the entry `"is_schema": "true"`. They will also contain JSON files describing tables.

Create a user for this database named `basekeep` and grant it all permissions. Give it a password, or else 🔮.

In the database folder, please add a file called `.secrets.json`. In it, add an entry `"dbpass": BASEKEEP-PASSWORD`. Don't forget to add this file to your `.gitignore`.

TODO: Add password flag to program invokation. 

TODO: Undecided on trigger storage.

## Conventions
A proper `basekeep` directory tree should look like this:

```
database/{database.json, schema1, schema2, schema1.json, schema2.json}/
schema1/{table1.json, table2.json, table1/, table2/}
table1/{trigger1.sql, trigger2.sql}
```

JSON files are used for tracking attributes of the object immediately above them, except in the case of tables, which use JSON to describe the columns and data types.

`basekeep` must be the owner of all objects its manipulating -- be careful! If you made some schemas and tables on a different account, `basekeep` will not see them, since it uses psycopg2 to query for these entities.

### Requirements
Database JSON file:

```
{
  "is_basekeep_db": "true"
}
```
Right now the presence of this entry is not important, but `basekeep` will look for this file when analyzing the directories. This is a contract saying, "I promise I want to use basekeep *here*."

## Usage
`./basekeep -b <dbname>`

Builds a model of the specified database and outputs it to a JSON file.

`./basekeep -l <db-folder>`

Relative or absolute paths can be used in this invokation. 