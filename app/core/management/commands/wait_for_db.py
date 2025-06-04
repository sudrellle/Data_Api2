from django.core.management.base import BaseCommand
import time
from django.db.utils import OperationalError
from psycopg2 import OperationalError as Psycopg2OpError

class Command(BaseCommand):
    """Django command to wait for database."""
    
    def handle(self, *args, **options):
        """Entrypoint for command."""
        self.stdout.write('Waiting for db...')
        db_up = False
        while not db_up:
            try:
                self.check(databases=['default'])  
                db_up = True
            except (Psycopg2OpError, OperationalError):
                self.stdout.write('Database indisponible, attente 1s...')
                time.sleep(1)
        
        self.stdout.write(self.style.SUCCESS('Database disponible'))