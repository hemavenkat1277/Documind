import re
from dataclasses import dataclass

TOKEN_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_\-]*")

def _token_set(text:str) -> set[str]:
    return   {match.group(0) for match in TOKEN_RE.finditer(text)}:

@dataclass(frozen=True)
class RerankedCandidate:
    candidate:dict
    rerank_score:float



