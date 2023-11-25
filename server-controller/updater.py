import sys
import os
import logging
import shutil
from file_exceptions import *
from config_loader import setYaml

logger = logging.getLogger('logs')
logger.setLevel(logging.INFO)

def updateYaml():
    port = input('Enter port for TCP server: ')
    startcommand = input('Enter the start command to run the server: ')
    setYaml(port, startcommand)

def updateFiles(dst):
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    dst = os.path.join(ROOT_DIR, dst)
    if not os.path.exists(dst):
        os.makedirs(dst)
    shutil.copy('config_loader.py', os.path.join(dst, 'config_loader.py'))
    shutil.copy('controller.py', os.path.join(dst, 'controller.py'))
    shutil.copy('requirements.txt', os.path.join(dst, 'requirements.txt'))
    if not os.path.exists(dst + '/config.yaml'):
        updateYaml()
        shutil.copy('config.yaml', os.path.join(dst, 'config.yaml'))

def main():
    logger.info('Updating files to version in this folder')

    # Error checker
    directoryFlagIsPresent = False
    directoryIsPresent = False
    for i in range(len(sys.argv)):
        if sys.argv[i] == '-dir':
            directoryFlagIsPresent = True
            if len(sys.argv) > i + 1 and sys.argv[i+1][0] != '-':
                directoryIsPresent = True
    if not directoryFlagIsPresent:
        raise MissingDirArg()
    if not directoryIsPresent:
        raise NoPathException()
    
    # Run updater
    for i in range(len(sys.argv)):
        if sys.argv[i] == '-dir' and len(sys.argv) >= i+1:
            dst = sys.argv[i+1]
    if dst[:0] == '/' or dst[:0] == '\\':
        dst = dst[:-1]
    updateFiles(dst)
    logger.info('Update complete')

if __name__ == "__main__":
    main()