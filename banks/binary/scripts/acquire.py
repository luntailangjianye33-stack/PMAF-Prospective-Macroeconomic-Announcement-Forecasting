import json, sys
from concurrent.futures import ThreadPoolExecutor
from fetch import fetch, ROOT, RAW
sys.stdout.reconfigure(encoding='utf-8')
def run(item):
    code, filters = item
    name = f'history_{code}.json'
    if not (RAW/name).exists():
        fetch(name, f'https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/{code}',
              {'lang':'en','geo':['EU27_2020','EA21'], 'sinceTimePeriod':'2024-01', **filters})
    j=json.loads((RAW/name).read_text(encoding='utf-8'))
    print(code, j.get('size'), list(j.get('dimension',{}).get('time',{}).get('category',{}).get('index',{}))[-4:], len(j.get('value',{})), flush=True)
with ThreadPoolExecutor(max_workers=3) as pool:
    list(pool.map(run,json.loads((ROOT/'series.json').read_text(encoding='utf-8')).items()))
