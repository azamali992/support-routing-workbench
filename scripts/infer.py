"""Independent stdlib inference for the exported browser model."""
import math,re,collections,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def predict(text,model=None):
    if not isinstance(text,str) or len(text)>2000:raise ValueError('Query must be text of at most 2000 characters')
    m=model or json.loads((ROOT/'public'/'model.json').read_text());tokens=re.findall(r'(?u)\b\w\w+\b',text.lower());terms=tokens+[tokens[i]+' '+tokens[i+1] for i in range(len(tokens)-1)];counts=collections.Counter(terms);features={m['vocabulary'][t]:(1+math.log(n))*m['idf'][m['vocabulary'][t]] for t,n in counts.items() if t in m['vocabulary']};norm=math.sqrt(sum(v*v for v in features.values()));scores=list(m['intercepts'])
    if norm:
        for feature,value in features.items():
            for c,weight in enumerate(m['weights'][feature]):scores[c]+=weight*value/norm
    ordered=sorted(range(len(scores)),key=lambda i:(-scores[i],i));gap=scores[ordered[0]]-scores[ordered[1]]
    return dict(prediction=m['classes'][ordered[0]],candidate=m['classes'][ordered[1]],margin=gap,scores=scores,review=not features or gap<m['threshold'],features=len(features))
