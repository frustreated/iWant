from twisted.internet import reactor
from iwant.client import FrontendFactory, Frontend
from iwant.config import SERVER_DAEMON_HOST, SERVER_DAEMON_PORT
from iwant.constants.server_event_constants import SEARCH_REQ, IWANT_PEER_FILE
import sys

data = sys.argv[1]
#reactor.connectTCP(SERVER_DAEMON_HOST, SERVER_DAEMON_PORT, FrontendFactory(SEARCH_REQ, data))

reactor.connectTCP(SERVER_DAEMON_HOST, SERVER_DAEMON_PORT, FrontendFactory(IWANT_PEER_FILE, data))
reactor.run()