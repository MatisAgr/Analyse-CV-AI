"""
Script d'initialisation complète des données de test
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Initialiser les utilisateurs de test (admin, recruteur, 2 candidats)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Réinitialiser toutes les données (supprime et recrée)',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('INITIALISATION DES DONNÉES DE TEST'))
        self.stdout.write('='*60)

        # Étape 1: Créer les utilisateurs
        self.stdout.write('\n📋 Étape 1: Création des utilisateurs de test...')
        call_command('create_test_users', delete_existing=options['reset'])

        # Étape 2: Initialiser les groupes
        self.stdout.write('\n👥 Étape 2: Initialisation des groupes...')
        call_command('init_groups')

        # Résumé final
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('INITIALISATION TERMINÉE!'))
        self.stdout.write('\nCOMPTES POSTMAN:')
        self.stdout.write('-'*30)
        self.stdout.write('Admin: admin@cvanalyzer.com / AdminTest123!')
        self.stdout.write('Recruteur: marie.recruteur@cvanalyzer.com / RecruteurTest123!')
        self.stdout.write('Candidat 1: jean.martin@email.com / CandidatTest123!')
        self.stdout.write('Candidat 2: sophie.bernard@email.com / CandidatTest123!')
        
        self.stdout.write('\n🔗 API BASE URL: http://127.0.0.1:8000/api')
