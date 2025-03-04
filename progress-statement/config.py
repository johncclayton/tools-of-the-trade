import configparser
import os


def get_config(file_name='config.ini'):
    config = configparser.ConfigParser()
    search_paths = [os.getcwd(), os.path.expanduser('~')]
    ini_path = None

    for path in search_paths:
        potential_path = os.path.join(path, file_name)
        if os.path.exists(potential_path):
            ini_path = potential_path
            config.read(ini_path)
            break

    if ini_path is None:
        config.add_section('paths')
        config.set('paths', 'input_dir', '.')
        config.set('paths', 'output_dir', '.')
    else:
        if not config.has_section('paths'):
            raise ValueError(f"Missing 'paths' section in configuration file '{ini_path}'.")

    if not config.has_option('paths', 'input_dir'):
        raise ValueError(f"Missing 'input_dir' option in 'paths' section of configuration file '{ini_path}'.")

    if not config.has_option('paths', 'output_dir'):
        raise ValueError(f"Missing 'output_dir' option in 'paths' section of configuration file '{ini_path}'.")

    return config
