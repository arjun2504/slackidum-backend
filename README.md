# slackidum-backend

This is a bakcend built with Django for [Slackidum](https://github.com/arjun2504/slackidum) web application.

- [django](https://www.djangoproject.com/) web framework
- [djangorestframwork](https://www.django-rest-framework.org/) - to build API endpoints
- [djang-channels](https://github.com/django/channels), for WebSocket
- [redis](https://redis.io/), as a backing store
- [postgresql](https://www.postgresql.org/), as a database

# Installation
Please make sure you that you have following prerequisites installed before installing on your machine.
- Python 3.5 or later
- Postgresql 9.4 or later
- Redis 5.0

### Steps

1. Clone this respository.
    ```
    $ git clone https://github.com/arjun2504/slackidum-backend.git
    $ cd slackidum-backend
    ```
2. Create a virtual envrionment.
    ```
    $ virtualenv venv
    $ source venv/bin/activate
    ```
3. Install the dependencies
    ```
    (venv) $ pip install -r requirements.txt
    ```
4. Open up `slackidum/settings.py` and modify your database settings.
    ```
    DATABASES = {
    'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'slackidum',
            'USER': 'postgres',
            'PASSWORD': 'postgres',
            'HOST': 'localhost',
            'PORT': '5432',
        }
    }
    ```
5. In case you are running redis on a different port, make sure your update it in the following code in the same file.
    ```
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                "hosts": [('127.0.0.1', 6379)],
            },
        },
    }
    ```
6. Migrate database.
    ```
    (venv) $ python manage.py makemigrations
    (venv) $ python manage.py migrate
    ```
7. Now serve the backend using:
    ```
    (venv) $ python manage.py runserver
    ```

## You're done!

Now its time to setup front end. Please look at [this repository](https://github.com/arjun2504/slackidum).
