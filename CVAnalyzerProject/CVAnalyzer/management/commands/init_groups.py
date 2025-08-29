from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

class Command(BaseCommand):
    def handle(self, *args, **options):
        for name in ['Administrateurs', 'Recruteurs', 'Candidats']:
            Group.objects.get_or_create(name=name)
        self.stdout.write('Groupes créés')
