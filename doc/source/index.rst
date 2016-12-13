

.. contents::

Project overview
----------------

Pure-RNG-Decks is a creative multiagent system that builds [Hearthstone](https://en.wikipedia.org/wiki/Hearthstone_(video_game)) decks.

Our system consists of three types of agents:

1. **CardCreatorAgents** create new Hearthstone cards based on an inspiring set of existing cards.

2. **GatekeeperAgents** ensure that the created cards are *fair* ("valuable") and *novel*. Fairness is evaluated using a regression model based on an inspiring set. Novelty is evaluated in terms of how similar the card is to other, previously seen cards.

3. **DeckBuilderAgents** build decks (sets of 30 cards) out of the cards accepted by GateKeeperAgents. At this point, their inner logic is very rudimentary, but we are working on a more complex deck builder. We would like different deck builders to value f.ex. aggressive or defensive cards.

Fair Cards
----------

The fairness of a Hearthstone card is not an easy subject: even the makers of the game have made some questionable decisions. As mentioned above, we use a regression model to ensure that the cards are fair. The following is a more detailed explanation of this model: We construct from real Heathstone cards a traning set, where the features are the known card mechanics and the card *stats* such as health and attack values. We then use ridge regression to fit a regression model that outputs the mana cost for a card given all the other features of that card as input. The idea here is simple: existing cards should be approximately fair, so their mana cost should approximate the combined "value" of their features. We can then use the coefficients learned from fitting this model to evaluate new, previously unseen cards. Such a previously unseen card can then be considered "fair" if its evaluated mana cost is within a reasonable range of the actual mana cost.

Project structure
-----------------

The project is built on top of the [Django web framework](https://www.djangoproject.com/). This allows us to use web pages as a user interface. Still, the project is not designed to be exposed to a larger audience as the computations are quite heavy: in other words, it's an *intranet-only web service*.

The high-level structure is as follows

::

  . # Project root
  ├── app
  │   ├── app/ # Server settings
  │   ├── cards
  │   │   ├── admin.py # Configuration for Admin UI
  │   │   ├── apps.py  # General configuration
  │   │   ├── lib
  │   │   │   ├── agents
  │   │   │   │   ├── card_creator_agent.py # Creates cards
  │   │   │   │   ├── deck_creator_agent.py # Creates decks
  │   │   │   │   ├── environment.py        # Contains all live agents
  │   │   │   │   ├── evaluator.py          # Helper for evaluating the fairness of cards
  │   │   │   │   └── gatekeeper_agent.py   # Ensures card fairness and novelty
  │   │   │   ├── card_generator.py  # Helper for web UI
  │   │   │   ├── deck_generator.py  # Helper for web UI
  │   │   │   ├── importer.py        # Fetches real card data
  │   │   │   └── learner.py         # Regression model
  │   │   └── ...
  │   ├── db.sqlite3           # Database
  │   ├── heathstonedata.npy   # Cache for learning data
  │   └── ...
  ├── requirements.txt
  └── ...

See the .py files in /app/cards/lib/ for the classes specific to Hearthstone.

Other remarks
-------------

We chose not to go with any existing multi-agent system frameworks, as in our view they bring unnecessary complexities while not being of great help. Notably, even asynchronous multiagent system frameworks are largely unable to allow for any concrete speedup due to the [Python GIL](https://wiki.python.org/moin/GlobalInterpreterLock) only allowing one thread to execute at a time.

Installation
------------

Fetch project

::

  ~$ git clone git@github.com:ljleppan/pure-rng-decks.git
  Cloning into 'pure-rng-decks'...
  remote: Counting objects: 237, done.
  remote: Compressing objects: 100% (170/170), done.
  remote: Total 237 (delta 83), reused 212 (delta 59), pack-reused 0
  Receiving objects: 100% (237/237), 6.32 MiB | 2.92 MiB/s, done.
  Resolving deltas: 100% (83/83), done.
  Checking connectivity... done.


Activate Virtual Environment

::

  ~$ source venv/bin/activate


Switch to project root

::

  (venv) ~$ cd pure-rng-decks/


Install dependencies

::

  (venv) ~/pure-rng-decks$ pip install -r requirements.txt

Switch to app directory

::

  (venv) ~/pure-rng-decks$ cd app/

Initialize database

::

  (venv) ~/pure-rng-decks/app$ python manage.py migrate
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

Create a superuser account

::

  (venv) ~/pure-rng-decks/app$ python manage.py createsuperuser
  Username (leave blank to use 'ljleppan'):
  Email address:
  Password:
  Password (again):
  Superuser created successfully.

Modify line 6 of `/cards/lib/importer.py` so that the variable `MASHAPE_KEY` contains a valid API key to the API at https://market.mashape.com/omgvamp/hearthstone. See project Moodle page in Univ. Helsinki Moodle for an API key that can be used for temporary and light-weight testing.

::

  MASHAPE_KEY = "ADD_KEY_HERE"


Start the server

::

  (venv) ~/pure-rng-decks/app$ python manage.py runserver
  Performing system checks...

  System check identified no issues (0 silenced).
  December 09, 2016 - 09:47:37
  Django version 1.10.3, using settings 'app.settings'
  Starting development server at http://127.0.0.1:8000/
  Quit the server with CONTROL-C.

Browse to http://localhost:8000/admin/ and log in

Browse to http://localhost:8000/populate_db. Wait for the program to populate the database from the API. You know the process is complete when you see a page with the text "Done!".

**NB:** If you get a HTTP Error 403: Forbidden, you either skipped step 9 or provided an incorrect API key.

Browse to http://localhost:8000/admin/cards/card/ and verify that the database got populated.

**NB:** The next step will take a long time, up to 15 minutes.

Browse to http://localhost:8000/learn and wait for the page to return "Done!".

You are done. You can browse to http://localhost:8000/create/card for a demo of the individual card creation, or to http://localhost:8000/create/deck to try out the (Work-In-Progress) deck creator.

# Running the system

On subsequent times, it is enough to start the server using `python manage.py runserver`, and then browsing to http://localhost:8000

.. include:: modules.rst
