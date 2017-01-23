This test is NOT a package (doesn't have an __init__.py), to prevent its
"discovery" by unittest. It messes up other tests when it's run together
with them.

To run this test, simply run
    $ python3 test_global_set_reset_defaults.py
from the log_calls/tests/set_reset_defaults/ directory.
