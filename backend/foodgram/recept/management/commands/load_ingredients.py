from csv import DictReader

from django.core.management import BaseCommand

from recept.models import Ingredient

ALREDY_LOADED_ERROR_MESSAGE = """
If you need to reload the child data from the CSV file,
first delete the db.sqlite3 file to destroy the database.
Then, run `python manage.py migrate` for a new empty
database with tables"""


class Command(BaseCommand):
    help = "Loads data from ingredients.csv"

    def handle(self, *args, **options):
        if Ingredient.objects.exists():
            print('ingredient data already loaded...exiting.')
            print(ALREDY_LOADED_ERROR_MESSAGE)
            return
        for row in DictReader(open('./static/ingredients.csv', encoding='UTF8')):
            ingredient=Ingredient(name=row['name'], measurement_unit=row['measurement_unit'])
            ingredient.save()