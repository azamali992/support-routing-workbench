"""Unattended UI happy path, genuine abstention, confirmation and CSV export."""
from pathlib import Path
import argparse,json,threading,http.server,functools,time
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--url');p.add_argument('--output',type=Path,default=ROOT/'capture');p.add_argument('--parity-only',action='store_true');a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
 server=None
 if not a.url:
  server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(ROOT)));threading.Thread(target=server.serve_forever,daemon=True).start();a.url=f'http://127.0.0.1:{server.server_port}/'
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True);page=browser.new_page(viewport={'width':1920,'height':1080},device_scale_factor=1,accept_downloads=True);errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  tick=time.perf_counter();page.goto(a.url,wait_until='networkidle');page.wait_for_function('window.QueueProof && window.QueueProof.ready');cold=time.perf_counter()-tick
  golden=json.loads((ROOT/'evaluation'/'golden.json').read_text());parity=[]
  for item in golden:
   actual=page.evaluate('(text)=>window.QueueProof.infer(text)',item['text']);delta=max(abs(x-y) for x,y in zip(actual['scores'],item['scores']));assert delta<1e-6,(delta,item['text']);assert actual['prediction']==item['predicted'];parity.append(delta)
  if not a.parity_only:
   page.get_by_role('button',name='Reset workspace').click();sample=json.loads((ROOT/'public'/'sample.json').read_text());page.locator('#messages').fill('\n'.join(r['text'] for r in sample[:5]));page.screenshot(path=str(a.output/'01-input.png'))
   page.get_by_role('button',name='Load real message batch').click();assert page.locator('#count-all').inner_text()=='40';page.screenshot(path=str(a.output/'02-result.png'))
   page.get_by_role('button',name='Needs review',exact=True).click();page.locator('tr[data-id]').first.click();page.locator('#detail').scroll_into_view_if_needed();assert 'below' in page.locator('#review-reason').inner_text();page.screenshot(path=str(a.output/'03-hard-case.png'))
   before=int(page.locator('#count-review').inner_text());page.locator('#human-intent').select_option('card_arrival');page.get_by_role('button',name='Confirm selected intent').click();assert int(page.locator('#count-review').inner_text())==before-1;assert 'card arrival' in page.locator('#review-reason').inner_text();page.screenshot(path=str(a.output/'04-confirmed.png'))
   with page.expect_download() as event:page.get_by_role('button',name='Export accepted suggestions').click()
   event.value.save_as(a.output/'queueproof-suggestions.csv');assert (a.output/'queueproof-suggestions.csv').stat().st_size>100;exported=(a.output/'queueproof-suggestions.csv').read_text();assert '"banking77-test-2"' in exported;assert '"card_arrival","card arrival","human_confirmed"' in exported;page.screenshot(path=str(a.output/'05-export.png'))
   page.get_by_role('button',name='Reset workspace').click();assert page.locator('#count-all').inner_text()=='0'
  assert not errors,errors
  result={'url':a.url,'viewport':[1920,1080],'cold_load_seconds':cold,'browser_python_max_score_delta':max(parity),'golden_queries':len(parity),'page_errors':errors,'happy_path_review_confirm_export_reset':'passed' if not a.parity_only else 'not run','captured_date':'2026-10-03'};(a.output/'capture-report.json').write_text(json.dumps(result,indent=2));print(json.dumps(result));browser.close()
 if server:server.shutdown()
if __name__=='__main__':main()
