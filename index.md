This page will eventually contain the documentation for this project

# Installation

1.  Fetch project

```
ljleppan@hp8x-42:~$ git clone git@github.com:ljleppan/pure-rng-decks.git
Cloning into 'pure-rng-decks'...
remote: Counting objects: 237, done.
remote: Compressing objects: 100% (170/170), done.
remote: Total 237 (delta 83), reused 212 (delta 59), pack-reused 0
Receiving objects: 100% (237/237), 6.32 MiB | 2.92 MiB/s, done.
Resolving deltas: 100% (83/83), done.
Checking connectivity... done.
```

2. Activate Virtual Environment
```
ljleppan@hp8x-42:~$ source venv/bin/activate
```

3. Switch to project root
```
(venv) ljleppan@hp8x-42:~$ cd pure-rng-decks/
```

4. Install dependencies
```
(venv) ljleppan@hp8x-42:~/pure-rng-decks$ pip install -r requirements.txt
```

6. Switch to app directory
```
(venv) ljleppan@hp8x-42:~/pure-rng-decks$ cd app/
```

7. Initialize database
```
(venv) ljleppan@hp8x-42:~/pure-rng-decks/app$ python manage.py migrate
Operations to perform:
  Apply all migrations: admin, auth, cards, contenttypes, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying admin.0002_logentry_remove_auto_add... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0002_alter_permission_name_max_length... OK
  Applying auth.0003_alter_user_email_max_length... OK
  Applying auth.0004_alter_user_username_opts... OK
  Applying auth.0005_alter_user_last_login_null... OK
  Applying auth.0006_require_contenttypes_0002... OK
  Applying auth.0007_alter_validators_add_error_messages... OK
  Applying auth.0008_alter_user_username_max_length... OK
  Applying cards.0001_squashed_0004_auto_20160802_0827... OK
  Applying cards.0002_auto_20160802_1410... OK
  Applying cards.0003_card_simple_value... OK
  Applying cards.0004_auto_20160802_1532... OK
  Applying cards.0005_card_image... OK
  Applying cards.0006_auto_20160807_1326... OK
  Applying sessions.0001_initial... OK

```

8. Create a superuser account
```
(venv) ljleppan@hp8x-42:~/pure-rng-decks/app$ python manage.py createsuperuser
Username (leave blank to use 'ljleppan'):
Email address:
Password:
Password (again):
Superuser created successfully.
```

9. Modify line 6 of `/cards/lib/importer.py` so that the variable `MASHAPE_KEY` contains a valid API key to the API at https://market.mashape.com/omgvamp/hearthstone.
```
MASHAPE_KEY = "ADD_KEY_HERE"
```

10. Start the server
```
(venv) ljleppan@hp8x-42:~/pure-rng-decks/app$ python manage.py runserver
Performing system checks...

System check identified no issues (0 silenced).
December 09, 2016 - 09:47:37
Django version 1.10.3, using settings 'app.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.

```

11. Browse to http://localhost:8000/admin/ and log in

12. Browse to http://localhost:8000/populate_db. Wait for the program to populate the database from the API. You know the process is complete when you see a page with the text "Done!".

NB: If you get a HTTP Error 403: Forbidden, you either skipped step 9 or provided an incorrect API key.

13. Browse to http://localhost:8000/admin/cards/card/ and verify that the database got populated.

NB: The next step will take a long time, up to 15 minutes.

14. Browse to http://localhost:8000/learn and wait for the page to return "Done!".

15. You are done. To generate a deck, browse to http://localhost:8000/create for a demo of the individual card creation. 
