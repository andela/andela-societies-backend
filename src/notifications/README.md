# Andela Societies Notifications
## About
This module implements notifications for this Andela socities notifications
## Goal
The goal of this project is to implement notifications asynchronously in the Andela socities platform
## Features
With this module;
- You can send email notifications using mail gun
- TODO: You can send slack notifications
- TODO: You can send telegram notifications
## Requirements
- Use Python 3.x.x+
- Use Django 2.x.x+
## Tests
"Code without tests is broken as designed", said  [Jacob Kaplan-Moss](https://jacobian.org/writing/django-apps-with-buildout/#s-create-a-test-wrapper). Therefore i shall not give you code that
can not be tested or has no tests. So, to run tests, enter the following command
```sh 
    $ python -m pytest src/notifications/tests
```
## Usage
To use this module;
- You need to install [rabbitMQ server](https://www.rabbitmq.com/install-standalone-mac.html) (broker)
- You need to install [celery](http://docs.celeryproject.org/en/latest/getting-started/first-steps-with-celery.html) (job server)
Then issue the following commands
```sh
    $ brew services start rabbitmq
    $ celery -A src.notifications.celery worker
```
You need to set the following environment variables:
```bash
export MAIL_GUN_URL=https://api.mailgun.net/v3/sandbox1ce36b0401fd4c929ee864bc19bf44e7.mailgun.org/messages
export MAIL_GUN_API_KEY=fef6a810b6acceac40cf2fcb1ebac4fe-0470a1f7-a03c7123
```
Then in your module/controller do the following:
```python
# import the notifications
from src.notifications.celery import send_email
   
...

class SomeEndPoint(Resource):
    def post(self):
        # some other business logic here
        ...
        # At this point you need to send the email
        send_email.delay(
            subject="Test email",
            message="This is a test message",
            recipients=["andela.project@gmail.com"],
            sender="Mailgun Sandbox <postmaster@sandbox1ce36b0401fd4c929ee864bc19bf44e7.mailgun.org>"
        )
```