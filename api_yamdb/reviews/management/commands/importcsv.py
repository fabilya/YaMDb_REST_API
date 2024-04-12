import csv
import traceback

from django.core.management.base import BaseCommand

from api_yamdb.settings import BASE_DIR, STATIC_URL
from reviews.models import Category, Comment, Genre, GenreTitle, Review, Title
from reviews.models import User

PATH = str(BASE_DIR) + STATIC_URL + 'data/'

IMPORT_ERROR = 'Error while import data from "{file}": {error}.'
IMPORT_SUCCESS = 'Data imported from "{file}" successfully.'


def purge_model(model):
    model.objects.all().delete()
    return


def simple_import_csv(file, model):
    model.objects.bulk_create(model(**data) for data in csv.DictReader(file))
    return


def alter_fields(row, fields):
    for field, value in fields:
        if isinstance(value, str):
            # alter field name
            row[value] = row.pop(field)
        else:
            # build relation
            row[field] = value.objects.get(pk=row[field])
    return row


def import_csv(filename, model, fields=None, clear=False, encoding='utf-8'):
    """
    Import data from CSV file to django Model.

    If every column of given file matches Model fields names
    and Model has no relations, pass only required params.

    Specify fields param to alter column names or build relations.
    Important note: always build relations BEFORE altering names.

    Required arguments:
    :param filename: filename-string with extension without path
    :param model: django Model where to save imported data

    Optional arguments:
    :param fields: tuple -> (field, value)
           field: column in given file to alter name or build relation
           value:
               a) Model to build foreign key
               b) string to match Model field name
           Important note: always build relations BEFORE altering names
    :param clear: if set TRUE delete all data before import
    :param encoding: specify file encoding

    :return: None
    """
    if clear:
        purge_model(model)
    try:
        with open(PATH + filename, 'r', encoding=encoding) as file:
            if not fields:
                simple_import_csv(file, model)
            else:
                for row in csv.DictReader(file):
                    row = alter_fields(row, fields)
                    model.objects.create(**row)
            print(IMPORT_SUCCESS.format(file=filename))
    except Exception as error:
        print(IMPORT_ERROR.format(file=filename, error=error))
        print(traceback.format_exc())
    return


class Command(BaseCommand):
    def handle(self, *args, **options):
        import_csv('users.csv', User)
        import_csv('category.csv', Category, clear=True)
        import_csv('genre.csv', Genre, clear=True)
        import_csv(
            filename='titles.csv',
            model=Title,
            fields=(
                ('category', Category),
            ),
            clear=True,
        )
        import_csv(
            filename='genre_title.csv',
            model=GenreTitle,
            fields=(
                ('title_id', Title),
                ('title_id', 'title'),
                ('genre_id', Genre),
                ('genre_id', 'genre'),
            ),
            clear=True,
        )
        import_csv(
            filename='review.csv',
            model=Review,
            fields=(
                ('title_id', Title),
                ('title_id', 'title'),
                ('author', User),
            ),
            clear=True,
        )
        import_csv(
            filename='comments.csv',
            model=Comment,
            fields=(
                ('review_id', Review),
                ('review_id', 'review'),
                ('author', User),
            ),
            clear=True,
        )
