__author__ = "Brian O'Neill"
__version__ = '0.3.0'


from unittest import TestCase


class TestDF(TestCase):

    def test__history_as_DataFrame(self):
        from log_calls import record_history

        @record_history()
        def f(a, b, x):
            return a*x + b

        for i in range(1000): f(3, 5, i)

        df = f.stats.history_as_DataFrame

        try:
            import pandas as pd
        except ImportError:
            self.assertEqual(df, None)
        else:
            self.assertIsInstance(df, pd.DataFrame)
            self.assertEqual(len(df.retval), 1000)
