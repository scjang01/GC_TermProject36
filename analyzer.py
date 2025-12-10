from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np
import re


class EmotionAnalyzer:
    def __init__(self, model_name="j-hartmann/emotion-english-distilroberta-base"):
        print("Loading Emotion Model...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.labels = ['anger', 'disgust', 'fear', 'joy', 'neutral', 'sadness', 'surprise']
        print("Model loaded successfully!")
        
    def predict(self, text:str) -> dict: # 감정 예측 테스트 함수
        inputs = self.tokenizer(text, return_tensors="pt")
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            
        probs = torch.nn.functional.softmax(outputs.logits, dim=1)[0]
        return {label: round(float(prob), 4) for label, prob in zip(self.labels, probs)}
    
    def predict_top1(self, text:str) -> tuple: # 감정 예측 top 1 테스트 함수
        result = self.predict(text)
        top_label = max(result, key=result.get)
        return top_label, result[top_label]
    
    def predict_batch(self, texts: list) -> list: # 여러 문장 및 각 문장 별 감정 예측 top1
        inputs = self.tokenizer(texts, return_tensors="pt", padding=True, truncation=True)

        with torch.no_grad():
            outputs = self.model(**inputs)

        probs = torch.nn.functional.softmax(outputs.logits, dim=1)

        results = []
        for i in range(len(texts)):
            prob = probs[i]
            prob_dict = {label: round(float(p), 4) for label, p in zip(self.labels, prob)}

            top_label = max(prob_dict, key=prob_dict.get)
            top_score = prob_dict[top_label]

            results.append({
                "probs": prob_dict,
                "top1": (top_label, top_score)
            })

        return results
    
    def analyze_paragraph(self, paragraph): # 문단 처리 감정 분석 함수
        sentences = split_into_sentences(paragraph)
        batch_results = self.predict_batch(sentences)
        n = len(batch_results)
        weights = [(i + 1) / n for i in range(n)]
        weighted_scores = {label: 0.0 for label in self.labels}

        for i, res in enumerate(batch_results):
            for label in self.labels:
                weighted_scores[label] += res["probs"][label] * weights[i]

        weighted_scores = {label: round(score, 4) for label, score in weighted_scores.items()}
        final_emotion = max(weighted_scores, key=weighted_scores.get)

        return {
            "sentences": sentences,
            "results": batch_results,
            "weights": weights,
            "weighted_scores": weighted_scores,
            "final_emotion": final_emotion,
        }
        
def split_into_sentences(text): # 문단을 문장 분리 함수
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s for s in sentences if s]