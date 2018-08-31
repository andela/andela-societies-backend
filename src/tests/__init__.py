import os
import sys

# this will enable us to run individual test files
# pytest <path to file>
# e.g pytest tests/test_logged_activities.py
# Run individual test within class
# e.g pytest <path to file>.py::ClassName::test_method_name


sys.path.insert(0,
                os.path.abspath(
                    os.path.join(os.path.dirname(__file__), '..')))
