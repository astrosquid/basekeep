# basekeep
🏰 A file driven utility for maintaining your PostgreSQL database through version control.

## Setting up database tracking
After you've decided on which database you'd like to track, you'll need to make a folder (in the appropriate location within your project's repo) that has the same name as your database. For instance if you had an app with a database called "myappdb", your database folder will also be called "myappdb".

Inside this folder should be a list of important settings, such as users and user permissions. It should also contain folders named after schemas. 

Schema folders will contain JSON files for tables, and should also include a JSON file with the same name having the entry `"is_schema": "true"`.

Create a user for this database named `basekeep` and grant it all permissions. Scary, right? Give it a password. 🔮

In the database folder, please add a file called `.secrets.json`. In it, add an entry `"dbpass": BASEKEEP-PASSWORD`. Don't forget to add this file to your `.gitignore`.

Usage: `python3 basekeep -l <db-folder>`

TODO: Add password flag to program invokation. 

TODO: Undecided on trigger storage.