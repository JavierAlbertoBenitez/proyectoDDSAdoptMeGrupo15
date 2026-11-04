"""
Agrega usuarios.email_verificado (RF02). Los usuarios que ya existian (los 3
genericos de 0019 y los que se registraron antes) quedan verificados, para que
puedan seguir entrando. Los que se registren desde ahora arrancan sin verificar.
"""

from django.db import migrations, models


def verificar_existentes(apps, schema_editor):
    Usuarios = apps.get_model('adopciones', 'Usuarios')
    Usuarios.objects.update(email_verificado=True)


class Migration(migrations.Migration):

    dependencies = [
        ('adopciones', '0020_alertas_publicacion_borrada'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuarios',
            name='email_verificado',
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(verificar_existentes, migrations.RunPython.noop),
    ]
