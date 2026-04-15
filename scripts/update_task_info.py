"""
Update vertex indices in task_info.py after mesh cleaning.

Reads the mesh_mappings.json produced by fix_meshes_blender.py and remaps
all vertex references (deform_anchor_vertices, deform_true_loop_vertices,
deform_fixed_anchor_vertex_ids) in DEFORM_INFO.

Usage:
    uv run python scripts/update_task_info.py
"""

import ast
import json
import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAPPINGS_FILE = os.path.join(REPO_ROOT, 'scripts', 'mesh_mappings.json')
TASK_INFO_FILE = os.path.join(REPO_ROOT, 'dedo', 'utils', 'task_info.py')

# Add repo to path so we can import
sys.path.insert(0, REPO_ROOT)


def main():
    if not os.path.exists(MAPPINGS_FILE):
        print(f'No mappings file at {MAPPINGS_FILE}')
        print('Run fix_meshes_blender.py first.')
        sys.exit(1)

    with open(MAPPINGS_FILE) as f:
        all_mappings = json.load(f)

    mappings = {}
    for path, m in all_mappings.items():
        mappings[path] = dict(enumerate(m))

    from dedo.utils.task_info import DEFORM_INFO

    with open(TASK_INFO_FILE) as f:
        content = f.read()

    fields = [
        'deform_anchor_vertices',
        'deform_true_loop_vertices',
        'deform_fixed_anchor_vertex_ids',
    ]
    changes = []

    for mesh_path, info in sorted(DEFORM_INFO.items()):
        if mesh_path not in mappings:
            continue
        m = mappings[mesh_path]

        # Find this mesh entry's dict block in the source
        mesh_key = f"'{mesh_path}'"
        pos = 0
        mesh_pos = -1
        while True:
            p = content.find(mesh_key, pos)
            if p == -1:
                break
            if content[p + len(mesh_key) : p + len(mesh_key) + 5].strip().startswith(':'):
                mesh_pos = p
                break
            pos = p + 1
        if mesh_pos == -1:
            continue

        dict_start = content.find('{', mesh_pos)
        depth = 0
        dict_end = dict_start
        for i in range(dict_start, len(content)):
            if content[i] == '{':
                depth += 1
            elif content[i] == '}':
                depth -= 1
                if depth == 0:
                    dict_end = i + 1
                    break
        block = content[dict_start:dict_end]

        for field in fields:
            if field not in info:
                continue
            old_val = info[field]

            # Remap, filtering out removed vertices (-1)
            if field == 'deform_fixed_anchor_vertex_ids':
                new_val = [m.get(v, v) for v in old_val]
                new_val = [v for v in new_val if v >= 0]
            else:
                new_val = [[m.get(v, v) for v in g] for g in old_val]
                new_val = [[v for v in g if v >= 0] for g in new_val]

            if old_val == new_val:
                continue

            # Warn about removed anchor vertices
            if field == 'deform_anchor_vertices':
                for gi, (og, _ng) in enumerate(zip(old_val, new_val, strict=True)):
                    removed = [v for v in og if m.get(v, v) < 0]
                    if removed:
                        print(
                            f'WARNING: {mesh_path} anchor[{gi}] lost vertices '
                            f'{removed} — manual fix needed!'
                        )

            # Find the field value in the source block
            fp = block.find(f"'{field}'")
            if fp == -1:
                continue
            cp = block.find(':', fp)
            bp = block.find('[', cp)
            d2 = 0
            be = bp
            for i in range(bp, len(block)):
                if block[i] == '[':
                    d2 += 1
                elif block[i] == ']':
                    d2 -= 1
                    if d2 == 0:
                        be = i + 1
                        break

            old_text = block[bp:be]
            clean = re.sub(r'#[^\n]*', '', old_text)
            try:
                if ast.literal_eval(clean) != old_val:
                    print(f'WARNING: parse mismatch for {mesh_path}/{field}, skipping')
                    continue
            except Exception:
                print(f'WARNING: parse error for {mesh_path}/{field}, skipping')
                continue

            if field == 'deform_fixed_anchor_vertex_ids':
                new_text = repr(new_val)
            else:
                indent = '            '
                new_text = '[\n' + '\n'.join(f'{indent}{g},' for g in new_val) + '\n        ]'

            abs_start = dict_start + bp
            abs_end = dict_start + be
            changes.append((abs_start, abs_end, new_text, mesh_path, field))

    # Apply in reverse order
    changes.sort(key=lambda x: x[0], reverse=True)
    for s, e, t, mp, f in changes:
        content = content[:s] + t + content[e:]
        print(f'Updated {mp}/{f}')

    with open(TASK_INFO_FILE, 'w') as f:
        f.write(content)

    print(f'\nApplied {len(changes)} updates to {TASK_INFO_FILE}')
    print(
        '\nNOTE: Entries with comments in anchor_vertices (apron_0/1/2/4) '
        'may need manual fixing — check the diff.'
    )


if __name__ == '__main__':
    main()
