import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoModel, Trainer, TrainingArguments
from sklearn.metrics import f1_score, precision_score, recall_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import numpy as np
import pandas as pd
from torch.utils.data import Dataset, DataLoader
import json

class CVDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_length=512):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(self.labels[idx], dtype=torch.long)
        }

class CVClassifier(nn.Module):
    def __init__(self, model_name='distilbert-base-uncased', num_classes=10):
        super(CVClassifier, self).__init__()
        self.bert = AutoModel.from_pretrained(model_name)
        self.dropout = nn.Dropout(0.3)
        self.classifier = nn.Linear(self.bert.config.hidden_size, num_classes)
    
    def forward(self, input_ids, attention_mask):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        pooled_output = outputs.pooler_output
        output = self.dropout(pooled_output)
        return self.classifier(output)

class AIModelTrainer:
    def __init__(self, model_name='distilbert-base-uncased'):
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = None
        self.label_encoder = LabelEncoder()
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    def prepare_data(self, df):
        if 'Resume_str' not in df.columns or 'Category' not in df.columns:
            return {"success": False, "error": "Colonnes manquantes"}
        
        texts = df['Resume_str'].tolist()
        labels = self.label_encoder.fit_transform(df['Category'])
        
        X_train, X_test, y_train, y_test = train_test_split(
            texts, labels, test_size=0.2, random_state=42, stratify=labels
        )
        
        return {
            "success": True,
            "X_train": X_train,
            "X_test": X_test,
            "y_train": y_train,
            "y_test": y_test,
            "num_classes": len(self.label_encoder.classes_),
            "classes": self.label_encoder.classes_.tolist()
        }
    
    def train_model(self, X_train, y_train, X_val, y_val, epochs=3, batch_size=16):
        num_classes = len(np.unique(y_train))
        self.model = CVClassifier(self.model_name, num_classes).to(self.device)
        
        train_dataset = CVDataset(X_train, y_train, self.tokenizer)
        val_dataset = CVDataset(X_val, y_val, self.tokenizer)
        
        optimizer = torch.optim.AdamW(self.model.parameters(), lr=2e-5)
        criterion = nn.CrossEntropyLoss()
        
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=batch_size)
        
        self.model.train()
        for epoch in range(epochs):
            total_loss = 0
            for batch in train_loader:
                optimizer.zero_grad()
                
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['labels'].to(self.device)
                
                outputs = self.model(input_ids, attention_mask)
                loss = criterion(outputs, labels)
                
                loss.backward()
                optimizer.step()
                total_loss += loss.item()
            
            avg_loss = total_loss / len(train_loader)
            val_metrics = self.evaluate(val_loader)
            
            print(f"Epoch {epoch+1}: Loss={avg_loss:.4f}, Val F1={val_metrics['f1']:.4f}")
        
        return {"success": True, "final_metrics": val_metrics}
    
    def evaluate(self, data_loader):
        self.model.eval()
        predictions = []
        true_labels = []
        
        with torch.no_grad():
            for batch in data_loader:
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['labels'].to(self.device)
                
                outputs = self.model(input_ids, attention_mask)
                _, preds = torch.max(outputs, dim=1)
                
                predictions.extend(preds.cpu().tolist())
                true_labels.extend(labels.cpu().tolist())
        
        return {
            "f1": f1_score(true_labels, predictions, average='weighted'),
            "precision": precision_score(true_labels, predictions, average='weighted'),
            "recall": recall_score(true_labels, predictions, average='weighted'),
            "classification_report": classification_report(true_labels, predictions, output_dict=True)
        }
    
    def predict(self, text):
        self.model.eval()
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=512,
            return_tensors='pt'
        )
        
        with torch.no_grad():
            input_ids = encoding['input_ids'].to(self.device)
            attention_mask = encoding['attention_mask'].to(self.device)
            
            outputs = self.model(input_ids, attention_mask)
            probabilities = torch.nn.functional.softmax(outputs, dim=-1)
            
            predicted_class_id = outputs.argmax().item()
            confidence = probabilities[0][predicted_class_id].item()
            
            predicted_class = self.label_encoder.inverse_transform([predicted_class_id])[0]
        
        return {
            "predicted_category": predicted_class,
            "confidence": confidence,
            "all_probabilities": probabilities[0].cpu().tolist()
        }
    
    def score_cv_for_job(self, cv_text, job_description, target_category=None):
        cv_prediction = self.predict(cv_text)
        
        if target_category and target_category in self.label_encoder.classes_:
            target_encoded = self.label_encoder.transform([target_category])[0]
            cv_encoding = self.tokenizer(cv_text, truncation=True, padding=True, return_tensors='pt')
            job_encoding = self.tokenizer(job_description, truncation=True, padding=True, return_tensors='pt')
            
            with torch.no_grad():
                cv_embedding = self.model.bert(**cv_encoding).pooler_output
                job_embedding = self.model.bert(**job_encoding).pooler_output
                
                similarity = torch.cosine_similarity(cv_embedding, job_embedding, dim=1).item()
                category_match = cv_prediction["predicted_category"] == target_category
                
                final_score = (similarity * 0.6 + cv_prediction["confidence"] * 0.4) * (1.2 if category_match else 0.8)
        else:
            final_score = cv_prediction["confidence"]
        
        return {
            "overall_score": min(final_score * 100, 100),
            "predicted_category": cv_prediction["predicted_category"],
            "confidence": cv_prediction["confidence"],
            "recommendation": "Excellent candidat" if final_score > 0.8 else "Candidat potentiel" if final_score > 0.6 else "À revoir"
        }
