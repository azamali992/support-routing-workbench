"""Training-only selection; official test is evaluated after freezing artifacts."""
from pathlib import Path
import csv,json,re,hashlib,time,collections,sys
ROOT=Path(__file__).resolve().parents[1]
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.metrics import accuracy_score,f1_score,classification_report
SEED=42
def rows(file):
    with file.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
def norm(text):return re.sub(r'\W+',' ',text.lower()).strip()
def words(text):return re.findall(r'(?u)\b\w\w+\b',text.lower())
def summarize(y,pred,gaps,threshold,known):
    accepted=(gaps>=threshold)&(known>0);wrong=(pred!=y)&accepted
    return dict(rows=len(y),accuracy=float(accuracy_score(y,pred)),macro_f1=float(f1_score(y,pred,average='macro')),accepted=int(accepted.sum()),wrong_accepted=int(wrong.sum()),accepted_error_rate=float(wrong.sum()/max(accepted.sum(),1)),review=int((~accepted).sum()),coverage=float(accepted.mean()),per_class=classification_report(y,pred,output_dict=True,zero_division=0))
def main():
    raw=ROOT/'data'/'raw';train=rows(raw/'train.csv');test=rows(raw/'test.csv');classes=sorted({r['category'] for r in train});classid={s:i for i,s in enumerate(classes)}
    texts=np.array([r['text'] for r in train]);ys=np.array([classid[r['category']] for r in train]);groups=np.array([norm(s) for s in texts])
    development,validation=next(StratifiedGroupKFold(n_splits=5,shuffle=True,random_state=SEED).split(texts,ys,groups));assert not(set(groups[development])&set(groups[validation]))
    vectorizer=TfidfVectorizer(max_features=8000,ngram_range=(1,2),sublinear_tf=True);xd=vectorizer.fit_transform(texts[development]);xv=vectorizer.transform(texts[validation])
    model=LinearSVC(C=1.0,random_state=SEED,dual='auto',max_iter=5000).fit(xd,ys[development]);vs=model.decision_function(xv);vp=vs.argmax(axis=1);vg=np.sort(vs,axis=1)[:,-1]-np.sort(vs,axis=1)[:,-2]
    candidates=sorted(set(float(x) for x in np.quantile(vg,np.linspace(0,1,101))))
    eligible=[t for t in candidates if (vg>=t).sum()>=100 and float((vp[vg>=t]==ys[validation][vg>=t]).mean())>=.95]
    threshold=min(eligible) if eligible else max(candidates)+1
    # Training-only keyword baseline: five distinctive unigram counts per intent.
    counters=[collections.Counter() for _ in classes];overall=collections.Counter()
    for i in development:
        w=set(words(texts[i]));counters[ys[i]].update(w);overall.update(w)
    baseline=[]
    for c in counters:
        ranked=sorted(((w,n/overall[w]) for w,n in c.items() if n>=3 and len(w)>2),key=lambda v:(-v[1],v[0]))[:5];baseline.append(dict(ranked))
    testtexts=[r['text'] for r in test];ty=np.array([classid[r['category']] for r in test]);xt=vectorizer.transform(testtexts);scores=model.decision_function(xt);pred=scores.argmax(axis=1);sorted_s=np.sort(scores,axis=1);gaps=sorted_s[:,-1]-sorted_s[:,-2];known=np.asarray((xt!=0).sum(axis=1)).ravel()
    def bp(text):
        ws=set(words(text));ss=[sum(weight for w,weight in rule.items() if w in ws) for rule in baseline];return int(np.argmax(ss))
    bpred=np.array([bp(t) for t in testtexts]);trainnorm=set(groups);overlap=[i for i,t in enumerate(testtexts) if norm(t) in trainnorm];clean=np.array([i for i in range(len(test)) if i not in overlap])
    latency=[]
    for t in testtexts[:200]:
        tick=time.perf_counter();model.decision_function(vectorizer.transform([t]));latency.append((time.perf_counter()-tick)*1000)
    report=dict(seed=SEED,training_rows=len(train),development_rows=len(development),validation_rows=len(validation),classes=len(classes),vocabulary=len(vectorizer.vocabulary_),threshold=threshold,threshold_selection='Minimum validation gap achieving >=95% correct accepted suggestions and >=100 accepted validation rows; 101 quantile candidates; no test tuning',validation=summarize(ys[validation],vp,vg,threshold,np.asarray((xv!=0).sum(axis=1)).ravel()),official=summarize(ty,pred,gaps,threshold,known),clean=summarize(ty[clean],pred[clean],gaps[clean],threshold,known[clean]),baseline=dict(official=dict(accuracy=float(accuracy_score(ty,bpred)),macro_f1=float(f1_score(ty,bpred,average='macro'))),clean=dict(accuracy=float(accuracy_score(ty[clean],bpred[clean])),macro_f1=float(f1_score(ty[clean],bpred[clean],average='macro')))),normalized_overlap_test_ids=overlap,latency=dict(unit='milliseconds',implementation='Python sklearn one-query vectorization + decision function; first 200 official test queries, warm process',p50=float(np.percentile(latency,50)),p95=float(np.percentile(latency,95))),limitations=['BANKING77 banking-domain benchmark only','Uncalibrated linear decision margins are not probabilities','Closed-set margin cannot certify out-of-domain detection','Queue names are this demo design, not a real bank taxonomy'])
    public=ROOT/'public';public.mkdir(exist_ok=True);evaluation=ROOT/'evaluation';evaluation.mkdir(exist_ok=True)
    artifact=dict(classes=classes,vocabulary={k:int(v) for k,v in vectorizer.vocabulary_.items()},idf=np.round(vectorizer.idf_,9).tolist(),weights=np.round(model.coef_.T,9).tolist(),intercepts=np.round(model.intercept_,9).tolist(),threshold=threshold,baseline=baseline,tokenizer='lowercase Unicode word tokens length >=2; word unigrams and adjacent bigrams; sublinear tf, smooth idf, L2 norm')
    modelpath=public/'model.json';modelpath.write_text(json.dumps(artifact,separators=(',',':')),encoding='utf-8');report['model_sha256']=hashlib.sha256(modelpath.read_bytes()).hexdigest()
    (evaluation/'results.json').write_text(json.dumps(report,indent=2)+'\n');(public/'metrics.json').write_text(json.dumps({k:v for k,v in report.items() if k not in ('validation',)} ,separators=(',',':')))
    (evaluation/'split.json').write_text(json.dumps(dict(development_ids=development.tolist(),validation_ids=validation.tolist(),normalized_overlap_test_ids=overlap),indent=2))
    # Audit-only labels never loaded by app. Display sample is explicitly curated, not used for metrics.
    reviews=[int(i) for i in clean if gaps[i]<threshold];accepted_correct=[int(i) for i in clean if gaps[i]>=threshold and pred[i]==ty[i]];wrong=[int(i) for i in clean if pred[i]!=ty[i] and gaps[i]<threshold]
    chosen=list(dict.fromkeys(wrong[:3]+reviews[:8]+accepted_correct[:40]))[:40]
    (public/'sample.json').write_text(json.dumps([dict(id=f'banking77-test-{i}',text=testtexts[i]) for i in chosen],indent=2),encoding='utf-8')
    (evaluation/'sample-audit.json').write_text(json.dumps([dict(id=f'banking77-test-{i}',truth=classes[ty[i]],prediction=classes[pred[i]],margin=float(gaps[i]),review=bool(gaps[i]<threshold)) for i in chosen],indent=2))
    (evaluation/'golden.json').write_text(json.dumps([dict(text=testtexts[i],scores=scores[i].tolist(),predicted=classes[pred[i]],margin=float(gaps[i])) for i in chosen[:12]],indent=2))
    # OOD fixtures are authored behavioral tests, separated from real-data metrics.
    ood=['What is the weather in Karachi?','Please book a dentist appointment tomorrow','How do I bake a birthday cake?','Cardboard packaging delivery was delayed']
    os=model.decision_function(vectorizer.transform(ood));(evaluation/'ood-fixtures.json').write_text(json.dumps([dict(text=t,synthetic=True,prediction=classes[int(s.argmax())],margin=float(np.sort(s)[-1]-np.sort(s)[-2]),would_accept=bool(np.sort(s)[-1]-np.sort(s)[-2]>=threshold)) for t,s in zip(ood,os)],indent=2))
    print(json.dumps({k:report[k] for k in ('training_rows','development_rows','validation_rows','vocabulary','threshold')}));print('Clean accuracy',report['clean']['accuracy'],'baseline',report['baseline']['clean']['accuracy'],'accepted',report['clean']['accepted'],'wrong',report['clean']['wrong_accepted'])
if __name__=='__main__':main()
