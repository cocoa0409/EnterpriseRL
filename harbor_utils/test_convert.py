"""Regression checks for the packed world's file layout and direct tool merging."""

import ast
import importlib.util
import tempfile
import tomllib
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from erlbench.kb import Document, KnowledgeBase
from erlbench.loader import load_tool_specs
from erlbench.tools import collect_specs
from harbor_utils.convert import (
    ConversionError, _write, document_filename, pack_task_tools, packed_documents,
    render_task_toml, rt, task_annotations,
)


class ConversionLayoutTests(unittest.TestCase):
    def test_direct_merge_preserves_tool_code_and_deduplicates_imports(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            specs = []
            original_functions = []
            for index, value in enumerate((7, 19)):
                path = root / 'tasks' / str(index) / 'task_tools.py'
                path.parent.mkdir(parents=True)
                source = f'''from __future__ import annotations
from erlbench import tool
from math import floor

VALUE_{index} = {value}
calls_{index} = 0
text_{index} = "quoted 'value' and \\n literal \\\\ path"

def helper_{index}():
    return VALUE_{index} + floor(1.5)

@tool(owner="agent", rw="read")
def read_{index}(ctx, amount: int = 1) -> str:
    """Read a value using helpers and state."""
    global calls_{index}
    calls_{index} += 1
    return str((helper_{index}() + amount, calls_{index}, text_{index}))
'''
                original_functions.extend(ast.dump(n) for n in ast.parse(source).body
                                          if isinstance(n, ast.FunctionDef))
                path.write_text(source)
                specs.extend(load_tool_specs(str(path), 'task'))
            scenario = SimpleNamespace(root=str(root), name='merge', specs=specs)
            bundle = root / 'packed' / 'task_tools.py'
            pack_task_tools(scenario, bundle, 'Example')
            tree = ast.parse(bundle.read_text())
            self.assertEqual([ast.dump(n) for n in tree.body if isinstance(n, ast.FunctionDef)],
                             original_functions)
            self.assertEqual(sum(isinstance(n, ast.ImportFrom) for n in tree.body), 3)
            spec = importlib.util.spec_from_file_location('packed_test_tools', bundle)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            packed = collect_specs(module, 'task')
            self.assertEqual([s.name for s in packed], [s.name for s in specs])
            self.assertIs(packed[0].func.__globals__, packed[1].func.__globals__)
            for original, actual in zip(specs, packed):
                self.assertEqual(original.func.__annotations__, actual.func.__annotations__)
                self.assertEqual(original.parameters, actual.parameters)
                for _ in range(3):
                    self.assertEqual(original.func(None), actual.func(None))
            self.assertEqual(list(bundle.parent.iterdir()), [bundle])

    def test_markdown_roundtrip_and_search_without_source_ids(self):
        docs = [Document('old_a', 'Z title', 'first\n\n- item'),
                Document('old_b', 'A title', 'second')]
        scenario = SimpleNamespace(name='titles', docs=docs)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            packed = packed_documents(scenario)
            for doc in packed:
                _write(root / 'knowledge_base' / document_filename(doc), doc.content)
            with patch.object(rt, 'TASK_DIR', root):
                loaded = rt.load_documents()
            self.assertEqual(loaded, packed)
            self.assertEqual([d.title for d in loaded], ['A title', 'Z title'])
            self.assertEqual(sorted(p.name for p in (root / 'knowledge_base').iterdir()),
                             ['A title.md', 'Z title.md'])
            self.assertEqual((root / 'knowledge_base/Z title.md').read_text(), docs[0].content)
            for corpus in (docs, loaded):
                kb = KnowledgeBase(corpus)
                for result in (kb.search('first'), kb.grep('first')):
                    self.assertIn('Z title', result)
                    self.assertIn(docs[0].content, result)
                    self.assertNotIn('ID:', result)
                    self.assertNotIn('old_a', result)

    def test_scoped_documents_and_difficulty_roundtrip_in_toml(self):
        scenario = SimpleNamespace(docs=[
            Document('a', 'Baseline', '', {'policy_id': 'p1', 'role': 'baseline'}),
            Document('b', 'Factor', '', {'policy_id': 'p1', 'role': 'factor'}),
            Document('c', 'Rule "quoted"', '', {'policy_id': 'p2', 'role': 'policy'}),
            Document('d', 'Unrelated', '', {'policy_id': 'p3'}),
        ])
        opts = SimpleNamespace(agent_timeout_sec=1, verifier_timeout_sec=1, build_timeout_sec=1)
        for count, expected in ((0, 'EASY'), (1, 'EASY'), (2, 'EASY'),
                                (3, 'MEDIUM'), (4, 'HARD'), (5, 'HARD')):
            task = {'charter_scope': {'extended_policies': ['p1', 'p2', 'p1']},
                    'prerequisite_closure': {'resolution_order': list(range(count))},
                    'required_documents': ['p3']}
            meta = {'scenario': 'test', 'category': 'desk', 'company': 'Example',
                    **task_annotations(scenario, task)}
            parsed = tomllib.loads(render_task_toml('test', meta, opts))
            with self.subTest(count=count):
                self.assertEqual(parsed['metadata']['difficulty'], expected)
                self.assertIn(expected, parsed['task']['keywords'])
                self.assertEqual(parsed['metadata']['related_knowledge_base_documents'],
                                 ['Baseline.md', 'Factor.md', 'Rule "quoted".md'])
                self.assertNotIn('knowledge_base_documents', parsed['metadata'])

    def test_invalid_or_colliding_titles_fail_instead_of_losing_documents(self):
        for title in ('', '../escape', 'a/b', 'a\\b', 'a\0b', '界' * 100):
            with self.subTest(title=title), self.assertRaises(ConversionError):
                document_filename(Document('id', title, 'content'))
        for title in ('Title', 'title'):
            scenario = SimpleNamespace(name='duplicate', docs=[
                Document('a', 'Title', 'first'), Document('b', title, 'second')])
            with self.subTest(title=title), self.assertRaises(ConversionError):
                packed_documents(scenario)


if __name__ == '__main__':
    unittest.main()
