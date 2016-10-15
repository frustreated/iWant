import os, sys
import time_uuid
import ConfigParser
from watchdog.observers import Observer
from iwant.core.exception import MainException
from iwant.core.engine.consensus.beacon import CommonroomProtocol
from iwant.core.engine.server import backendFactory
from iwant.core.engine.monitor.watching import ScanFolder
from iwant.core.config import SERVER_DAEMON_HOST, SERVER_DAEMON_PORT, MCAST_IP, MCAST_PORT
from iwant.core.protocols import FilemonitorClientFactory, FilemonitorClientProtocol
from iwant.core.engine.monitor.callbacks import filechangeCB, fileindexedCB
from iwant.core.engine.identity.book import CommonlogBook
from twisted.internet import reactor, endpoints
from iwant.utils import get_ips, generate_id
from iwant.core.client import FrontendFactory, Frontend
from iwant.core.config import SERVER_DAEMON_HOST, SERVER_DAEMON_PORT
from iwant.core.constants import SEARCH_REQ, IWANT_PEER_FILE, INIT_FILE_REQ
import argparse

def get_paths():
    Config = ConfigParser.ConfigParser()
    conf_path = get_basepath()
    try:
        Config.read(os.path.join(conf_path,'.iwant.conf'))
        CONFIG_PATH = conf_path
        SHARING_FOLDER = Config.get('Paths', 'share')
        DOWNLOAD_FOLDER = Config.get('Paths', 'download')
    except:
        raise MainException(2)

    return (SHARING_FOLDER, DOWNLOAD_FOLDER, CONFIG_PATH)

def get_basepath():
    iwant_directory_path = os.path.expanduser('~')
    if sys.platform =='linux2' or sys.platform == 'linux' or sys.platform == 'darwin':
        iwant_directory_path = os.path.join(iwant_directory_path, '.iwant')
    elif sys.platform == 'win32':
        iwant_directory_path = os.path.join(os.getenv('APPDATA'),'.iwant')

    return iwant_directory_path

def main():
    ips = get_ips()
    for count, ip in enumerate(ips):
        print count+1, ip
    ip = input('Enter index of ip addr:')
    timeuuid = generate_id()
    book = CommonlogBook(identity=timeuuid, state=0, ip = ips[ip-1])  # creating shared memory between server and election daemon


    SHARING_FOLDER, DOWNLOAD_FOLDER, CONFIG_PATH = get_paths()
    if not os.path.exists(SHARING_FOLDER) or \
        not os.path.exists(DOWNLOAD_FOLDER) or \
            not os.path.exists(CONFIG_PATH):
        raise MainException(1)

    try:
        reactor.listenMulticast(MCAST_PORT, CommonroomProtocol(book), listenMultiple=True)  # spawning election daemon
        endpoints.serverFromString(reactor, 'tcp:{0}'.format(SERVER_DAEMON_PORT)).\
                listen(backendFactory(book, sharing_folder=SHARING_FOLDER,\
                download_folder=DOWNLOAD_FOLDER, config_folder= CONFIG_PATH))  # spawning server daemon
        ScanFolder(SHARING_FOLDER, filechangeCB, \
                fileindexedCB, CONFIG_PATH, bootstrap=True)  # spawning filemonitoring daemon and registering callbacks
        reactor.run()

    except KeyboardInterrupt:
        observer.stop()
        reactor.stop()
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)


def ui():
    parser = argparse.ArgumentParser(description='iwant')
    parser.add_argument("--search", help="instant fuzzy search", type=str)
    parser.add_argument("--download", help="download file by giving hash", type=str)
    args = parser.parse_args()

    if args.search:
        reactor.connectTCP(SERVER_DAEMON_HOST, SERVER_DAEMON_PORT, FrontendFactory(SEARCH_REQ, args.search))

    elif args.download:
        reactor.connectTCP(SERVER_DAEMON_HOST, SERVER_DAEMON_PORT, FrontendFactory(IWANT_PEER_FILE, args.download))#, DOWNLOAD_FOLDER))
    reactor.run()
