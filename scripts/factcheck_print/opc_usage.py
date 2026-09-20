"""Safe public usage totals; detailed response IDs/prompts stay in private Drive."""
import json
import os
from pathlib import Path


def summary(root: Path) -> dict:
    text_path=root/'resources/text-usage.json';image_path=root/'resources/image-usage.json'
    text=json.loads(text_path.read_text()) if text_path.exists() else {'entries':[],'estimated_usd':0}
    images=json.loads(image_path.read_text()) if image_path.exists() else []
    entries=text.get('entries',[])
    totals={k:sum(e.get(k,0) for e in entries) for k in ('input_tokens','output_tokens','cache_read_tokens','cache_creation_tokens','web_searches')}
    result={**totals,'text_responses':len(entries),'image_requests':len(images),
            'text_estimated_usd':text.get('estimated_usd',0),'image_estimated_usd':None if images else 0,
            'total_cost_complete':not images and not text.get('incomplete_cost',False),
            'note':'List-rate text estimate only, not invoice. Image amount unknown; prediction count retained.'}
    (root/'resources/usage-summary.json').write_text(json.dumps(result,indent=2))
    print('OPC_USAGE '+json.dumps(result))
    if os.getenv('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'],'a') as f:
            f.write('\n### OPC measured usage (not invoice)\n\n```json\n'+json.dumps(result,indent=2)+'\n```\n')
    return result
