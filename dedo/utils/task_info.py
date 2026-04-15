"""
Information for scene and mesh configuration for the default tasks.

Note: this code is for research i.e. quick experimentation; it has minimal
comments for now, but if we see further interest from the community -- we will
add further comments, unify the style, improve efficiency and add unittests.

@contactrika, @yonkshi

"""
import numpy as np

# Task information dictionary/map from task names to mesh file names lists.
# Notes: forward slashes ok as separators on all systems, since we wrap paths
# using pathlib.Path that automatically converts slashes if needed.
TASK_INFO = {
    'HangBag': ['bags/totes/bag0_0.obj',
                'bags/totes/bag1_0.obj',
                'bags/totes/bag2_0.obj',
                ],
    'HangGarment': ['cloth/apron_0.obj',
                    'cloth/apron_1.obj',
                    'cloth/apron_2.obj',
                    'cloth/apron_3.obj',
                    'cloth/apron_4.obj',

                    'cloth/shirt_0.obj',
                    'cloth/shirt_1.obj',
                    'cloth/shirt_2.obj',
                    'cloth/shirt_3.obj',
                    'cloth/shirt_4.obj',
                    ],
    'Button': ['cloth/button_cloth.obj'],
    'ButtonProc': ['proc_button_cloth'],
    'DressBag': [
        'bags/backpack_0.obj',
        'bags/backpack_1.obj',
        'bags/backpack_2.obj',
        'bags/backpack_3.obj',
        'bags/backpack_4.obj',
    ],
    'DressGarment': [
        'cloth/vest_0.obj',
        'cloth/vest_1.obj',
        'cloth/vest_2.obj',
        'cloth/vest_3.obj',
        'cloth/vest_4.obj',
    ],
    'Hoop': ['ropes/hoop3d_0.obj'],
    'Lasso': [
        'ropes/lasso3d_0_fast.obj',
    ],
    'Mask': ['cloth/mask_0.obj',
             'cloth/mask_1.obj',
             'cloth/mask_2.obj',
             'cloth/mask_3.obj',
             'cloth/mask_4.obj',
             ],
    'HangProcCloth': ['procedural_hang_cloth'],
    'BGarments': [],
    'Debug': ['cloth/apron_0_large.obj',
              'bags/backpack_0.obj',
              ],
    'FoodPacking': [
        'ycb/015_peach/google_16k/08194_sparse_textured_ok.obj',
        'ycb/014_lemon/google_16k/08194_sparse_textured_ok.obj',
        'ycb/018_plum/google_16k/08194_sparse_textured_ok.obj',
    ],
}
TOTE_VARS_PER_VERSION = 36  # num. tote mesh variants per major mesh version
TOTE_MAJOR_VERSIONS = 3  # num. major mesh versions for totes (108 meshes total)
MESH_MAJOR_VERSIONS = 5  # num. major mesh versions for all items except totes

# Information about rigid objects to load into the scene.
SCENE_INFO = {
    'debug': {
        'entities': {
            'urdf/hanger.urdf': {
                'basePosition': [0.0, 0, 5.5],
                'baseOrientation': [0, 0, 0],
                'globalScaling': 10.0,
            },
            'urdf/rod.urdf': {
                'basePosition': [0.00, 0.00, 2.00],
                'baseOrientation': [0, 0, 0],
                'globalScaling': 10.0,
            },
        },
        'goal_pos': [-0.077, 0.03, 0.315],
        'easy_target_pos': [-0.077, 0.12, 0.315],
    },
    'dress': {
        'entities': {
            'urdf/figure_headless.urdf': {
                'basePosition': [-0.22, 0, 3.00],
                'baseOrientation': [0, 0, np.pi / 2],
                'globalScaling': 10,
                'useTexture': True,
            },
            'head_with_ears2.obj': {
                'basePosition': [-0.22, 0.00, 6.54],  # [-0.22, 0.00, 0.64],
                'baseOrientation': [0, 0, np.pi * 1.05],
                'globalScaling': 0.4,
                'rgbaColor': (0.9, 0.75, 0.65, 1),
            },
        },
        'goal_pos': [[-1, -0.23, 5.3],
                     [0.6, -0.23, 5.3], ],
        'easy_target_pos': [-0.077, 2, 3.00],
    },
    'hangbag': {
        'entities': {
            'pole.obj': {
                'basePosition': [0.0, 0.0, 5],
                'baseOrientation': [np.pi / 2, 0, 0],
                'globalScaling': 0.5,
                'rgbaColor': (0.9, 0.75, 0.65, 1),
                'useTexture': True,
            },
            'urdf/hook_small.urdf': {
                'basePosition': [0, 1.28, 9],
                'baseOrientation': [0, 0, np.pi / 2],
                'globalScaling': 10,

            },

        },
        'goal_pos': [[0.00, 1.28, 9]],
    },
    'hangcloth': {
        'entities': {
            'urdf/hanger.urdf': {
                'basePosition': [0.0, 0, 8],
                'baseOrientation': [0, 0, 0],
                'globalScaling': 10.0,

            },
            'urdf/tallrod.urdf': {
                'basePosition': [0.00, 0.00, 0],
                'baseOrientation': [0, 0, 0],
                'globalScaling': 10.0,
                'useTexture': True,
            },

        },
        'goal_pos': [[0, 0.00, 8.2]],
    },
    'button': {
        'entities': {
            'urdf/torso.urdf': {
                'basePosition': [0.0, 0.0, 2],
                'baseOrientation': [0, 0, 0],
                'globalScaling': 1,
                'useTexture': True,
            },
            'urdf/button_fixed.urdf': {
                'basePosition': [1.95, 0.20, 2.70],
                'baseOrientation': [0, 0, np.pi / 2],
                'globalScaling': 7,
            },
            'urdf/button_fixed2.urdf': {
                'basePosition': [2.25, 0.20, 1.40],
                'baseOrientation': [0, 0, np.pi / 2],
                'globalScaling': 7,
            },
        },
        'goal_pos': [[1.95, 0.00, 2.70], [2.25, 0.00, 1.40]],

    },
    'hoop': {
        'entities': {
            'urdf/rod.urdf': {
                'basePosition': [0.00, 0.00, 0.00],
                'baseOrientation': [0, 0, 0],
                'globalScaling': 10.0,
                'useTexture': True,
            },
            'urdf/rod2.urdf': {
                'basePosition': [2.00, 3.00, 0.00],
                'baseOrientation': [0, 0, 0],
                'globalScaling': 10.0,
                'useTexture': True,
            },
        },
        'goal_pos': [[0, 0.00, 0.5]],
        'easy_target_pos': [0.00, 0.00, 0.35],
    },
    'lasso': {
        'entities': {
            'urdf/rod.urdf': {
                'basePosition': [0.00, 0.00, 0.00],
                'baseOrientation': [0, 0, 0],
                'globalScaling': 10.0,
                'useTexture': True,
            },
        },
        'goal_pos': [[0, 0.00, 0.5]],
        'easy_target_pos': [0.00, 0.00, 0.35],
    },
    'mask': {
        'entities': {
            'urdf/figure_headless.urdf': {
                'basePosition': [-0.22, 0, 3.00],
                'baseOrientation': [0, 0, np.pi / 2],
                'globalScaling': 10,
                'useTexture': True,
            },
            'head_with_ears2.obj': {
                'basePosition': [-0.22, 0.00, 6.54],  # [-0.22, 0.00, 0.64],
                'baseOrientation': [0, 0, np.pi * 1.05],
                'globalScaling': 0.4,
                'rgbaColor': (0.9, 0.75, 0.65, 1),
            },
        },
        'goal_pos': [[-0.7, 0.00, 6.5],
                     [0.3, 0.00, 6.5], ],
    },
    'foodpacking': {
        'entities': {
            'urdf/borders.urdf': {
                'basePosition': [-1.5, 2.0, 0.5],
                'baseOrientation': [0, 0, 0],
                'globalScaling': 4.0,
                'mass': 0,
                'useTexture': True,
            },
            # 'ycb/004_sugar_box/google_16k/textured.obj': {
            # 'ycb/009_gelatin_box/google_16k/textured.obj': {
            'ycb/003_cracker_box/google_16k/textured.obj': {
                'basePosition': [1.8, 1.7, 0.25],
                'baseOrientation': [0, 0, 0],
                'globalScaling': 7.0,
                'mass': 0.01,
                'rgbaColor': (0.9, 0.75, 0.65, 1),
            },
            # 'ycb/005_tomato_soup_can/google_16k/textured.obj': {
            # 'ycb/007_tuna_fish_can/google_16k/textured.obj': {
            'ycb/002_master_chef_can/google_16k/textured.obj': {
                'basePosition': [0.9, 1.5, 0.25],
                'baseOrientation': [0, 0, 0],
                'globalScaling': 8.0,
                'mass': 0.01,
                'rgbaColor': (0.9, 0.75, 0.65, 1),
            },
        },
        'goal_pos': [[-2.5, 2.0, 0.5]],
    },
}

