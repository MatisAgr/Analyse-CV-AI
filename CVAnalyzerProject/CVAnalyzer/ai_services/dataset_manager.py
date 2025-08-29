"""
Service pour télécharger et préparer le dataset Kaggle des CV
"""
import os
import kagglehub
import pandas as pd
from pathlib import Path
from django.conf import settings

class DatasetManager:
    def __init__(self):
        self.dataset_path = None
        self.processed_data = None
    
    def download_kaggle_dataset(self):
        try:
            path = kagglehub.dataset_download("snehaanbhawal/resume-dataset")
            self.dataset_path = path
            print(f"Dataset téléchargé dans: {path}")
            return path
        except Exception as e:
            print(f"Erreur lors du téléchargement: {e}")
            return None
    
    def load_and_explore_dataset(self):
        if not self.dataset_path:
            print("Dataset non téléchargé. Téléchargement en cours...")
            self.download_kaggle_dataset()
        
        try:
            dataset_dir = Path(self.dataset_path)
            csv_files = list(dataset_dir.glob("*.csv"))
            
            if not csv_files:
                csv_files = list(dataset_dir.glob("**/*.csv"))
            
            if not csv_files:
                json_files = list(dataset_dir.glob("*.json"))
                txt_files = list(dataset_dir.glob("*.txt"))
                
                print(f"Fichiers trouvés dans {dataset_dir}:")
                for file in dataset_dir.iterdir():
                    print(f"  - {file.name}")
                
                if json_files:
                    print(f"Fichiers JSON trouvés: {json_files}")
                if txt_files:
                    print(f"Fichiers TXT trouvés: {txt_files}")
                    
                if txt_files:
                    txt_file = txt_files[0]
                    print(f"Chargement du fichier TXT: {txt_file}")
                    with open(txt_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    print(f"Contenu aperçu: {content[:500]}...")
                    return None
                
                print("Aucun fichier de données reconnu trouvé")
                return None
            
            csv_file = csv_files[0]
            print(f"Chargement du fichier: {csv_file}")
            
            df = pd.read_csv(csv_file)
            self.processed_data = df
            
            print(f"Dataset chargé avec {len(df)} lignes et {len(df.columns)} colonnes")
            print(f"Colonnes disponibles: {list(df.columns)}")
            print("\nPremières lignes du dataset:")
            print(df.head())
            
            return df
            
        except Exception as e:
            print(f"Erreur lors du chargement du dataset: {e}")
            return None
    
    def preprocess_dataset(self):
        if self.processed_data is None:
            self.load_and_explore_dataset()
        
        try:
            df = self.processed_data.copy()
            
            df = df.dropna()
            
            print("Structure du dataset après nettoyage:")
            print(df.info())
            
            processed_path = Path(settings.DATASETS_DIR) / "processed_resumes.csv"
            processed_path.parent.mkdir(exist_ok=True)
            df.to_csv(processed_path, index=False)
            
            print(f"Dataset préprocessé sauvegardé dans: {processed_path}")
            return df
            
        except Exception as e:
            print(f"Erreur lors du préprocessing: {e}")
            return None
    
    def get_sample_data(self, n=5):
        """
        Retourne un échantillon du dataset
        """
        if self.processed_data is None:
            self.load_and_explore_dataset()
        
        if self.processed_data is not None:
            return self.processed_data.head(n)
        return None

def initialize_dataset():
    """
    Fonction utilitaire pour initialiser le dataset
    """
    manager = DatasetManager()
    return manager.download_kaggle_dataset()

if __name__ == "__main__":
    manager = DatasetManager()
    manager.download_kaggle_dataset()
    manager.load_and_explore_dataset()
    manager.preprocess_dataset()
