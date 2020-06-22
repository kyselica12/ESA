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


PACKAGES = ['numpy', 'astropy','matplotlib', 'concurrent', 'scipy', 'json']

def import_packages():

    print('---------- Loading packages --------- \n')
    for p in PACKAGES:
        test_install_package(p)
    print()
