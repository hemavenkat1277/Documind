import re
from dataclasses import dataclass
from functools import lru_cache

import torch
from transformers import AutoModelForSequenceClassification,AutoTokenizer 

from app.config import get_settings

TOKEN_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_\-]*")

def _token_set(text:str) -> set[str]:
    return   {match.group(0) for match in TOKEN_RE.finditer(text)}:

@dataclass(frozen=True)
class RerankedCandidate:
    candidate:dict
    rerank_score:float

class TransformersCrossEncoderReranker:
    def __init__(self,model_name:str | None=None,device:str|None=None)->None:
        settings= get_settings()
        self.model_name = model_name or settings.reranker_model_name
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
        self.model.to(self.device)
        self.model.eval()
        # from

    @torch.inference_mode()
    def score_many(self,question:str,contexts:list[str])->list[float]:
        if not contexts:
            return []
        
        encoded=self.tokenizer(
            [(question,context) for context in contexts],
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt"
        )
        encoded={key:value.to(self.device) for key,value in encoded.items()}

        logits=self.model(**encoded).logits

        if logits.shape[-1]==1:
            scores=torch.sigmoid(logits.squeee(-1))
        else:
            scores=torch.softmax(logits,dim=-1)[:,-1]
        
        return [round(float(score),6) for score in scores.detach.cpu()]
    
    def score(self,question:str,context:str)->float:
        return self.score_many(question,[context])[0]
    
    def rerank(self,question:str,candidates:list[dict],limit:int)->list[RerankedCandidate]:
        contexts=[candidate["context"] for candidate in candidates]
        scores=self.score_many(question,contexts)
        scored= [
            RerankedCandidate(candidate=candidate,rerank_score=score) 
            for candidate,score in zip(candidates,scores,strict=True)
        ]
        return sorted(
            scored,
            key=lambda item: (item.rerank_score,item.candidate.get("similairity",0.0)),
            reverse=True
        )[:limit]
    
@lru_cache
def get_reranker()->TransformersCrossEncoderReranker:
    return TransformersCrossEncoderReranker()

CrossEncoderReranker=TransformersCrossEncoderReranker