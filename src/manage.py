#!/usr/bin/env python

"""Entry point for app, contain commands to configure and run the app."""

import csv
import os
import sys

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Shell, prompt_bool

from api.utils.initial_data import generete_initial_data_run_time_env
from app import create_app, db
from api.models import Center, Cohort, Society, Activity, Role, User
from run_tests import test


app = create_app(environment=os.environ.get('APP_SETTINGS', "Production"))
manager = Manager(app)


@manager.command
def drop_database():
    """Drop database tables."""
    if prompt_bool("Are you sure you want to lose all your data"):
        try:
            db.drop_all()
            print("Dropped all tables successfully.")
        except Exception:
            print("Failed, make sure your database server is running!")


@manager.command
def create_database():
    """Create database tables from sqlalchemy models."""
    try:
        db.create_all()
        print("Created tables successfully.")
    except Exception:
        db.session.rollback()
        print("Failed, make sure your database server is running!")


@manager.command
def seed():
    """Seed database tables with initial data."""
    environment = os.getenv("APP_SETTINGS", "Production")
    if environment.lower() in ["production", "staging"] and \
            os.getenv("PRODUCTION_SEED") != "True":
        print("\n\n\t\tYou probably don't wanna do that. Exiting...\n")
        sys.exit()

    if environment.lower() in ["production", "staging"]:
        print("Seeding data to DB: NOTE create, migrate and upgrade your DB")
        try:
            production_data = generete_initial_data_run_time_env()\
                .get('production_data')
            db.session.add_all(production_data)
            return print("Data dumped in DB succefully.")
        except Exception as e:
            db.session.rollback()
            return print("Error occured, database rolledback: ", e)

    else:
        print('You are in dev mode or test mode :-)')

        mes = "\n\n\nThis operation will remove all existing data" \
            " and create tables in your database\n" \
            " Type n to skip dropping existing data and tables."

        if environment != "Testing" and prompt_bool(mes):
            try:
                db.session.remove()
                db.drop_all()
                db.create_all()
                print("\nTables created successfully.\n")
            except Exception as e:
                db.session.rollback()
                return print("\nError while creating tables: ", e)

        try:
            dev_data = generete_initial_data_run_time_env().get('dev_data')
            db.session.add_all(dev_data)
            return print("\n\n\nTables seeded successfully.\n\n\n")
        except Exception as e:
            db.session.rollback()
            return print("\n\n\nFailed:\n", e, "\n\n")


def linker(cohort_name, society_name):
    """Link Cohorts with Society."""
    cohort = Cohort.query.filter_by(name=cohort_name).first()
    if not cohort:
        return print(
            f'Error cohort by name: {cohort_name} does not exist in DB.')
    if (cohort.society and
        not prompt_bool(f'Cohort:{cohort_name} has society:{cohort.society} '
                        ' already! \n Do you want to change to '
                        f'{society_name}?')):
        return 0

    society = Society.query.filter_by(name=society_name).first()
    if not society:
        return print(
            f'Error society with name:{society_name} does not exist.')

    society.cohorts.append(cohort)
    if society.save():
        message = f'Cohort:{cohort_name} succefully'
        message += f' added to society:{society_name}'
        return print(message)
    else:
        print('Error something went wrong when saving to DB. :-)')


@manager.command
def link_society_cohort_csv_data(path='data/cohort_data.csv'):
    """CLI tool, link cohort with society."""
    with open(path) as raw_data:
        csv_reader = csv.reader(raw_data)
        societies = None
        i = 0
        for row in csv_reader:
            if not i:
                societies = row
                i = 1
            else:
                for cohort_name, society_name in zip(row, societies):
                    linker(cohort_name.lower(), society_name.lower())


@manager.command
def tests():
    """Run the tests."""
    test()


def shell():
    """Make a shell/REPL context available."""
    return dict(app=app,
                db=db,
                User=User,
                Society=Society,
                Activity=Activity,
                Center=Center,
                Role=Role,
                Cohort=Cohort)


manager.add_command('shell', Shell(make_context=shell))
migrate = Migrate(app, db)
manager.add_command("db", MigrateCommand)

if __name__ == "__main__":
    manager.run()
