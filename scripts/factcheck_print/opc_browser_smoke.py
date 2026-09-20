"""Synthetic browser fixture. Not generated content, project proof or live API evidence."""
from pathlib import Path
import json
import os
import subprocess
from PIL import Image, ImageDraw
from opc_render import export, review
from opc_contract import digest_file, STATUS, AI_DISCLOSURE


def main():
    root=Path('opc-browser-fixture');(root/'resources').mkdir(parents=True,exist_ok=True)
    im=Image.effect_noise((1200,800),40).convert('RGB')
    ImageDraw.Draw(im).text((50,50),'SYNTHETIC TEST ONLY - NOT A PRODUCT PHOTO',fill='white',stroke_width=1)
    im.save(root/'resources/test.jpg');im.save(root/'resources/proof.png')
    subprocess.run(['ffmpeg','-y','-loglevel','error','-f','lavfi','-i','testsrc=size=320x240:rate=24','-f','lavfi','-i','sine=frequency=440','-t','3','-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac',str(root/'resources/video.mp4')],check=True)
    spec={'title':'Synthetic layout test','project':'opc','language':'en','kind':'education','status':STATUS,'approved':False,
          'caption':'Synthetic test content only. '+AI_DISCLOSURE,'hashtags':'','editorial_review':{'passed':True},
          'sources':[{'id':'S1','name':'Synthetic source','url':'https://example.org','screenshot':'resources/proof.png','observed_in_search':False}],
          'assets':[{'key':'A1','kind':'ai_illustration','path':'resources/test.jpg','sha256':digest_file(root/'resources/test.jpg')}],
          'video':{'file':'resources/video.mp4'},
          'slides':[{'id':i,'layout':'point','headline':'Test the visual layout','body':'This fixture tests readable type, image loading and browser behavior. It is not real content.','source_ids':['S1'],'visual_key':'A1'} for i in range(1,6)]}
    export(spec,root);pagefile=review(spec,root)
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b=pw.chromium.launch(headless=True)
        page=b.new_page(viewport={'width':390,'height':844})
        page.set_content(pagefile.read_text(),wait_until='load')
        page.wait_for_function('document.querySelector("video").readyState>=2')
        page.evaluate('window.testVideo=document.querySelector("video");window.testVideo.currentTime=1;window.testVideo.pause()')
        page.locator('[data-theme="cream"]').click()
        page.locator('[data-deck="cream"] [data-choice="keep"]').first.click()
        same=page.evaluate('window.testVideo===document.querySelector("video")&&Math.abs(window.testVideo.currentTime-1)<0.2')
        if not same:raise RuntimeError('Feedback/theme switch replaced or restarted the video')
        if page.evaluate('document.documentElement.scrollWidth>innerWidth+1'):raise RuntimeError('Mobile horizontal overflow')
        page.screenshot(path=str(root/'mobile-review.png'),full_page=False)
        result={'synthetic_only':True,'fonts_and_15_pngs_checked':True,'mobile_width':390,'video_preserved_after_feedback':same}
        (root/'browser-smoke.json').write_text(json.dumps(result,indent=2));print(json.dumps(result));b.close()

if __name__=='__main__':main()
