"""Module containing run tests function."""
import coverage
import pytest


def test():
    """Run tests with coverage."""
    # Testing configurations
    COV = coverage.coverage(
        branch=True,
        omit=[
            '*/tests/*',
            '*/marshmallow_schemas.py',
            'manage.py',
            '*/.virtualenvs/*',
            '*/venv/*',
            'config.py',
            '*/site-packages/*',
            '*/__init__.py',
            '*/initial_data.py',
            'run_tests.py'
        ]
    )
    COV.start()

    tests_failed = pytest.main(['-x', '-v', '-s', 'tests'])

    COV.stop()
    if not tests_failed:
        COV.save()
        print('Coverage Summary:')
        COV.report(show_missing=True)
        COV.html_report()
        COV.erase()
        return 0
    return 1


if __name__ == '__main__':
    test()
