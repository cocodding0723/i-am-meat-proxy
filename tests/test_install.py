import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('meat', REPO / 'scripts/meat_proxy.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.home=Path(self.temp.name)
        self.roots=m.roots(self.home, environment=False)
    def tearDown(self): self.temp.cleanup()
    def install(self):
        changes=m.plan(REPO,self.roots,replace=True)
        return m.apply(changes,self.home/'backups')

    def test_install_eight_skills_and_repeat_without_changes(self):
        self.install()
        for root in self.roots.values():
            self.assertEqual(len(list((root/'skills').glob('*/SKILL.md'))),8)
        self.assertEqual(m.plan(REPO,self.roots),[])
        self.assertTrue(m.doctor(REPO,self.roots))

    def test_legacy_policy_replaced_and_unrelated_soul_preserved(self):
        codex=self.roots['codex'];codex.mkdir()
        (codex/'AGENTS.md').write_bytes((REPO/'modules/global-config/legacy/codex-AGENTS.md').read_bytes())
        hermes=self.roots['hermes'];hermes.mkdir()
        (hermes/'SOUL.md').write_text('기존 사용자 성격 설정\n')
        self.install()
        self.assertNotIn('Create a concise commit', (codex/'AGENTS.md').read_text())
        self.assertTrue((hermes/'SOUL.md').read_text().startswith('기존 사용자 성격 설정'))

    def test_only_duplicate_plugin_is_disabled(self):
        root=self.roots['claude'];root.mkdir()
        original={'model':'unchanged','permissions':{'defaultMode':'auto'},'enabledPlugins':{'i-have-adhd@i-have-adhd':True,'keep@plugin':True}}
        (root/'settings.json').write_text(json.dumps(original))
        self.install()
        after=json.loads((root/'settings.json').read_text())
        original['enabledPlugins']['i-have-adhd@i-have-adhd']=False
        self.assertEqual(original,after)

    def test_conflicting_existing_skill_blocks_all_writes(self):
        dst=self.roots['hermes']/'skills/create-pr';dst.mkdir(parents=True)
        (dst/'SKILL.md').write_text('user work')
        with self.assertRaises(ValueError):m.plan(REPO,self.roots)
        self.assertFalse(self.roots['codex'].exists())
        self.assertEqual((dst/'SKILL.md').read_text(),'user work')

    def test_unknown_legacy_rule_is_not_overwritten(self):
        root=self.roots['codex'];root.mkdir()
        (root/'AGENTS.md').write_text('# Global Git lifecycle\n사용자 수정\n')
        with self.assertRaises(ValueError):m.plan(REPO,self.roots,replace=True)
        self.assertIn('사용자 수정',(root/'AGENTS.md').read_text())

    def test_duplicate_frontmatter_name_is_rejected(self):
        dst=self.roots['hermes']/'skills/category/other-folder';dst.mkdir(parents=True)
        (dst/'SKILL.md').write_text('---\nname: create-pr\ndescription: duplicate\n---\n')
        with self.assertRaises(ValueError):m.plan(REPO,self.roots,replace=True)

    def test_changed_after_plan_is_preserved(self):
        changes=m.plan(REPO,self.roots,replace=True)
        first=changes[0]['path'];first.mkdir(parents=True)
        (first/'SKILL.md').write_text('another session')
        with self.assertRaises(ValueError):m.apply(changes,self.home/'backups')
        self.assertEqual((first/'SKILL.md').read_text(),'another session')

    def test_failure_restores_completed_targets(self):
        root=self.home/'sample';root.mkdir()
        old=root/'old';old.mkdir();(old/'x').write_text('before')
        new=root/'new.txt'
        changes=[{'path':old,'kind':'dir','before':{'x':b'before'},'after':{'x':b'after'},'owner':'test'},
                 {'path':new,'kind':'file','before':None,'after':b'new','owner':'test'}]
        real=m.shutil.move
        calls=0
        def fail_once(*args,**kwargs):
            nonlocal calls
            calls+=1
            if calls==2:raise OSError('simulated disk failure')
            return real(*args,**kwargs)
        with patch.object(m.shutil,'move',side_effect=fail_once):
            with self.assertRaises(OSError):m.apply(changes,self.home/'backups')
        self.assertEqual((old/'x').read_text(),'before');self.assertFalse(new.exists())

    def test_symlink_target_refused(self):
        root=self.roots['codex']/'skills';root.mkdir(parents=True)
        target=self.home/'outside';target.mkdir()
        (root/'create-pr').symlink_to(target,target_is_directory=True)
        with self.assertRaises(ValueError):m.plan(REPO,self.roots,replace=True)
        self.assertEqual(list(target.iterdir()),[])

    def test_rollback_preserves_a_concurrent_user_edit(self):
        a=self.home/'a';a.write_bytes(b'before')
        b=self.home/'b'
        changes=[{'path':a,'kind':'file','before':b'before','after':b'ours','owner':'test'},
                 {'path':b,'kind':'file','before':None,'after':b'new','owner':'test'}]
        real=m.shutil.move;calls=0
        def edit_and_fail(*args,**kwargs):
            nonlocal calls
            calls+=1
            if calls==2:
                a.write_bytes(b'user edit')
                raise OSError('disk failure')
            return real(*args,**kwargs)
        with patch.object(m.shutil,'move',side_effect=edit_and_fail):
            with self.assertRaises(ValueError):m.apply(changes,self.home/'backups')
        self.assertEqual(a.read_bytes(),b'user edit')
        self.assertEqual(next((self.home/'backups').glob('*/0')).read_bytes(),b'before')

    def test_profiles_are_explicit_and_scope_is_isolated(self):
        profile=self.roots['hermes']/'profiles/worker';profile.mkdir(parents=True)
        (profile/'config.yaml').write_text('model: test\n')
        basic=m.roots(self.home,environment=False)
        extended=m.roots(self.home,profiles=True,environment=False)
        self.assertNotIn('hermes:worker',basic);self.assertIn('hermes:worker',extended)
        m.apply(m.plan(REPO,extended,True),self.home/'backups')
        self.assertTrue((profile/'skills/create-pr/SKILL.md').exists())
        self.assertEqual((profile/'config.yaml').read_text(),'model: test\n')


if __name__=='__main__':unittest.main()