# Information about deformable objects.
DEFORM_INFO = {
    'procedural_hang_cloth': {
        'deform_init_pos': [0, 5, 8],
        'deform_init_ori': [-np.pi / 2, 0, 3 * np.pi / 2],
        'deform_scale': 3,
        'deform_elastic_stiffness': 50,
        'deform_bending_stiffness': 1,
        'deform_damping_stiffness': 0.1,
        'cam_viewmat': [8.8, -12.6, 314, -0.4, 0.6, 5.3],
        'plane_texture_file': 'textures/plane/brown_yellow_carpet.jpg',
        'rigid_texture_file': "textures/rigid/lightwood.jpg",
        'deform_texture_file': 'textures/deform/pb_greenleaves.png',
    },
    'bags/totes/bag0_0.obj': {
        'deform_init_pos': [0, 8, 2],
        'deform_init_ori': [np.pi / 2, 0, 0],
        'deform_scale': 1,
        'deform_elastic_stiffness': 50,
        'deform_bending_stiffness': 1,
        'deform_damping_stiffness': 0.1,
        'disable_self_collision': True,
        'deform_anchor_vertices': [
            [187],
            [238],
        ],
        'deform_true_loop_vertices': [
            [515, 511, 509, 507, 505, 512, 510, 508, 506, 502, 504, 503, 514,
             513, ],
            [461, 457, 455, 453, 451, 458, 456, 454, 452, 448, ],
        ],
        'cam_viewmat': [8, -5.8, 272, 1.05, 4.04, 5.22],
        'plane_texture_file': 'textures/plane/white_marble.jpg',
        'rigid_texture_file': "textures/rigid/darkwood.jpg",
        'deform_texture_file': 'textures/deform/pb_bluegold_pattern.jpg',
    },
    'bags/totes/bag1_0.obj': {
        'deform_init_pos': [0, 8, 2],
        'deform_init_ori': [np.pi / 2, 0, 0],
        'deform_scale': 1,
        'deform_elastic_stiffness': 50,
        'deform_bending_stiffness': 1,
        'deform_damping_stiffness': 0.1,
        'disable_self_collision': True,
        'deform_anchor_vertices': [
            [209],
            [297],
        ],
        'deform_true_loop_vertices': [
            [200, 190, 535, 534, 533, 532, 259, 276, 196, 191, 539, 538, 537,
             536, 258, 280, 196, 197, 198, 199, 280, 279, 278, 277, ],
            [167, 166, 164, 165, 163, 354, 353, 352, 351, 350, 178, 487, 486,
             485, 484, 333, 179, 491, 490, 489, 488, 332, ],
        ],
        'cam_viewmat': [8, -5.8, 272, 1.05, 4.04, 5.22],
        'plane_texture_file': 'textures/plane/grey_tile.jpg',
        'rigid_texture_file': "textures/rigid/marble.png",
        'deform_texture_file': 'textures/deform/pb_jeans.jpg',
    },
    'bags/totes/bag2_0.obj': {
        'deform_init_pos': [0, 8, 2],
        'deform_init_ori': [np.pi / 2, 0, 0],
        'deform_scale': 1,
        'deform_elastic_stiffness': 50,
        'deform_bending_stiffness': 1,
        'deform_damping_stiffness': 0.1,
        'disable_self_collision': True,
        'deform_anchor_vertices': [
            [220],
            [299],
        ],
        'deform_texture_file': 'textures/deform/pb_pink_fur.jpg',
        'rigid_texture_file': "textures/rigid/darkwood.jpg",
        'plane_texture_file': 'textures/plane/cobblestone.jpg',
        'deform_true_loop_vertices': [
            [195, 196, 197, 198, 199, 200, 186, 179, 479, 478, 477, 476, 243,
             254, 263, 264, 265, 266, 267, 268, 269,
             255, 242, 480, 481, 482, 483, 180, 185, 194],
            [335, 321, 308, 444, 445, 446, 447, 171, 162, 153, 329, 320, 309,
             440, 441, 442, 443, 170, 161, 147, 152,
             151, 150, 149, 148, 335, 334, 333, 332, 331, 330],
        ],
        'cam_viewmat': [8, -5.8, 272, 1.05, 4.04, 5.22],
    },
    'bags/backpack_0.obj': {
        'deform_init_pos': [-0.2, 2, 4],
        'deform_init_ori': [-np.pi / 2, -np.pi, np.pi],
        'deform_scale': 3,
        'deform_elastic_stiffness': 100,
        # 'deform_bending_stiffness': 5,
        'deform_bending_stiffness': 10,
        'deform_damping_stiffness': 0.1,
        'cam_viewmat': [7, -32, 499, 0.15, -0.25, 3.1],
        'max_episode_len': 700,
        'disable_self_collision': True,
        'deform_anchor_vertices': [
            [480],
            [264],
        ],
        'deform_true_loop_vertices': [
            [139, 199, 218, 7, 237, 238, 239, 240, 241, 243, 246, 248, 250, 252, 253, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 272, 290, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 517],
            [305, 307, 314, 315, 365, 366, 375, 391, 393, 434, 385, 450, 451, 452, 453, 454, 455, 458, 461, 462, 464, 466, 468, 471, 472, 473, 474, 475, 476, 477, 478, 479, 480, 485, 503, 505, 507, 508, 509, 510, 511, 512, 513, 514, 515],
        ],

        'plane_texture_file': 'textures/plane/red_brick.jpg',
        'rigid_texture_file': "textures/rigid/darkbrownwood.jpg",
        'deform_texture_file': 'textures/deform/pb_whitered_checker.jpg',
    },
    'bags/backpack_1.obj': {
        'deform_init_pos': [-0.2, 2, 4],
        'deform_init_ori': [-np.pi / 2, -np.pi, np.pi],
        'deform_scale': 3,
        'deform_elastic_stiffness': 100,
        # 'deform_bending_stiffness': 5,
        'deform_bending_stiffness': 10,
        'deform_damping_stiffness': 0.1,
        'cam_viewmat': [7, -32, 499, 0.15, -0.25, 3.1],
        'max_episode_len': 700,
        'disable_self_collision': True,
        'deform_anchor_vertices': [
            [471],
            [256],
        ],
        'deform_true_loop_vertices': [
            [115, 139, 200, 217, 7, 236, 238, 239, 240, 241, 242, 243, 244, 246, 247, 248, 249, 250, 253, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 291, 293, 294, 295, 296, 297, 298, 299, 300, 301, 521],
            [183, 218, 377, 388, 426, 436, 452, 453, 455, 456, 457, 458, 459, 462, 463, 464, 465, 467, 472, 473, 475, 476, 477, 478, 479, 480, 481, 482, 484, 507, 509, 511, 512, 513, 514, 515, 516, 517, 518, 519, 308],
        ],

        'plane_texture_file': 'textures/plane/white_marble.jpg',
        'rigid_texture_file': "textures/rigid/darkbrownwood.jpg",
        'deform_texture_file': 'textures/deform/pb_pink_fur.jpg',

    },
    'bags/backpack_2.obj': {
        'deform_init_pos': [-0.2, 2, 4],
        'deform_init_ori': [-np.pi / 2, -np.pi, np.pi],
        'deform_scale': 3,
        'deform_elastic_stiffness': 100,
        # 'deform_bending_stiffness': 5,
        'deform_bending_stiffness': 10,
        'deform_damping_stiffness': 0.1,
        'disable_self_collision': True,
        'cam_viewmat': [7, -32, 499, 0.15, -0.25, 3.1],
        'max_episode_len': 700,
        'deform_anchor_vertices': [
            [468],
            [254],
        ],
        'deform_true_loop_vertices': [
            [23, 25, 95, 97, 114, 115, 144, 152, 238, 239, 241, 240, 242, 243, 245, 246, 247, 248, 249, 250, 251, 252, 254, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 273, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301],
            [180, 217, 236, 306, 315, 316, 365, 366, 92, 377, 390, 392, 434, 394, 451, 452, 453, 454, 455, 456, 459, 460, 461, 462, 464, 466, 469, 470, 472, 473, 474, 475, 476, 477, 478, 479, 481, 504, 506, 508, 509, 510, 511, 512, 513, 514, 515, 516, 308],
        ],
        'plane_texture_file': 'textures/plane/grass.jpg',
        'rigid_texture_file': "textures/rigid/darkbrownwood.jpg",
        'deform_texture_file': 'textures/deform/pd_gold.jpg',
    },
    'bags/backpack_3.obj': {
        'deform_init_pos': [-0.2, 2, 4],
        'deform_init_ori': [-np.pi / 2, -np.pi, np.pi],
        'deform_scale': 3,
        'deform_elastic_stiffness': 100,
        # 'deform_bending_stiffness': 5,
        'deform_bending_stiffness': 10,
        'deform_damping_stiffness': 0.1,
        'cam_viewmat': [7, -32, 499, 0.15, -0.25, 3.1],
        'max_episode_len': 700,
        'disable_self_collision': True,
        'deform_anchor_vertices': [
            [455],
            [260],
        ],
        'deform_true_loop_vertices': [
            [20, 26, 98, 100, 118, 243, 244, 245, 246, 248, 250, 251, 252, 254, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 293, 294, 295, 296, 297, 298, 299, 300, 301, 303],
            [95, 184, 308, 317, 238, 379, 394, 396, 30, 422, 432, 452, 454, 455, 456, 459, 461, 462, 463, 464, 466, 469, 470, 472, 473, 474, 475, 476, 477, 478, 479, 481, 504, 506, 508, 509, 510, 511, 512, 513, 514, 516],
        ],
        'plane_texture_file': 'textures/plane/brown_brick.jpg',
        'rigid_texture_file': "textures/rigid/darkbrownwood.jpg",
        'deform_texture_file': 'textures/deform/pb_pink_silk.jpg',

    },
    'bags/backpack_4.obj': {
        'deform_init_pos': [-0.2, 2, 4],
        'deform_init_ori': [-np.pi / 2, -np.pi, np.pi],
        'deform_scale': 3,
        'deform_elastic_stiffness': 100,
        # 'deform_bending_stiffness': 5,
        'deform_bending_stiffness': 10,
        'deform_damping_stiffness': 0.1,
        'disable_self_collision': True,
        'cam_viewmat': [7, -32, 499, 0.15, -0.25, 3.1],
        'max_episode_len': 700,
        'deform_anchor_vertices': [
            [472],
            [242],
        ],
        'deform_true_loop_vertices': [
            [19, 115, 150, 238, 241, 240, 246, 248, 250, 251, 252, 254, 255, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 292, 293, 294, 295, 296, 297, 298, 300, 301],
            [376, 450, 452, 453, 451, 458, 460, 462, 463, 465, 466, 467, 468, 469, 471, 472, 473, 474, 475, 476, 477, 478, 480, 505, 507, 508, 509, 510, 511, 512, 514, 515],
        ],
        'plane_texture_file': 'textures/plane/black_tile.jpg',
        'rigid_texture_file': "textures/rigid/darkbrownwood.jpg",
        'deform_texture_file': 'textures/deform/pb_white_knit.jpg',
    },
    'cloth/vest_0.obj': {
        'deform_init_pos': [0, 2, 5],
        'deform_init_ori': [np.pi / 2, 0, 0],
        'deform_scale': 3,
        'deform_elastic_stiffness': 80,
        # 'deform_bending_stiffness': 5,
        'deform_bending_stiffness': 0.1,
        'deform_damping_stiffness': 0.1,
        'deform_anchor_vertices': [
            [42],
            [229],
        ],
        'deform_true_loop_vertices': [
            [200, 201, 203, 246, 247, 284, 287, 292, 295, 298, 357, 358, 359, 360, 365, 367, 368],
            [6, 8, 9, 10, 57, 59, 93, 95, 96, 99, 102, 104, 172, 173, 174, 179, 180, 182, 183],
        ],
        'cam_viewmat': [4.2, -26, 151, 0.04, 0.17, 4.66],
        'max_episode_len': 350,
        'plane_texture_file': 'textures/plane/stonefloor.jpg',
        'rigid_texture_file': "textures/rigid/birch.png",
        'deform_texture_file': 'textures/deform/pb_camo.png',
    },
    'cloth/vest_1.obj': {
        'deform_init_pos': [0, 2, 5],
        'deform_init_ori': [np.pi / 2, 0, 0],
        'deform_scale': 3,
        'deform_elastic_stiffness': 80,
        # 'deform_bending_stiffness': 5,
        'deform_bending_stiffness': 0.1,
        'deform_damping_stiffness': 0.1,
        'deform_anchor_vertices': [
            [0],
            [192],
        ],

        'deform_true_loop_vertices': [
            [198, 200, 201, 203, 247, 248, 287, 290, 295, 297, 298, 300, 360, 361, 362, 367, 369, 370],
            [6, 8, 9, 10, 56, 58, 95, 97, 98, 101, 103, 104, 106, 175, 176, 181, 182, 184, 185],
        ],
        'cam_viewmat': [4.2, -26, 151, 0.04, 0.17, 4.66],
        'max_episode_len': 350,
        'plane_texture_file': 'textures/plane/brown_brick.jpg',
        'rigid_texture_file': "textures/rigid/brown_brick.jpg",
        'deform_texture_file': 'textures/deform/pb_greenleaves.png',
    },
    'cloth/vest_2.obj': {
        'deform_init_pos': [0, 2, 5],
        'deform_init_ori': [np.pi / 2, 0, 0],
        'deform_scale': 3,
        'deform_elastic_stiffness': 80,
        # 'deform_bending_stiffness': 5,
        'deform_bending_stiffness': 0.1,
        'deform_damping_stiffness': 0.1,
        'deform_anchor_vertices': [
            [0],
            [213],
        ],

        'deform_true_loop_vertices': [
            [219, 220, 222, 265, 266, 306, 314, 318, 322, 323, 324, 384, 385, 386, 391, 393, 394],
            [53, 54, 55, 56, 60, 62, 109, 114, 115, 119, 121, 194, 195, 201],
        ],
        'cam_viewmat': [4.2, -26, 151, 0.04, 0.17, 4.66],
        'max_episode_len': 350,
        'plane_texture_file': 'textures/plane/cobblestone.jpg',
        'rigid_texture_file': "textures/rigid/brown_brick.jpg",
        'deform_texture_file': 'textures/deform/orange_pattern.png',
    },
    'cloth/vest_3.obj': {
        'deform_init_pos': [0, 2, 5],
        'deform_init_ori': [np.pi / 2, 0, 0],
        'deform_scale': 3,
        'deform_elastic_stiffness': 80,
        # 'deform_bending_stiffness': 5,
        'deform_bending_stiffness': 0.1,
        'deform_damping_stiffness': 0.1,
        'deform_anchor_vertices': [
            [0],
            [197],
        ],

        'deform_true_loop_vertices': [
            [205, 206, 208, 253, 254, 304, 309, 313, 314, 378, 379, 384, 386, 387],
            [8, 9, 10, 57, 59, 97, 104, 108, 109, 111, 112, 165, 167, 180, 188, 190, 191, 192],
        ],
        'cam_viewmat': [4.2, -26, 151, 0.04, 0.17, 4.66],
        'max_episode_len': 350,
        'plane_texture_file': 'textures/plane/grass.jpg',
        'rigid_texture_file': "textures/rigid/brown_brick.jpg",
        'deform_texture_file': 'textures/deform/pd_goldpattern.jpg',
    },
    'cloth/vest_4.obj': {
        'deform_init_pos': [0, 2, 5],
        'deform_init_ori': [np.pi / 2, 0, 0],
        'deform_scale': 3,
        'deform_elastic_stiffness': 80,
        # 'deform_bending_stiffness': 5,
        'deform_bending_stiffness': 0.1,
        'deform_damping_stiffness': 0.1,
        'deform_anchor_vertices': [
            [0],
            [198],
        ],

        'deform_true_loop_vertices': [
            [204, 206, 207, 209, 253, 254, 294, 302, 303, 305, 306, 308, 368, 369, 370, 375, 377, 378],
            [8, 9, 10, 56, 58, 96, 103, 107, 111, 112, 181, 182, 183, 188, 190, 191],
        ],
        'cam_viewmat': [4.2, -26, 151, 0.04, 0.17, 4.66],
        'max_episode_len': 350,
        'plane_texture_file': 'textures/plane/lightwood.jpg',
        'rigid_texture_file': "textures/rigid/brown_brick.jpg",
        'deform_texture_file': 'textures/deform/pb_whitered_checker.jpg',

    },
    'cloth/apron_0.obj': {
        'deform_init_pos': [0, 5, 8],
        'deform_init_ori': [np.pi / 2, 0, np.pi],
        'deform_scale': 3,
        'deform_elastic_stiffness': 50,
        'deform_bending_stiffness': 1,
        'deform_damping_stiffness': 0.1,
        'deform_anchor_vertices': [
            [14],
            [151],
        ],

        'cam_viewmat': [8.8, -12.6, 314, -0.4, 0.6, 5.3],

        'deform_true_loop_vertices': [
            [0, 1, 3, 4, 7, 8, 9, 11, 13, 15, 17, 19, 21, 23, 24, 25, 137, 138, 140, 141, 143, 144, 145, 147, 148, 150, 153, 155, 157, 159, 160, 253],
            [58, 91, 92, 93, 94, 117, 125, 126, 127, 128, 129, 130, 131, 132, 57, 133, 135, 136, 211, 212, 213, 214, 234, 236, 241, 242, 243, 244, 245, 246, 247, 248, 249, 181, 250, 251, 252, 256, 257],
        ],
        'plane_texture_file': 'textures/plane/brown_yellow_carpet.jpg',
        'rigid_texture_file': "textures/rigid/red_leather.jpg",
        'deform_texture_file': 'textures/deform/pb_lightblue_rings.png',
    },
    'cloth/apron_1.obj': {
        'deform_init_pos': [0, 5, 8],
        'deform_init_ori': [np.pi / 2, 0, np.pi],
        'deform_scale': 3,
        'deform_elastic_stiffness': 50,
        'deform_bending_stiffness': 1,
        'deform_damping_stiffness': 0.1,
        'cam_viewmat': [8.8, -12.6, 314, -0.4, 0.6, 5.3],

        'deform_anchor_vertices': [
            [14],
            [155],
        ],
        'deform_true_loop_vertices': [
            [1, 2, 4, 6, 7, 8, 10, 9, 11, 12, 13, 14, 15, 17, 19, 21, 22, 23, 24, 25, 26, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 157, 159, 161, 162, 163, 164, 191],
            [60, 62, 95, 96, 97, 98, 120, 121, 128, 129, 130, 131, 132, 133, 134, 136, 61, 59, 135, 137, 138, 139, 140, 185, 186, 215, 216, 217, 218, 239, 240, 245, 246, 247, 248, 249, 251, 252, 253, 254, 255, 256, 257, 250],
        ],
        'plane_texture_file': 'textures/plane/blue_carpet.jpg',
        'rigid_texture_file': "textures/rigid/birch.png",
        'deform_texture_file': 'textures/deform/pd_goldpattern.jpg',
    },
    'cloth/apron_2.obj': {
        'deform_init_pos': [0, 5, 8],
        'deform_init_ori': [np.pi / 2, 0, np.pi],
        'deform_scale': 3,
        'deform_elastic_stiffness': 50,
        'deform_bending_stiffness': 1,
        'deform_damping_stiffness': 0.1,
        'cam_viewmat': [8.8, -12.6, 314, -0.4, 0.6, 5.3],
        'deform_anchor_vertices': [
            [153],
            [15],
        ],
        'deform_true_loop_vertices': [
            [0, 2, 4, 6, 8, 9, 10, 11, 12, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 142, 145, 147, 148, 149, 150, 151, 152, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165],
            [61, 62, 64, 97, 98, 99, 100, 122, 123, 128, 129, 130, 131, 132, 133, 134, 135, 137, 136, 63, 138, 139, 140, 141, 216, 217, 219, 220, 240, 241, 246, 247, 248, 249, 250, 252, 253, 254, 255, 187, 186, 256, 257, 251],
        ],
        'plane_texture_file': 'textures/plane/grey_tile.jpg',
        'rigid_texture_file': "textures/rigid/birch.png",
        'deform_texture_file': 'textures/deform/pb_pink_silk.jpg',
    },
    'cloth/apron_3.obj': {
        'deform_init_pos': [0, 5, 8],
        'deform_init_ori': [np.pi / 2, 0, np.pi],
        'deform_scale': 3,
        'deform_elastic_stiffness': 50,
        'deform_bending_stiffness': 1,
        'deform_damping_stiffness': 0.1,
        'cam_viewmat': [8.8, -12.6, 314, -0.4, 0.6, 5.3],
        'deform_anchor_vertices': [
            [128],  # 10, 12, 13, 14, 15],
            [79],  # 167, 169, 171, 172, 174],
        ],
        'deform_true_loop_vertices': [
            [0, 1, 2, 31, 32, 33, 34, 35, 75, 76, 77, 79, 81, 82, 83, 123, 124,
             125, 126, 128, 129, 163, 165, 166, 168, 171, 173, 272, 273, 274,
             277, 307, 308, 347, 348, 349, 350, 351, 352, 354, 355, 403, 404,
             406, 467, 468, 469, 471, 472, 473, 474, 475, 476, 478, 480, 481,
             482, 483, 501, 502, 503, 504, 505, 506, 509, 516, 517, 544, 567,
             568, 584, 591, 592, 593, 594, 595, 597, 598, 604],
            [20, 25, 26, 28, 48, 49, 56, 57, 61, 62, 63, 66, 67, 70, 71, 72,
             108, 111, 113, 114, 115, 117, 120, 121, 154, 155, 157, 160, 162,
             193, 206, 207, 256, 258, 262, 265, 266, 267, 268, 269, 270, 271,
             336, 338, 339, 340, 341, 342, 343, 344, 345, 346, 377, 395, 396,
             397, 398, 400, 401, 402, 425, 438, 458, 459, 460, 461, 462, 464,
             465, 466, 491, 498, 499, 534, 538, 554, 564, 566, 582,
             583, 589, 590, 602, 603],
        ],
        'plane_texture_file': 'textures/plane/cobblestone.jpg',
        'rigid_texture_file': "textures/rigid/darkbrownwood.jpg",
        'deform_texture_file': 'textures/deform/pd_gold.jpg',
    },
    'cloth/apron_4.obj': {
        'deform_init_pos': [0, 5, 8],
        'deform_init_ori': [np.pi / 2, 0, np.pi],
        'deform_scale': 3,
        'deform_elastic_stiffness': 50,
        'deform_bending_stiffness': 1,
        'deform_damping_stiffness': 0.1,
        'cam_viewmat': [8.8, -12.6, 314, -0.4, 0.6, 5.3],
        'deform_anchor_vertices': [
            [14],
            [154],
        ],
        'deform_true_loop_vertices': [
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 19, 21, 22, 23, 24, 25, 26, 126, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 156, 158, 160, 161, 162, 163, 190],
            [60, 62, 95, 96, 97, 98, 120, 121, 128, 129, 130, 134, 136, 135, 61, 59, 137, 138, 139, 184, 214, 215, 216, 217, 238, 239, 244, 245, 246, 247, 252, 253, 185, 251, 254, 255, 256, 257],
        ],
        'plane_texture_file': 'textures/plane/grass.jpg',
        'rigid_texture_file': "textures/rigid/red_marble.png",
        'deform_texture_file': 'textures/deform/pb_whitered_checker.jpg',
    },
    'cloth/shirt_0.obj': {
        'deform_init_pos': [0, 3, 4],  # [0, 0, 6]
        'deform_init_ori': [np.pi / 2, 0, 0],
        'deform_scale': 5,
        'deform_elastic_stiffness': 90,
        'deform_bending_stiffness': 0.1,
        'deform_damping_stiffness': 0.1,
        'deform_friction_coeff': 0.5,
        'cam_viewmat': [7.2, -30, 323, -0.37, 1.08, 4.7],
        'deform_anchor_vertices': [
            [270],
            [3],
        ],
        'max_episode_len': 300,
        'deform_true_loop_vertices': [
            [0, 3, 5, 7, 11, 12, 15, 17, 19, 236, 268, 270, 273, 275, 278, 280, 282, 284, 286, 287, 494],
        ],
        'deform_texture_file': 'textures/deform/pb_leopard.png',
        'plane_texture_file': 'textures/plane/cobblestone.jpg',
        'rigid_texture_file': "textures/rigid/concrete.jpg",
    },
    'cloth/shirt_1.obj': {
        'deform_init_pos': [0, 3, 4],  # [0, 0, 6]
        'deform_init_ori': [np.pi / 2, 0, 0],
        'deform_scale': 5,
        'deform_elastic_stiffness': 90,
        'deform_bending_stiffness': 0.1,
        'deform_damping_stiffness': 0.1,
        'deform_friction_coeff': 0.5,
        'cam_viewmat': [7.2, -30, 323, -0.37, 1.08, 4.7],
        'deform_anchor_vertices': [
            [270],
            [3],
        ],
        'max_episode_len': 300,
        'deform_true_loop_vertices': [
            [0, 3, 5, 7, 11, 12, 15, 17, 19, 237, 268, 270, 273, 275, 278, 280, 282, 284, 286, 287, 495],
        ],
        'deform_texture_file': 'textures/deform/pb_purple_fancy.jpg',
        'plane_texture_file': 'textures/plane/brown_yellow_carpet.jpg',
        'rigid_texture_file': "textures/rigid/red_leather.jpg",
    },
    'cloth/shirt_2.obj': {
        'deform_init_pos': [0, 3, 4],  # [0, 0, 6]
        'deform_init_ori': [np.pi / 2, 0, 0],
        'deform_scale': 5,
        'deform_elastic_stiffness': 90,
        'deform_bending_stiffness': 0.1,
        'deform_damping_stiffness': 0.1,
        'deform_friction_coeff': 0.5,
        'cam_viewmat': [7.2, -30, 323, -0.37, 1.08, 4.7],
        'deform_anchor_vertices': [
            [270],
            [3],
        ],
        'max_episode_len': 300,
        'deform_true_loop_vertices': [
            [0, 3, 5, 7, 11, 12, 15, 17, 19, 237, 268, 270, 273, 275, 278, 280, 282, 284, 286, 287, 494],
        ],
        'deform_texture_file': 'textures/deform/pb_jeans.jpg',
        'plane_texture_file': 'textures/plane/grey_tile.jpg',
        'rigid_texture_file': "textures/rigid/marble.png",
    },
    'cloth/shirt_3.obj': {
        'deform_init_pos': [0, 3, 4],  # [0, 0, 6]
        'deform_init_ori': [np.pi / 2, 0, 0],
        'deform_scale': 5,
        'deform_elastic_stiffness': 90,
        'deform_bending_stiffness': 0.1,
        'deform_damping_stiffness': 0.1,
        'deform_friction_coeff': 0.5,
        'cam_viewmat': [7.2, -30, 323, -0.37, 1.08, 4.7],
        'deform_anchor_vertices': [
            [275],
            [3],
        ],
        'max_episode_len': 300,
        'deform_true_loop_vertices': [
            [0, 3, 5, 7, 11, 12, 15, 17, 19, 237, 273, 275, 278, 280, 283, 285, 287, 289, 291, 292, 500],
        ],
        'plane_texture_file': 'textures/plane/white_brick.jpg',
        'rigid_texture_file': "textures/rigid/concrete.jpg",
        'deform_texture_file': 'textures/deform/pb_canvas.jpg',
    },
    'cloth/shirt_4.obj': {
        'deform_init_pos': [0, 3, 4],  # [0, 0, 6]
        'deform_init_ori': [np.pi / 2, 0, 0],
        'deform_scale': 5,
        'deform_elastic_stiffness': 90,
        'deform_bending_stiffness': 0.1,
        'deform_damping_stiffness': 0.1,
        'deform_friction_coeff': 0.5,
        'cam_viewmat': [7.2, -30, 323, -0.37, 1.08, 4.7],
        'deform_anchor_vertices': [
            [270],
            [3],
        ],
        'max_episode_len': 300,
        'deform_true_loop_vertices': [
            [0, 3, 5, 7, 11, 12, 15, 17, 19, 237, 268, 270, 273, 275, 278, 280, 282, 284, 286, 287, 495],
        ],
        'deform_texture_file': 'textures/deform/pb_white_knit.jpg',
        'plane_texture_file': 'textures/plane/blue_carpet.jpg',
        'rigid_texture_file': "textures/rigid/darkwood.jpg",
    },
    'cloth/tshirt_0.obj': {
        'deform_init_pos': [0, 3, 4],
        'deform_init_ori': [np.pi / 2, 0, 0],
        'deform_scale': 5,
        'deform_elastic_stiffness': 90,
        'deform_bending_stiffness': 0.1,
        'deform_damping_stiffness': 0.1,
        'deform_friction_coeff': 0.5,
        'cam_viewmat': [10.6, -16.4, 269, -0.16, 1.2, 8.2],
        'deform_anchor_vertices': [
            [6],
            [304],
        ],
        'deform_true_loop_vertices': [
            [0, 3, 4, 5, 6, 7, 9, 13, 14, 17, 19, 21, 249, 283, 284, 285, 286, 287, 288, 290, 292, 295, 297, 299, 301, 303, 304, 511],
        ],
        'deform_texture_file': 'textures/deform/pd_gold.jpg',
        'plane_texture_file': 'textures/plane/black_tile.jpg',
        'rigid_texture_file': "textures/rigid/metal.jpg",
    },
    'cloth/tshirt_1.obj': {
        'deform_init_pos': [0, 3, 4],
        'deform_init_ori': [np.pi / 2, 0, 0],
        'deform_scale': 5,
        'deform_elastic_stiffness': 90,
        'deform_bending_stiffness': 0.1,
        'deform_damping_stiffness': 0.1,
        'deform_friction_coeff': 0.1,
        'cam_viewmat': [11.3, -28, 193.4, -0.08, 0.29, 1.80],
        'deform_anchor_vertices': [
            [288],
            [259],
        ],

        'deform_true_loop_vertices': [
            [0, 3, 5, 7, 9, 13, 14, 16, 17, 19, 21, 22, 250, 283, 285, 287, 288, 290, 292, 295, 297, 299, 301, 303, 304, 512],
        ],
        'deform_texture_file': 'textures/deform/pb_purple_fancy.jpg',
        'plane_texture_file': 'textures/plane/brown_yellow_carpet.jpg',
        'rigid_texture_file': "textures/rigid/red_leather.jpg",
    },
    'cloth/tshirt_2.obj': {
        'deform_init_pos': [0, 3, 4],
        'deform_init_ori': [np.pi / 2, 0, 0],
        'deform_scale': 5,
        'deform_elastic_stiffness': 90,
        'deform_bending_stiffness': 0.1,
        'deform_damping_stiffness': 0.1,
        'deform_friction_coeff': 0.5,
        'cam_viewmat': [11.3, -28, 193.4, -0.08, 0.29, 1.80],
        'deform_anchor_vertices': [
            [288],
            [259],
        ],

        'deform_true_loop_vertices': [
            [0, 3, 5, 7, 9, 13, 14, 17, 19, 21, 250, 283, 285, 287, 288, 290, 292, 295, 297, 299, 301, 303, 304, 511],
        ],
        'deform_texture_file': 'textures/deform/pb_leopard.png',
        'plane_texture_file': 'textures/plane/grey_tile.jpg',
        'rigid_texture_file': "textures/rigid/marble.png",
    },
    'cloth/tshirt_3.obj': {
        'deform_init_pos': [0, 3, 4],
        'deform_init_ori': [np.pi / 2, 0, 0],
        'deform_scale': 5,
        'deform_elastic_stiffness': 90,
        'deform_bending_stiffness': 0.1,
        'deform_damping_stiffness': 0.1,
        'deform_friction_coeff': 0.5,
        'cam_viewmat': [11.3, -28, 193.4, -0.08, 0.29, 1.80],
        'deform_anchor_vertices': [
            [292],
            [554],
        ],

        'deform_true_loop_vertices': [
            [0, 3, 5, 7, 9, 13, 14, 17, 19, 21, 250, 287, 289, 291, 292, 294, 296, 299, 301, 303, 305, 307, 308, 516],
        ],
        'plane_texture_file': 'textures/plane/white_brick.jpg',
        'rigid_texture_file': "textures/rigid/concrete.jpg",
        'deform_texture_file': 'textures/deform/pb_pink_fur.jpg',

    },
    'cloth/tshirt_4.obj': {
        'deform_init_pos': [0, 3, 4],
        'deform_init_ori': [np.pi / 2, 0, 0],
        'deform_scale': 5,
        'deform_elastic_stiffness': 90,
        'deform_bending_stiffness': 0.1,
        'deform_damping_stiffness': 0.1,
        'deform_friction_coeff': 0.5,
        'cam_viewmat': [11.3, -28, 193.4, -0.08, 0.29, 1.80],
        'deform_anchor_vertices': [
            [288],
            [259],
        ],

        'deform_true_loop_vertices': [
            [0, 3, 5, 7, 9, 13, 14, 17, 19, 21, 250, 283, 285, 287, 288, 290, 292, 295, 297, 299, 301, 303, 304, 512],
        ],
        'deform_texture_file': 'textures/deform/pb_white_knit.jpg',
        'plane_texture_file': 'textures/plane/blue_carpet.jpg',
        'rigid_texture_file': "textures/rigid/darkwood.jpg",

    },

    'cloth/mask_0.obj': {
        'deform_init_pos': [-0.2, 2, 6.2],
        'deform_init_ori': [np.pi / 2, 0, np.pi],
        'deform_scale': 1.3,
        'deform_elastic_stiffness': 100,
        # 'deform_bending_stiffness': 5,
        'deform_bending_stiffness': 1,
        'deform_damping_stiffness': 0.1,
        'deform_friction_coeff': 2,
        'deform_anchor_vertices': [
            [356],
            [269],

        ],
        'deform_true_loop_vertices': [
            [117, 200, 215, 217, 268, 270, 272, 274, 276, 278, 280, 282, 284,
             286, 287, 293, 294, 295, 297, 298, 299,
             301, 303, 305, 307, 309, 311, 313, 319, 320, 321, 400],
            [0, 232, 233, 337, 338, 339, 341, 343, 345, 347, 348, 350, 353, 354,
             357, 358, 360, 362, 364, 366, 369, 371,
             373, 375, 377, 379, 381, 383, 384, 385, 391, 393, 395, 396],
        ],
        'cam_viewmat': [3.80, -23.6, 177.4, -0.42, 0.06, 5.00],
        'deform_texture_file': 'textures/deform/pb_purple_fancy.jpg',
        'plane_texture_file': 'textures/plane/brown_yellow_carpet.jpg',
        'rigid_texture_file': "textures/rigid/red_leather.jpg",

    },
    'cloth/mask_1.obj': {
        'deform_init_pos': [-0.2, 2, 6.2],
        'deform_init_ori': [np.pi / 2, 0, np.pi],
        'deform_scale': 1.3,
        'deform_elastic_stiffness': 100,
        # 'deform_bending_stiffness': 5,
        'deform_bending_stiffness': 1,
        'deform_damping_stiffness': 0.1,
        'deform_friction_coeff': 2,
        'deform_anchor_vertices': [
            [394],
            [289],
        ],
        'deform_true_loop_vertices': [
            [117, 200, 215, 217, 268, 270, 272, 274, 276, 278, 280, 282, 284,
             286, 287, 293, 294, 295, 297, 298, 299,
             301, 303, 305, 307, 309, 311, 313, 319, 320, 321, 400],
            [0, 232, 233, 337, 338, 339, 341, 343, 345, 347, 348, 350, 353, 354,
             357, 358, 360, 362, 364, 366, 369, 371,
             373, 375, 377, 379, 381, 383, 384, 385, 391, 393, 395, 396],
        ],
        'cam_viewmat': [3.80, -23.6, 177.4, -0.42, 0.06, 5.00],
        'deform_texture_file': 'textures/deform/pb_leopard.png',
        'plane_texture_file': 'textures/plane/grey_tile.jpg',
        'rigid_texture_file': "textures/rigid/marble.png",
    },
    'cloth/mask_2.obj': {
        'deform_init_pos': [-0.2, 2, 6.2],
        'deform_init_ori': [np.pi / 2, 0, np.pi],
        'deform_scale': 1.3,
        'deform_elastic_stiffness': 100,
        # 'deform_bending_stiffness': 5,
        'deform_bending_stiffness': 1,
        'deform_damping_stiffness': 0.1,
        'deform_friction_coeff': 2,
        'deform_anchor_vertices': [
            [354],
            [288],
        ],
        'deform_true_loop_vertices': [
            [117, 199, 215, 217, 266, 272, 274, 282, 284, 295, 296, 301, 303,
             311],
            [0, 231, 232, 336, 337, 344, 346, 349, 352, 354, 357, 361, 368, 374,
             376, 378, 379, 382, 384, 395],
        ],
        'cam_viewmat': [3.80, -23.6, 177.4, -0.42, 0.06, 5.00],
        'plane_texture_file': 'textures/plane/cobblestone.jpg',
        'rigid_texture_file': "textures/rigid/brown_brick.jpg",
        'deform_texture_file': 'textures/deform/orange_pattern.png',
    },
    'cloth/mask_3.obj': {
        'deform_init_pos': [-0.2, 2, 6.2],
        'deform_init_ori': [np.pi / 2, 0, np.pi],
        'deform_scale': 1.3,
        'deform_elastic_stiffness': 100,
        # 'deform_bending_stiffness': 5,
        'deform_bending_stiffness': 1,
        'deform_damping_stiffness': 0.1,
        'deform_friction_coeff': 2,
        'deform_anchor_vertices': [
            [358],
            [289],
        ],
        'deform_true_loop_vertices': [
            [93, 99, 117, 119, 128, 190, 192, 198, 213, 215, 270, 278, 280, 281,
             282, 286, 299, 307, 309, 310, 311, 315],
            [0, 1, 3, 5, 30, 54, 81, 83, 152, 166, 233, 234, 268, 340, 348, 351,
             353, 365, 372, 374, 376, 380, 394, 396],
        ],
        'cam_viewmat': [3.80, -23.6, 177.4, -0.42, 0.06, 5.00],
        'plane_texture_file': 'textures/plane/grass.jpg',
        'rigid_texture_file': "textures/rigid/brown_brick.jpg",
        'deform_texture_file': 'textures/deform/pd_goldpattern.jpg',
    },
    'cloth/mask_4.obj': {
        'deform_init_pos': [-0.2, 2, 6.2],
        'deform_init_ori': [np.pi / 2, 0, np.pi],
        'deform_scale': 1.3,
        'deform_elastic_stiffness': 100,
        # 'deform_bending_stiffness': 5,
        'deform_bending_stiffness': 1,
        'deform_damping_stiffness': 0.1,
        'deform_friction_coeff': 2,
        'deform_anchor_vertices': [
            [360],
            [298],
        ],
        'deform_true_loop_vertices': [
            [93, 96, 98, 99, 123, 188, 197, 200, 219, 221, 275, 276, 277, 279,
             283, 289, 291, 293, 294, 298, 300, 303,
             304, 305, 306, 308, 312, 314, 318, 320, 323, 325, 327],
            [0, 3, 54, 56, 153, 234, 235, 236, 254, 269, 341, 343, 345, 347,
             349, 354, 357, 366, 368, 370, 373, 375,
             381, 393, 395, 398, 400],
        ],
        'cam_viewmat': [3.80, -23.6, 177.4, -0.42, 0.06, 5.00],
        'plane_texture_file': 'textures/plane/lightwood.jpg',
        'rigid_texture_file': "textures/rigid/brown_brick.jpg",
        'deform_texture_file': 'textures/deform/pb_whitered_checker.jpg',
    },
    'ropes/lasso3d_0.obj': {
        'deform_init_pos': [-3, 1, 6],
        'deform_init_ori': [-np.pi / 2, -np.pi, np.pi],
        'deform_scale': 5,
        'deform_elastic_stiffness': 100,
        'deform_bending_stiffness': 1,
        'deform_damping_stiffness': 0.1,
        'deform_friction_coeff': 0.5,
        'disable_self_collision': True,
        'deform_anchor_vertices': [
            [221],
            [131],
        ],

        'deform_true_loop_vertices': [
            [356, 358, 359, 381, 400, 401, 402, 403, 405, 406, 407, 409, 413,
             419, 424, 427, 428, 431, 436, 440, 453, 455, 458, 460, 468, 473,
             474, 475, 476, 480, 484, 487, 489, 495, 500, 506, 508, 511, 516,
             517, 520, 522, 524, 528, 533, 535, 536, 538, 549, 551, 560, 720,
             721, 724, 733, 736, 737, 738, 740, 749, 751, 753, 755, 756, 764,
             766, 771, 772, 774, 785, 787, 791, 799, 800, 802, 807, 813, 817,
             818, 820, 823, 824, 833, 835, 844, 852, 856, 861, 863, 864, 867,
             868, 871, 877, 878, 880, 881, 886, 892, 897],
        ],
        'cam_viewmat': [7, -15, 267, -0.08, 0.32, 4.5],
        'rigid_texture_file': "textures/rigid/red_leather.jpg",
        'plane_texture_file': 'textures/plane/white_marble.jpg',
        'deform_texture_file': 'textures/deform/pd_gold.jpg',
    },
    'ropes/lasso3d_0_fast.obj': {
        'deform_init_pos': [-3, 1, 6],
        'deform_init_ori': [-np.pi / 2, -np.pi, np.pi],
        'deform_scale': 5,
        'deform_elastic_stiffness': 100,
        'deform_bending_stiffness': 0.1,
        'deform_damping_stiffness': 0.1,
        'deform_friction_coeff': 0.5,
        'disable_self_collision': True,
        'max_episode_len': 250,
        'deform_anchor_vertices': [
            [82],
            [2],
        ],

        'deform_true_loop_vertices': [
            [180, 181, 204, 220, 222, 223, 224, 225, 229, 230, 233, 237, 240,
             241, 243, 245, 247, 249, 251, 255, 256, 265, 268, 271, 274, 276,
             279, 281, 283, 285, 286, 290, 292, 295, 297, 300, 306, 307, 309,
             310, 319, 339, 433, 442, 443, 445, 447, 454, 455, 458, 459, 460,
             461, 463, 467, 478, 479, 480, 482, 487, 488, 491, 495, 498, 499,
             503, 504, 506, 507, 514, 519, 520, 523, 527, 531, 539, 542, 543,
             547, 549, 554, 559, 561, 565, 566, 568, 569, 574, 575, 576, 578,
             579, 580, 581, 584, 590, 593, 594, 596, 601],
        ],
        'cam_viewmat': [5.6, -40, 271, -0.08, 0.33, 4.6],
        'rigid_texture_file': "textures/rigid/red_leather.jpg",
        'plane_texture_file': 'textures/plane/white_brick.jpg',
        'deform_texture_file': 'textures/deform/pd_gold.jpg',
    },
    'ropes/hoop3d_0.obj': {
        'deform_init_pos': [2, 3, 1],
        'deform_init_ori': [-np.pi / 2, -np.pi, np.pi],
        'deform_scale': 4,
        'deform_elastic_stiffness': 100,
        'deform_bending_stiffness': 10,
        'deform_damping_stiffness': 0.1,
        'cam_viewmat': [4.4, -45, 267, -0.03, 1.18, 3.2],
        'deform_anchor_vertices': [
            [397],
            [457],
        ],
        'deform_true_loop_vertices': [
            [6, 18, 30, 42, 54, 66, 78, 90, 102, 114, 126, 138, 150, 162, 174,
             186, 198, 210, 222, 234, 246, 258, 270,
             282, 294, 306, 318, 330, 342, 354, 366, 378, 390, 402, 414, 426,
             438, 450, 462, 474, 486, 498, 510, 522, 534, 546, 558, 570],
        ],
        'rigid_texture_file': "textures/rigid/lightwood.jpg",
        'plane_texture_file': 'textures/plane/blue_carpet.jpg',
        'deform_texture_file': 'textures/deform/pd_gold.jpg',
    },
    'cloth/button_cloth.obj': {
        'deform_init_pos': [0, 0.05, 2],  # [-0.13, 0.16, 0.21],
        'deform_init_ori': [np.pi, 0, 0],
        'deform_scale': 1,  # 0.5
        'deform_elastic_stiffness': 10,
        'deform_bending_stiffness': 10,
        'deform_anchor_vertices': [
            [0],
            [37],
        ],
        'deform_fixed_anchor_vertex_ids':
            [371, 372, 373, 374, 375, 376, 377, 378, 379, 380, 381, 382, 383, 384, 385, 386, 387, 388, 389],

        'deform_true_loop_vertices': [
            [79, 80, 81, 82, 97, 98, 114, 115, 133, 134, 135, 153],
            [53, 54, 55, 56, 73, 74, 91, 92, 107, 108, 109, 125],
        ],
        'cam_viewmat': [5, -8.8, 176.2, 1.4, 0.2, 1.65],
    },
    'proc_button_cloth': {
        'deform_init_pos': [0, 0.05, 2],  # [-0.13, 0.16, 0.21],
        'deform_init_ori': [np.pi, np.pi, 0],
        'anchor_init_pos': [-0.6, 3, 4],
        'other_anchor_init_pos': [-0.6, 3, 0.4],

        'deform_elastic_stiffness': 10,
        'deform_bending_stiffness': 10,
        'deform_fixed_anchor_vertex_ids':
            [0, 1, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34,
             36, 38, 40, 42, 44, 46, 48, 50, 52, 54,
             56, 58, 60, 62, 64, 66, 68, 70, 72, 74, 76, 78],

        'deform_true_loop_vertices': [
            [647, 648, 649, 650, 687, 688, 723, 724, 760, 762],
            [667, 668, 669, 670, 705, 706, 741, 742, 782, 784],
        ],
        'cam_viewmat': [5, -8.8, 176.2, 1.4, 0.2, 1.65],
        'plane_texture_file': 'textures/plane/grass.jpg',
        'rigid_texture_file': "textures/rigid/lightwood.jpg",
        'deform_texture_file': 'textures/deform/pb_white_knit.jpg',

    },
    'berkeley_garments': {
        'deform_init_pos': [0, 5, 8],
        'deform_init_ori': [np.pi / 2, 0, 0],
        'deform_scale': 5,
        'anchor_init_pos': [1, 4.4722, 10.4271],
        'other_anchor_init_pos': [-1, 4.4708, 10.4309],
        'deform_elastic_stiffness': 10.0,
        'deform_bending_stiffness': 0.05,
        'deform_damping_stiffness': 0.1,
        'cam_viewmat': [5, -9.8, 328, -0.44, 1.37, 8.7],
        'plane_texture_file': 'textures/plane/brown_yellow_carpet.jpg',
        'rigid_texture_file': "textures/rigid/lightwood.jpg",
        'deform_texture_file': 'textures/deform/pb_jeans.jpg',
    },
    'sewing_garments': {
        'deform_init_pos': [0, 5, 8],
        'deform_init_ori': [np.pi / 2, 0, 0],
        'deform_scale': 0.05,
        'anchor_init_pos': [1, 4.4722, 10.4271],
        'other_anchor_init_pos': [-1, 4.4708, 10.4309],
        'deform_elastic_stiffness': 10.0,
        'deform_bending_stiffness': 0.05,
        'deform_damping_stiffness': 0.1,
        'cam_viewmat': [5, -9.8, 328, -0.44, 1.37, 8.7],
        'plane_texture_file': 'textures/plane/brown_yellow_carpet.jpg',
        'rigid_texture_file': "textures/rigid/lightwood.jpg",
        'deform_texture_file': 'textures/deform/pb_jeans.jpg',
    },
    'ycb/015_peach/google_16k/08194_sparse_textured_ok.obj': {
        'deform_init_pos': [1.0, 3.4, 0.6],
        'deform_init_ori': [-np.pi / 2, -np.pi, np.pi],
        'deform_scale': 12.0,
        'deform_elastic_stiffness': 10.0,
        'deform_bending_stiffness': 10.0,
        'deform_damping_stiffness': 1.0,
        'cam_viewmat': [4.4, -45, 267, -0.03, 1.18, 3.2],
        'deform_anchor_vertices': [
            [397],
            [457],
        ],
        'rigid_texture_file': "textures/rigid/lightwood.jpg",
        'plane_texture_file': 'textures/plane/blue_carpet.jpg',
        'deform_texture_file': 'ycb/015_peach/google_16k/texture_map.png',
    },
    'ycb/014_lemon/google_16k/08194_sparse_textured_ok.obj': {
        'deform_init_pos': [1.0, 3.5, 0.3],
        'deform_init_ori': [-np.pi / 2, -np.pi, np.pi],
        'deform_scale': 13.0,
        'deform_elastic_stiffness': 10.0,
        'deform_bending_stiffness': 10.0,
        'deform_damping_stiffness': 1.0,
        'cam_viewmat': [4.4, -45, 267, -0.03, 1.18, 3.2],
        'deform_anchor_vertices': [
            [397],
            [457],
        ],
        'rigid_texture_file': "textures/rigid/lightwood.jpg",

        'plane_texture_file': 'textures/plane/blue_carpet.jpg',

        'deform_texture_file': 'ycb/014_lemon/google_16k/texture_map.png',
    },
    'ycb/018_plum/google_16k/08194_sparse_textured_ok.obj': {
        'deform_init_pos': [1.0, 3.5, 1.0],
        'deform_init_ori': [-np.pi / 2, -np.pi, np.pi],
        'deform_scale': 10.0,
        'deform_elastic_stiffness': 10.0,
        'deform_bending_stiffness': 10.0,
        'deform_damping_stiffness': 1.0,
        'cam_viewmat': [4.4, -45, 267, -0.03, 1.18, 3.2],
        'deform_anchor_vertices': [
            [397],
            [457],
        ],
        'rigid_texture_file': "textures/rigid/lightwood.jpg",
        'plane_texture_file': 'textures/plane/blue_carpet.jpg',
        'deform_texture_file': 'ycb/018_plum/google_16k/texture_map.png',
    },
}

