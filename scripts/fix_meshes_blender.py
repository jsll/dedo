"""
Blender headless script to fix deformable meshes for PyBullet soft body sim.

Problem: Blender's OBJ export duplicates vertices along UV seams. PyBullet's
soft body solver treats these as separate mass points with only 1-2 spring
connections, causing them to spike out during simulation.

Fix: Merge by distance, dissolve degenerate faces, delete loose geometry.
Then re-export. Also outputs a vertex index remapping so that task_info.py
references can be updated.

Usage:
    blender --background --python scripts/fix_meshes_blender.py

If Blender is not in PATH on macOS:
    /Applications/Blender.app/Contents/MacOS/Blender --background --python scripts/fix_meshes_blender.py

Requires: Blender >= 2.93
"""

import json
import os
from collections import Counter

import bmesh
import bpy

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(REPO_ROOT, 'dedo', 'data')

# Directories to skip (rigid bodies, textures)
SKIP_PREFIXES = ('robots', 'textures')

# Merge threshold in Blender units (OBJ local coords)
MERGE_DISTANCE = 0.0001


def clean_mesh_file(filepath):
    """Load an OBJ, clean it, re-export. Returns (old_to_new_map, stats) or None."""
    # Clear scene
    bpy.ops.wm.read_factory_settings(use_empty=True)

    # Import OBJ
    bpy.ops.wm.obj_import(filepath=filepath)

    obj = None
    for o in bpy.context.scene.objects:
        if o.type == 'MESH':
            obj = o
            break

    if obj is None:
        return None

    # Record original vertex positions (in OBJ order)
    orig_verts = [(v.co.x, v.co.y, v.co.z) for v in obj.data.vertices]
    n_orig = len(orig_verts)

    # Enter edit mode
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')

    # Select all
    bpy.ops.mesh.select_all(action='SELECT')

    # Merge by distance (weld UV seam vertices)
    bpy.ops.mesh.remove_doubles(threshold=MERGE_DISTANCE)

    # Dissolve degenerate faces
    bpy.ops.mesh.dissolve_degenerate(threshold=MERGE_DISTANCE)

    # Delete loose verts/edges
    bpy.ops.mesh.delete_loose(use_verts=True, use_edges=True, use_faces=False)

    # Remove under-connected vertices (<=1 face) that cause physics spikes.
    # Use bmesh for per-vertex face count; iterate until stable.
    bpy.ops.object.mode_set(mode='OBJECT')
    changed = True
    while changed:
        changed = False
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bm.verts.ensure_lookup_table()
        to_remove = [v for v in bm.verts if len(v.link_faces) <= 1]
        if to_remove:
            bmesh.ops.delete(bm, geom=to_remove, context='VERTS')
            changed = True
        bm.to_mesh(obj.data)
        bm.free()
        obj.data.update()

    new_verts = [(v.co.x, v.co.y, v.co.z) for v in obj.data.vertices]
    n_new = len(new_verts)

    if n_new == n_orig:
        return None  # No changes

    # Build old->new mapping by matching vertex positions
    # New verts are a subset of old verts (merged). Find nearest match.
    old_to_new = [-1] * n_orig
    for old_idx, old_pos in enumerate(orig_verts):
        best_dist = float('inf')
        best_new = -1
        for new_idx, new_pos in enumerate(new_verts):
            d = sum((a - b) ** 2 for a, b in zip(old_pos, new_pos, strict=True)) ** 0.5
            if d < best_dist:
                best_dist = d
                best_new = new_idx
                if d < MERGE_DISTANCE:
                    break
        old_to_new[old_idx] = best_new

    # Export OBJ (overwrite original)
    # Remove all objects except the mesh first
    for o in bpy.context.scene.objects:
        if o != obj:
            bpy.data.objects.remove(o, do_unlink=True)

    bpy.ops.wm.obj_export(
        filepath=filepath,
        export_selected_objects=True,
        export_uv=True,
        export_normals=False,  # PyBullet recomputes normals
        export_materials=False,
        export_triangulated_mesh=True,
    )

    stats = {
        'old_verts': n_orig,
        'new_verts': n_new,
        'removed': n_orig - n_new,
    }

    return old_to_new, stats


def main():
    all_mappings = {}
    total_fixed = 0

    for root, _dirs, files in os.walk(DATA_DIR):
        rel_root = os.path.relpath(root, DATA_DIR)
        if any(rel_root.startswith(p) for p in SKIP_PREFIXES):
            continue

        for fname in sorted(files):
            if not fname.endswith('.obj'):
                continue
            fpath = os.path.join(root, fname)
            rel_path = os.path.relpath(fpath, DATA_DIR)

            result = clean_mesh_file(fpath)
            if result is None:
                continue

            old_to_new, stats = result
            all_mappings[rel_path] = old_to_new
            total_fixed += 1
            print(
                f'  {rel_path}: {stats["old_verts"]} -> {stats["new_verts"]} '
                f'(-{stats["removed"]} verts)'
            )

    # Save mappings for task_info.py update
    mappings_path = os.path.join(REPO_ROOT, 'scripts', 'mesh_mappings.json')
    with open(mappings_path, 'w') as f:
        json.dump(all_mappings, f, indent=2)

    print(f'\nFixed {total_fixed} meshes')
    print(f'Mappings saved to {mappings_path}')
    print(
        "\nNext step: run 'uv run python scripts/update_task_info.py' "
        'to update vertex indices in task_info.py'
    )


if __name__ == '__main__':
    main()
