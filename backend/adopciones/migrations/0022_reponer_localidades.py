"""
Migracion de datos: vuelve a cargar las localidades del catalogo
(data/georef_argentina.json) que falten en la base. Por ejemplo, a algunas bases
les faltaba la localidad Campana (y Otamendi y Rio Lujan) del partido de Campana.
Las que ya estan no se tocan (ignore_conflicts), asi que se puede correr siempre.
"""

import json
from pathlib import Path

from django.db import migrations

ARCHIVO = Path(__file__).resolve().parent.parent / 'data' / 'georef_argentina.json'


def reponer_localidades(apps, schema_editor):
    Localidades = apps.get_model('adopciones', 'Localidades')

    with open(ARCHIVO, encoding='utf-8') as archivo:
        datos = json.load(archivo)

    existentes = set(Localidades.objects.values_list('id_localidad', flat=True))
    Localidades.objects.bulk_create(
        [Localidades(id_localidad=id, departamento_id=departamento_id, nombre=nombre)
         for id, departamento_id, nombre in datos['localidades'] if id not in existentes],
        ignore_conflicts=True
    )


class Migration(migrations.Migration):

    dependencies = [
        ('adopciones', '0021_email_verificado'),
    ]

    operations = [
        migrations.RunPython(reponer_localidades, migrations.RunPython.noop),
    ]
