import csv
import os

from django.core.management.base import BaseCommand

from recipe.models import Ingredient, Tag

LOCAL_DIR = '/app/data/'
files_csv = {
    'ingredients.csv': Ingredient,
    'tags.csv': Tag,
}


def import_data():
    for file, model in files_csv.items():
        dataReader = csv.DictReader(
            open(
                os.path.join(LOCAL_DIR, file),
                encoding='utf-8',
            ),
        )
        model.objects.bulk_create(model(**row) for row in dataReader)


class Command(BaseCommand):
    help = 'Imports data from a CSV file into the Tags and Ingredients models'

    def handle(self, *args, **options):
        import_data()
        self.stdout.write(self.style.SUCCESS('Data imported successfully'))
