#!/usr/bin/env python3
"""패키지 구조, 한국어 메타데이터, 링크, 고정 서브모듈을 확인한다."""
import json
from pathlib import Path
import re
import subprocess
from meat_proxy import ROOT, compose


def main():
    skills=compose()
    assert len(skills)==9
    for name,data in skills.items():
        text=data['SKILL.md'].decode()
        assert re.search(r'^name: '+re.escape(name)+r'$',text,re.M),name
        assert re.search('[가-힣]',text),name
        assert '[TODO:' not in text,name
        assert data.get('agents/openai.yaml'),name
        for link in re.findall(r'\[[^\]]*\]\(([^)]+)\)',text):
            if '://' not in link and not link.startswith('#'):
                assert link.split('#')[0] in data,(name,link)
    for p in [ROOT/'README.md',ROOT/'THIRD_PARTY_NOTICES.md']:
        if not p.exists():raise ValueError(f'문서 누락: {p}')
        for link in re.findall(r'(?<!!)\[[^\]]*\]\(([^)]+)\)',p.read_text()):
            if '://' not in link and not link.startswith('#'):
                assert (p.parent/link.split('#')[0]).exists(),(p.name,link)
    locked=json.loads((ROOT/'modules.lock.json').read_text())
    for entry in locked:
        sha=subprocess.check_output(['git','-C',str(ROOT/entry['path']),'rev-parse','HEAD'],text=True).strip()
        assert sha==entry['commit'],entry['path']
    print(f'한국어 스킬 {len(skills)}개, 문서 링크, 서브모듈 {len(locked)}개 확인')


if __name__=='__main__':main()
