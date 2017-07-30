# basekeep
🏰 A file driven utility for maintaining your PostgreSQL database through version control.

## Purpose
basekeep is intended to make database structure maintainance easy. Databases are difficult to edit consistently because they are not tracked by version control. Therefore, basekeep will make changes to a database by using a file tree as a reference. It is only UNIX compatible, and does not have a Windows port planned.

**⚠️ Warning:** basekeep will also destroy things that are no longer represented in the file structure. **It is highly recommended to obtain a pg_dump of your entire database before running basekeep against it.** 

In the future, basekeep will generate a file tree based on the current state of the database.

If you're not sure, don't.

Talk to your DBA.

☢️ basekeep does not yet give a warning when it destroys entities.

## Setup
After you've decided on which database you'd like to track, you'll need to make a folder that has the same name as your database. For instance if you had an app with a database called "myappdb", your database folder will also be called "myappdb".

Inside this folder should be a list of important settings, such as users and user permissions. It should also contain folders named after schemas. 

Schema folders will contain JSON files for tables, and should also include a JSON file with the same name and having the entry `"is_schema": "true"`.

Create a user for this database named `basekeep` and grant it all permissions. Scary, right? Give it a password, or else 🔮.

In the database folder, please add a file called `.secrets.json`. In it, add an entry `"dbpass": BASEKEEP-PASSWORD`. Don't forget to add this file to your `.gitignore`.

TODO: Add password flag to program invokation. 

Usage: `python3 basekeep -l <db-folder>`

TODO: Undecided on trigger storage.