[![Codacy Badge](https://api.codacy.com/project/badge/Grade/afbc8438e34a48fea86d20a953bf6998)](https://app.codacy.com/app/jonathankamau/andela-societies-backend?utm_source=github.com&utm_medium=referral&utm_content=AndelaOSP/andela-societies-backend&utm_campaign=badger)
[![Maintainability](https://api.codeclimate.com/v1/badges/f5db32ea8acc28bd7790/maintainability)](https://codeclimate.com/github/AndelaOSP/andela-societies-backend/maintainability)
[![CircleCI](https://circleci.com/gh/AndelaOSP/andela-societies-backend.svg?style=svg)](https://circleci.com/gh/AndelaOSP/andela-societies-backend)
[![Coverage Status](https://coveralls.io/repos/github/AndelaOSP/andela-societies-backend/badge.svg)](https://coveralls.io/github/AndelaOSP/andela-societies-backend)

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

- Install Requirements
```
$ cd src
$ pip install -r requirements.txt
```

- Configure Environment
```
export SECRET="Thequickbrownfoxjumpedoverthelazydog"
export APP_SETTINGS=Development
export DEV_DATABASE=database_url_for_development_environment
export TEST_DATABASE=database_url_for_testing_environment
export ANDELA_API_URL=https://api.andela.com/api/v1/
export DEV_TOKEN=token_from_signed_in_webapps
```
> Note replace the value for DATABASE_URL & TEST_DATABASE with a real database path and SECRET with a strong string value

- Run App 🏃
```
$ cd src
$ python manage.py runserver
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

## Database Seeding

You will need the following extra environment variables to seed the database.
```
export PRIVATE_KEY_TEST=""
export PUBLIC_KEY_TEST=""
export PUBLIC_KEY=""
export DEV_TOKEN=""
export APP_SETTINGS="Development"
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
