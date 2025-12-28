import os
import sys
from gennet.lib import menu
from gennet.lib import misc
from gennet.lib.ansi_colors import red, yellow


def read_env(env_key, needed=True):
    env_data = os.environ.get(env_key)
    if env_data:
        return env_data
    if needed:
        print(red(f'{env_key} is needed.'))
        sys.exit(1)
    else:
        print(yellow(f'{env_key} is not available.'))
    return


def run_menu():
    config_toml_path = read_env('TOML_PATH')
    outdir_path = read_env('OUTDIR_PATH')

    if config_toml_path and outdir_path:
        params = misc.read_toml(config_toml_path)
        menu_list = [
            'Generate by ovs-docker',
            'Generate by macvlan',
            'Exit',
        ]
        num = menu.choose_num(menu_list)
        if num == len(menu_list)-1:
            pass
        elif num == 0:
            from gennet.docker.ovs_docker import gen
            gen.generate_scripts(outdir_path, params)
        elif num == 1:
            from gennet.docker.macvlan import gen
            gen.generate_scripts(outdir_path, params)


if __name__ == '__main__':
    run_menu()
