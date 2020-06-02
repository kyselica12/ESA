import importlib
import subprocess
import sys


def test_install_package(package):
    try:
        importlib.import_module(package)
        print(f'Package {package} installed')
    except:
        print(f'Package {package} is not installed -> Downloading:')
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f'Package {package} installed')


def import_packages():
    test_install_package('numpy')
    test_install_package('astropy')
    test_install_package('matplotlib')
    test_install_package('argparse')
    test_install_package('concurrent')
    test_install_package('scipy')
    test_install_package('dataclass')
