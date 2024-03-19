from django.contrib.postgres.operations import CreateCollation

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        CreateCollation(
            'case_insensitive',
            provider='icu',
            locale='und-u-ks-level2',
            deterministic=False
        )
    ]