# Default camera values: [distance, pitch, yaw, posX, posY, posZ]
DEFAULT_CAM = [11.4, -22.4, 257, -0.08, -0.29, 1.8]

# Info for camera rendering without debug visualizer.
# projectionMatrix is output 3 from pybullet.getDebugVisualizerCamera()
DEFAULT_CAM_PROJECTION = {
    # Camera info for {cameraDistance: 11.0, cameraYaw: 140,
    # cameraPitch: -40, cameraTargetPosition: array([0., 0., 0.])}
    'projectionMatrix': (1.0, 0.0, 0.0, 0.0,
                         0.0, 1.0, 0.0, 0.0,
                         0.0, 0.0, -1.0000200271606445, -1.0,
                         0.0, 0.0, -0.02000020071864128, 0.0)
}

ROBOT_INFO = {
    'franka2': {
        'file_name': 'franka/franka_dual.urdf',
        'ee_joint_name': 'panda_joint7_r',
        'ee_link_name': 'panda_hand_r',
        'left_ee_joint_name': 'panda_joint7_l',
        'left_ee_link_name': 'panda_hand_l',
        'global_scaling': 10.0,
        'use_fixed_base': True,
        'base_pos': np.array([5.0, 1.5, 0]),
        'rest_arm_qpos': np.array(
            [-0.7332, -0.0135, 0.1112, -0.718, 0.0978, 1.99, -0.5592]),
        'left_rest_arm_qpos': np.array(
            [0.7732, -0.0135, -0.0212, -0.68, 0.0978, 1.99, -0.5592]),
    },
    'franka1': {
        'file_name': 'franka/franka_small_fingers.urdf',
        'ee_joint_name': 'panda_joint7',
        'ee_link_name': 'panda_hand',
        'global_scaling': 10.0,
        'use_fixed_base': True,
        'base_pos': np.array([5.0, 1.5, 0]),
        'rest_arm_qpos': np.array(
            # for [2.5, 1.5, 1.0]
            [0.4083, 0.4691, -0.6216, -2.9606, -0.9926, 3.4903, 1.5129]
        ),
    }
}
