
from django.core.management import call_command
from django.db.utils import OperationalError
from unittest.mock import patch

from django.test import TestCase

class CommandTest(TestCase):


    @patch('core.management.commands.wait_for_db.Command.check')
    def test_wait_for_db(self, patched_check):
        patched_check.return_value = True

        call_command('wait_for_db')

        patched_check.assert_called_once_with(databases=['default'])

    @patch('time.sleep', return_value=None)
    @patch('core.management.commands.wait_for_db.Command.check')
    def test_wait_for_db_ready(self, patched_check, patched_sleep):
       
        # Simule des erreurs puis un succès
        patched_check.side_effect = [OperationalError] * 5 + [True]

        call_command('wait_for_db')

        self.assertEqual(patched_check.call_count, 6)