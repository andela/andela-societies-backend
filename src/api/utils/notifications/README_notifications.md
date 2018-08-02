# Andela Societies Notifications
## About
This module implements notifications for this Andela Societies notifications
## Goal
The goal of this project is to implement notifications asynchronously in the Andela Societies platform
## Features
With this module;
- You can send email notifications using mail gun
- TODO: You can send slack notifications
- TODO: You can send telegram notifications
## Requirements
- Use Python 3.x.x+
- Use Flask
## Tests
"Code without tests is broken as designed", said  [Jacob Kaplan-Moss](https://jacobian.org/writing/django-apps-with-buildout/#s-create-a-test-wrapper). Therefore i shall not give you code that
can not be tested or has no tests. So, to run tests, enter the following command
```sh
    $ python -m pytest src/tests/test_send_email.py
```
## Usage
To use this module;
- You need to install [RabbitMQ Server](https://www.rabbitmq.com/install-standalone-mac.html) (broker)
- You need to install [Celery](http://docs.celeryproject.org/en/latest/getting-started/first-steps-with-celery.html) (job server)

After successfully installing RabbitMQ, you will need to set a number of environment variables to get module working.
```bash
    $ export CELERY_BROKER_URL="amqp://username:password@localhost:port_number//"
    $ export CELERY_BACKEND="rpc://"

```

Then issue the following commands
```sh
    $ brew services start rabbitmq
    $ celery -A api.utils.notifications.celery worker
```
You need to set the following environment variables:
```bash
export MAIL_GUN_URL="Insert Mailgun URL here."
export MAIL_GUN_API_KEY="Insert Mailgun API Key here."
export SENDER_CREDS="Insert MailGun Credentials here."
export MAIL_GUN_TEST="Whichever string you want for the test variable."
```
Then in your module/controller do the following:
```python
# import the notifications
from api.utils.notifications.email_notices import send_email

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
            sender=current_app.config["SENDER_CREDS"]
        )
```
