import unittest,json,sys,hashlib,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from infer import predict
class ContractTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.m=json.loads((ROOT/'public'/'model.json').read_text());cls.report=json.loads((ROOT/'evaluation'/'results.json').read_text())
 def test_exported_model_matches_frozen_python_scores(self):
  for example in json.loads((ROOT/'evaluation'/'golden.json').read_text()):
   result=predict(example['text'],self.m);self.assertEqual(result['prediction'],example['predicted']);self.assertLess(max(abs(a-b) for a,b in zip(result['scores'],example['scores'])),1e-6)
 def test_ground_truth_is_not_in_browser_input(self):
  sample=json.loads((ROOT/'public'/'sample.json').read_text());self.assertEqual(len(sample),40)
  for row in sample:self.assertEqual(set(row),{'id','text'})
 def test_no_feature_input_abstains_and_bound_is_enforced(self):
  self.assertTrue(predict('!!!',self.m)['review'])
  with self.assertRaises(ValueError):predict('a'*2001,self.m)
 def test_corpus_split_and_reporting_denominators(self):
  self.assertEqual(self.report['official']['rows'],3080);self.assertEqual(self.report['clean']['rows'],3055);self.assertEqual(len(self.report['normalized_overlap_test_ids']),25)
  for name in ['official','clean']:
   r=self.report[name];self.assertEqual(r['accepted']+r['review'],r['rows']);self.assertLessEqual(r['wrong_accepted'],r['accepted']);self.assertAlmostEqual(r['coverage'],r['accepted']/r['rows'])
 def test_model_provenance_hash(self):self.assertEqual(hashlib.sha256((ROOT/'public'/'model.json').read_bytes()).hexdigest(),self.report['model_sha256'])
 def test_real_hard_case_in_sample(self):
  audit=json.loads((ROOT/'evaluation'/'sample-audit.json').read_text());self.assertTrue(any(r['review'] and r['truth']!=r['prediction'] for r in audit))
 def test_ood_is_separate_and_explicitly_synthetic(self):
  rows=json.loads((ROOT/'evaluation'/'ood-fixtures.json').read_text());self.assertTrue(all(r['synthetic'] for r in rows));self.assertEqual(len(rows),4)
if __name__=='__main__':unittest.main()
