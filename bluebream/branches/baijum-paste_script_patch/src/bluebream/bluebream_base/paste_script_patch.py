import os
from paste.script import pluginlib
from paste.script.pluginlib import egg_name

def egg_info_dir(base_dir, dist_name):
    all = []
    for dir_extension in ['.'] + os.listdir(base_dir):
        full = os.path.join(base_dir, dir_extension,
                            egg_name(dist_name)+'.egg-info')
        all.append(full)
        if os.path.exists(full):
            return full
    return ''

pluginlib.egg_info_dir = egg_info_dir
