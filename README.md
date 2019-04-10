[![Codacy Badge](https://api.codacy.com/project/badge/Grade/c192df4792dd45e6b8ba687ad5b283d2)](https://www.codacy.com/app/AndelaOS/andela-societies-backend?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=andela/andela-societies-backend&amp;utm_campaign=Badge_Grade)
[![Maintainability](https://api.codeclimate.com/v1/badges/6424fe59a14ce0148125/maintainability)](https://codeclimate.com/github/andela/andela-societies-backend/maintainability)
[![CircleCI](https://circleci.com/gh/andela/andela-societies-backend.svg?style=svg)](https://circleci.com/gh/andela/andela-societies-backend)
[![Coverage Status](https://coveralls.io/repos/github/andela/andela-societies-backend/badge.svg)](https://coveralls.io/github/andela/andela-societies-backend)

# Andela-Societies ✍
### API for Andela Societies.


The Andela Societies are an awesome platform for collaboration and relationship-building across all centers of Andela for all fellows.
They give all Fellows a common ground to interact and know about each other regardless as to the geographical location of each one of them.
This way location of the Fellow does not stand in the way of the opportunity for long-lasting collaborative relationships being formed.


- ## API
This App exposes endpoints that allows ```clients/Users``` to interact with Andela society Platform.

- #### Available Resource Endpoints

|Method | Endpoint | Usage |
| ---- | ---- | --------------- |
|POST| `/api/v1.0/login` | Login user.|
|POST| `/api/v1/activities` or `/api/v1/activities/` | Create an activity.|
|GET| `/api/v1/activity-types` or `/api/v1/activity-types/` | Get information on activity types.|
|POST| `/api/v1/logged-activities` or `/api/v1/logged-activities/` | Log a new activity.|
|DELETE| `/api/v1/logged-activities/{logged_activity_id}` or `/api/v1/logged-activities/{logged_activity_id}/` | Delete a logged activity.|
|PUT| `/api/v1/logged-activities/{logged_activity_id}` or `/api/v1/logged-activities/{logged_activity_id}/` | Edit a logged activity.|
|POST| `/api/v1/societies` or `/api/v1/societies/` | Create a society.|
|PUT| `/api/v1/societies/{society_id}` or `/api/v1/societies/{society_id}/` | Edit a society.|
|GET| `/api/v1/user/profile` or `/api/v1/user/profile/` | Get user information.|
|GET| `/api/v1/users/{user_id}/logged-activities` | Get a user's logged activities by user_id URL parameter.|



## Getting Started 🕵
- To run on local machine git clone this project :
```
 $ git clone https://github.com/AndelaOSP/andela-societies-backend.git
 ```

 Copy and paste the above command in your terminal, the project will be downloaded to your local machine.

- To consume API in client of choice navigate to:
 ```
 http://api-staging-societies.andela.com/
 ```

### Prerequisites
The application is built using python: Flask framework.
>[Flask](http://flask.pocoo.org/) is a micro-framework for the Python programming language.


To Install python checkout:
```
https://www.python.org/
```


### Installing
For this section I will assume you have python3 and it's configured on your machine. </br>
Navigate to the folder you cloned and run: </br>

##### Get configuration .env from the team channel or ask the team TTL

#### Using Docker

   - Install docker on your machine
       - [Docker](https://www.docker.com/get-started)


   - Navigate to src folder within the project, then run

      ```
         docker-compose build
      ```

    - Run this to start the server

        ```
        docker-compose up
        ```
    - Useful Commands you might need

        - Connect to the running web service
            ```
            $ docker-compose exec python-web-api-dev  bash
            ```

        - Delete containers (in case something breaks)

            ```
            docker-compose down
            ```
        - Commands that you can run inside the container
            ```
            # seed data

            $ python manage.py db seed

            # setup migrations

            $ python manage.py db init # run once at initialization
            $ python manage.py db migrate # run whenever you change the models
            $ python manage.py db upgrade # apply the changes to the db
            ```

#### Manual Way

- Install Requirements
```
$ cd src
$ pip install -r requirements.txt
```

- Configure Environment
```
export SECRET="Thequickbrownfoxjumpedoverthelazydog"
export APP_SETTINGS=Development
FLASK_APP=manage.py
export DEV_DATABASE=database_url_for_development_environment
export TEST_DATABASE=database_url_for_testing_environment
export ANDELA_API_URL=https://api.andela.com/api/v1/
export DEV_TOKEN=token_from_signed_in_webapps
```
> Note replace the value for DATABASE_URL & TEST_DATABASE with a real database path and SECRET with a strong string value

- Run App 🏃
```
$ cd src
$ python manage.py run
```
The app should be accessible via : http://127.0.0.1:5000/


## Running the tests

```
$ cd src
$ python manage.py test
```

- Coding style tests

[PEP8](https://pypi.org/project/pycodestyle/) (pycodestyle) standards are followed in project. </br>
PEP8 has deprecated; instead use pycodestyle for the same effect

```
$ cd src
$ pycodestyle .

```

## Database Seeding 🔂

You will need the following extra environment variables to seed the database.
```
export PRIVATE_KEY_TEST=""
export PUBLIC_KEY_TEST=""
export PUBLIC_KEY=""
export DEV_TOKEN=""
export APP_SETTINGS="Development"
FLASK_APP=manage.py
```
The value of this variables are obtained from the TTL, or the DevOps engineer in the team.

Seed the database.
```
$ python manage.py db seed
```
## Running the sandbox
Follow the instructions on this [link](docker/dev/sandbox.md) to run it.

In case of any errors ask the DevOps Engineer in the team

## Set Up Notifications Package
 - [Check this out to set up the Notifications Package](src/api/utils/notifications/README_notifications.md)

## Deployment 🚀

- [Check this out to deploy to heroku](https://devcenter.heroku.com/articles/getting-started-with-python#introduction)

## Built With  🏗 🔨⚒

* [Flask](http://flask.pocoo.org/) - The web framework used
* [Flaskrestplus](https://flask-restplus.readthedocs.io/en/stable/) - Extension for Flask that adds support for quickly building REST APIs.

## Contributing 👍

- Please Fork me! :-)

## Versioning ⚙

- [Checkout our releases](https://github.com/AndelaOSP/andela-societies-backend/releases)

## Authors 📚

* **AndelaOSP**


## License 🤝

- This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments 🙏

* [Andela ](https://andela.com/) - We are hiring !
* [Motivation](https://www.youtube.com/watch?v=dQw4w9WgXcQ) - BEST RESOURCE EVER!!! 🤓🤓
