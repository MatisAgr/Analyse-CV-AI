# IA
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from CVAnalyzer.models import User


class Command(BaseCommand):
    help = 'Créer des utilisateurs de test pour l\'application CV Analyzer'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete-existing',
            action='store_true',
            help='Supprimer les utilisateurs existants avant création',
        )

    def handle(self, *args, **options):
        # Supprimer les utilisateurs existants si demandé
        if options['delete_existing']:
            self.stdout.write('Suppression des utilisateurs de test existants...')
            User.objects.filter(email__in=[
                'marie.recruteur@cvanalyzer.com', 
                'jean.martin@email.com',
                'sophie.bernard@email.com'
            ]).delete()

        # Créer les utilisateurs de test
        users_data = [
            {
                'email': 'testrecruteur@test.test',
                'username': 'recruteur_marie',
                'first_name': 'Marie',
                'last_name': 'Dubois',
                'role': 'recruteur',
                'password': 'test',
                'is_staff': True,
                'is_superuser': False
            },
            {
                'email': 'testcandidat@test.test',
                'username': 'candidat_jean',
                'first_name': 'Jean',
                'last_name': 'Martin',
                'role': 'candidat',
                'password': 'test',
                'is_staff': False,
                'is_superuser': False
            },
            {
                'email': 'testcandidat2@test.test',
                'username': 'candidat_sophie',
                'first_name': 'Sophie',
                'last_name': 'Bernard',
                'role': 'candidat',
                'password': 'test',
                'is_staff': False,
                'is_superuser': False
            }
        ]

        created_count = 0
        for user_data in users_data:
            email = user_data['email']
            
            # Vérifier si l'utilisateur existe déjà
            if User.objects.filter(email=email).exists():
                self.stdout.write(
                    self.style.WARNING(f' Utilisateur {email} existe déjà')
                )
                continue

            password = user_data.pop('password')
            user = User.objects.create_user(**user_data)
            user.set_password(password)
            user.save()
            
            created_count += 1
            self.stdout.write(
                self.style.SUCCESS(f' Créé: {user.first_name} {user.last_name} ({user.role}) - {email}')
            )

        # Afficher le résumé
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS(f' {created_count} utilisateurs créés avec succès!'))
        self.stdout.write('\n COMPTES DE TEST CRÉÉS:')
        self.stdout.write('='*60)
        
        test_accounts = [
            ('ADMIN', 'admin@cvanalyzer.com', 'AdminTest123!'),
            ('RECRUTEUR', 'marie.recruteur@cvanalyzer.com', 'RecruteurTest123!'),
            ('CANDIDAT 1', 'jean.martin@email.com', 'CandidatTest123!'),
            ('CANDIDAT 2', 'sophie.bernard@email.com', 'CandidatTest123!'),
        ]
        
        for role, email, password in test_accounts:
            self.stdout.write(f'{role}:')
            self.stdout.write(f'  Email: {email}')
            self.stdout.write(f'  Mot de passe: {password}')
            self.stdout.write('')

        self.stdout.write(self.style.SUCCESS('Prêt pour les tests Postman!'))
