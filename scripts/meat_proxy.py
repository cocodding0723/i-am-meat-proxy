#!/usr/bin/env python3
"""한국어 스킬 조립·전역 설치·충돌 점검. 런타임 모델 설정은 덮어쓰지 않는다."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import tempfile

ROOT = Path(__file__).resolve().parents[1]
START = '<!-- i-am-meat-proxy:start -->'
END = '<!-- i-am-meat-proxy:end -->'


def files(root):
    if root.is_symlink(): raise ValueError(f'심볼릭 링크 대상 거부: {root}')
    result = {}
    for p in root.rglob('*'):
        if p.is_symlink(): raise ValueError(f'심볼릭 링크 거부: {p}')
        if p.is_file() and '__pycache__' not in p.parts:
            result[str(p.relative_to(root))] = p.read_bytes()
    return result


def compose(repo=ROOT):
    manifest = json.loads((repo / 'meat-proxy.json').read_text())
    result = {}
    for item in manifest['skills']:
        src = repo / item['source']
        if not (src / 'SKILL.md').is_file(): raise ValueError(f'서브모듈/스킬 누락: {src}; git submodule update --init --recursive 필요')
        data = files(src)
        if item['overlay']:
            original = data['SKILL.md']
            data.update(files(repo / item['overlay']))
            if item['name'] in ('writing-humanizer', 'i-have-adhd'):
                data['references/upstream-SKILL.md'] = original
        if item['name'] == 'i-have-adhd':
            data['LICENSE'] = (repo / 'modules/i-have-adhd-compression/LICENSE').read_bytes()
            # Gemini 전용 어댑터는 이 패키지의 세 도구 설치 범위 밖이다.
            data.pop('agents/gemini.toml', None)
        result[item['name']] = data
    return result


def roots(home, agent='all', profiles=False, environment=True):
    env = os.environ if environment else {}
    codex = Path(env.get('CODEX_HOME', str(home / '.codex'))).expanduser()
    claude = Path(env.get('CLAUDE_CONFIG_DIR', str(home / '.claude'))).expanduser()
    hermes = Path(env.get('HERMES_HOME', str(home / '.hermes'))).expanduser()
    all_roots = {'codex': codex, 'claude': claude, 'hermes': hermes}
    selected = all_roots if agent == 'all' else {agent: all_roots[agent]}
    if profiles and agent in ('all', 'hermes'):
        for p in sorted((hermes / 'profiles').glob('*')):
            if p.is_dir() and (p / 'config.yaml').is_file(): selected['hermes:' + p.name] = p
    return selected


def managed_text(old, base, policy, legacy=None):
    if old.count(START) != old.count(END) or old.count(START) > 1:
        raise ValueError('관리 블록 손상: 원문을 보존하고 중단')
    block = f'''{START}
## i-am-meat-proxy

공통 규칙: [{policy.name}]({policy}). 해당 작업에서 필요한 스킬만 읽는다.
코드 변경 마무리에는 `review-before-commit`: 변경·검증 결과를 제시하고, 이번 범위에 대한 명시적 승인 뒤 stage·commit·push한다. 이미 받은 게시 승인은 재사용한다.
PR은 `create-pr`, Issue는 `manage-issues`. 초안 요청은 게시 승인이 아니다.
문서 구조·문장 편집·표현 검사는 각 글쓰기 스킬을 필요할 때 선택한다. 한국어는 답부터 짧고 정확하게 쓴다.
`i-have-adhd`는 명시적으로 호출할 때만 적용한다. 스킬 설치 위치: `{base / 'skills'}`.
{END}'''
    if legacy and old.strip() == legacy.strip(): old = ''
    elif '# Global Git lifecycle' in old and START not in old:
        raise ValueError('알려진 원본과 다른 Git 규칙: 자동 교체하지 않음')
    if START in old:
        return re.sub(re.escape(START) + r'.*?' + re.escape(END), lambda _: block, old, flags=re.S)
    return old.rstrip() + ('\n\n' if old.strip() else '') + block + '\n'


def current(path, kind):
    if path.is_symlink(): raise ValueError(f'심볼릭 링크 대상 거부: {path}')
    if not path.exists(): return None
    if kind == 'dir':
        if not path.is_dir(): raise ValueError(f'디렉터리 아님: {path}')
        return files(path)
    if not path.is_file(): raise ValueError(f'파일 아님: {path}')
    return path.read_bytes()


def plan(repo, target_roots, replace=False):
    skills = compose(repo)
    config = repo / 'modules/global-config'
    policy = (config / 'policy/WORKFLOW.md').read_bytes()
    legacy = (config / 'legacy/codex-AGENTS.md').read_text()
    changes = []
    def add(path, kind, desired, owner):
        before = current(path, kind)
        if before != desired:
            if before is not None and not replace: raise ValueError(f'기존 내용 다름: {path}; diff 확인 후 --replace 사용')
            changes.append({'path': path, 'kind': kind, 'before': before, 'after': desired, 'owner': owner})
    for owner, base in target_roots.items():
        skill_root = base / 'skills'
        for name, data in skills.items():
            if skill_root.exists():
                for p in skill_root.rglob('SKILL.md'):
                    text = p.read_text(errors='replace')
                    match = re.search(r'^name:\s*[\'"]?([^\n\'\"]+)', text, re.M)
                    if match and match.group(1).strip() == name and p.parent != skill_root / name:
                        raise ValueError(f'중복 스킬: {p}')
            add(skill_root / name, 'dir', data, owner)
        policy_path = base / 'meat-proxy/WORKFLOW.md'
        add(policy_path, 'file', policy, owner)
        instruction = base / ('AGENTS.md' if owner == 'codex' else 'CLAUDE.md' if owner == 'claude' else 'SOUL.md')
        old = current(instruction, 'file') or b''
        desired = managed_text(old.decode(), base, policy_path, legacy if owner == 'codex' else None).encode()
        add(instruction, 'file', desired, owner)
        if owner == 'claude':
            settings = base / 'settings.json'
            if settings.exists():
                data = json.loads(settings.read_text())
                enabled = data.get('enabledPlugins', {})
                if enabled.get('i-have-adhd@i-have-adhd'):
                    enabled['i-have-adhd@i-have-adhd'] = False
                    add(settings, 'file', (json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode(), owner)
        if owner == 'codex':
            hook = base / 'hooks/git_session_start.py'
            if hook.exists():
                old = hook.read_text()
                phrase = 'commit only task-owned files, push the current branch, and verify the remote SHA.'
                if phrase in old:
                    new = old.replace(phrase, 'present task-owned changes for user review; stage, commit and push only with explicit authorization for this scope, then verify the remote SHA.')
                    add(hook, 'file', new.encode(), owner)
    # 같은 경로에 두 번 적용하지 않는다.
    targets = [str(c['path'].absolute()) for c in changes]
    if len(targets) != len(set(targets)): raise ValueError('설치 대상 경로 중복')
    return changes


def write_content(path, kind, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    if kind == 'dir':
        path.mkdir()
        for rel, content in data.items():
            target = path / rel; target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
    else:
        path.write_bytes(data)


def apply(changes, backup_root):
    # 모든 경로를 실제 변경 직전에 재확인한다. 다른 세션의 수정을 덮어쓰지 않는다.
    for c in changes:
        if current(c['path'], c['kind']) != c['before']: raise ValueError(f'계획 후 변경 감지: {c["path"]}')
    if not changes: return None
    backup = backup_root / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    backup.mkdir(parents=True, mode=0o700)
    receipt = []
    done = []
    try:
        for index, c in enumerate(changes):
            path = c['path']; saved = backup / str(index)
            if current(path, c['kind']) != c['before']: raise ValueError(f'동시 변경 감지: {path}')
            if c['before'] is not None:
                if c['kind'] == 'dir': shutil.copytree(path, saved)
                else: shutil.copy2(path, saved)
            mode = path.stat().st_mode & 0o777 if path.exists() else (0o755 if c['kind'] == 'dir' else 0o644)
            with tempfile.TemporaryDirectory(prefix='.meat-proxy-', dir=path.parent if path.parent.exists() else backup) as tmp:
                prepared = Path(tmp) / 'prepared'
                write_content(prepared, c['kind'], c['after'])
                if path.exists():
                    if c['kind'] == 'dir': shutil.rmtree(path)
                    else: path.unlink()
                done.append((c, saved))
                path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(prepared), str(path))
                path.chmod(mode)
            if current(path, c['kind']) != c['after']: raise ValueError(f'설치 검증 실패: {path}')
            receipt.append({'path': str(path), 'kind': c['kind'], 'backup': str(saved) if c['before'] is not None else None})
    except Exception as failure:
        conflicts = []
        for c, saved in reversed(done):
            path = c['path']
            # 복원 중에도 다른 세션이 만든 새 변경을 덮어쓰지 않는다.
            if current(path, c['kind']) not in (None, c['after']):
                conflicts.append(str(path))
                continue
            if path.exists():
                if path.is_dir(): shutil.rmtree(path)
                else: path.unlink()
            if saved.exists():
                if saved.is_dir(): shutil.copytree(saved, path)
                else: shutil.copy2(saved, path)
        if conflicts:
            raise ValueError(f'복원 중 동시 변경 보존: {conflicts}; 원본 백업: {backup}') from failure
        raise
    (backup / 'receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    return backup


def doctor(repo, target_roots):
    issues = []
    try:
        for change in plan(repo, target_roots, replace=True):
            issues.append(f'{change["owner"]}: 설치본 차이 {change["path"].name}')
    except ValueError as exc:
        issues.append(str(exc))
    desired = compose(repo)
    for owner, base in target_roots.items():
        for name, data in desired.items():
            if current(base / 'skills' / name, 'dir') != data: issues.append(f'{owner}: 누락/차이 {name}')
        instruction = base / ('AGENTS.md' if owner == 'codex' else 'CLAUDE.md' if owner == 'claude' else 'SOUL.md')
        text = instruction.read_text() if instruction.exists() else ''
        if text.count(START) != 1 or text.count(END) != 1: issues.append(f'{owner}: 공통 규칙 블록 누락/중복')
        if 'Create a concise commit describing the completed task' in text: issues.append(f'{owner}: 자동 커밋 규칙 충돌')
        if owner == 'claude' and (base / 'settings.json').exists():
            d = json.loads((base / 'settings.json').read_text())
            if d.get('enabledPlugins', {}).get('i-have-adhd@i-have-adhd'): issues.append('claude: i-have-adhd 플러그인 중복')
    print(json.dumps({'roots': list(target_roots), 'skills': len(desired), 'issues': issues}, ensure_ascii=False, indent=2))
    return not issues


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['install', 'doctor', 'build'])
    parser.add_argument('--home', type=Path, help='격리된 테스트 홈. 환경변수 경로를 무시한다.')
    parser.add_argument('--agent', choices=['all', 'codex', 'claude', 'hermes'], default='all')
    parser.add_argument('--hermes-profiles', action='store_true')
    parser.add_argument('--replace', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    home = (args.home or Path.home()).expanduser().absolute()
    try:
        if args.command == 'build':
            if not args.output: raise ValueError('build는 --output 필요')
            if args.output.exists(): raise ValueError('기존 출력 폴더 덮어쓰기 거부')
            for name, data in compose().items(): write_content(args.output / name, 'dir', data)
            return
        targets = roots(home, args.agent, args.hermes_profiles, args.home is None)
        if args.command == 'doctor': raise SystemExit(0 if doctor(ROOT, targets) else 1)
        changes = plan(ROOT, targets, args.replace)
        for c in changes: print(f'{c["owner"]}: {"백업·교체" if c["before"] is not None else "신규"}: {c["path"]}')
        if not args.dry_run:
            receipt = apply(changes, home / '.local/share/i-am-meat-proxy/backups')
            print(f'설치 완료: {len(changes)}개 대상 변경. 백업: {receipt or "변경 없음"}')
    except (ValueError, OSError) as exc: parser.exit(1, f'중단: {exc}\n')


if __name__ == '__main__': main()
