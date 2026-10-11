"""Exercise actual stage-audit link loops and output writers after docs moves."""
import ast
import json
from pathlib import Path
import re
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def main_body(name):
    tree = ast.parse((ROOT / 'scripts' / name).read_text())
    return next(node.body for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'main')


def execute(nodes, namespace):
    exec(compile(ast.Module(body=nodes, type_ignores=[]), '<actual stage-audit statements>', 'exec'), namespace)


class DocumentationPaths(unittest.TestCase):
    def test_actual_link_loops_support_moved_docs_and_directory_links(self):
        for name in ['verify_milestone_05.py', 'verify_milestone_06.py']:
            with self.subTest(script=name):
                body = main_body(name)
                nodes = [node for node in body if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id in {'docs', 'links'} for target in node.targets)]
                nodes += [node for node in body if isinstance(node, ast.For) and isinstance(node.iter, ast.Name) and node.iter.id == 'docs']
                namespace = {'ROOT': ROOT, 're': re}
                execute(nodes, namespace)
                self.assertGreater(namespace['links'], 0)

    def test_actual_writers_preserve_archived_evidence(self):
        for number in ['05', '06']:
            with self.subTest(stage=number), tempfile.TemporaryDirectory() as directory:
                root = Path(directory).resolve()
                historic = root / f'evidence/archive/v1/milestone_{number}_documentation_audit.json'
                historic.parent.mkdir(parents=True)
                historic.write_text('preserved archive sentinel')
                body = main_body(f'verify_milestone_{number}.py')
                # Execute the real output statements, without stage-specific assertions.
                writer = next(i for i, node in enumerate(body) if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute) and node.value.func.attr == 'write_text')
                start = writer
                if writer >= 2 and isinstance(body[writer - 2], ast.Assign) and any(isinstance(target, ast.Name) and target.id == 'destination' for target in body[writer - 2].targets):
                    start = writer - 2
                execute(body[start:writer + 1], {'ROOT': root, 'json': json, 'result': {'result': 'fixture'}})
                self.assertEqual(historic.read_text(), 'preserved archive sentinel')
                current = root / f'.runtime/historical-audits/milestone_{number}_documentation_audit.json'
                self.assertEqual(json.loads(current.read_text()), {'result': 'fixture'})


if __name__ == '__main__':
    unittest.main(verbosity=2)
