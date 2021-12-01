from gallocloud_utils.scheduling import schedule_in_thread
from gallocloud_utils.jsonlogging import configure_logger
from gallocloud_utils.config import load_config_from_env
import socketserver, http.server, sqlite3
from urllib.request import pathname2url

config = load_config_from_env()
logger = configure_logger(config.get('log', {}).get('level', 'info'))

def backup(raise_on_error=False):
    logger.info('Starting backup', extra={'action': 'backup', 'status': 'starting'})

    source_con = None
    target_con = None

    source = config.get('source', {}).get('path', '/backup/source.db')
    destination = config.get('target', {}).get('path', '/backup/target.db')

    try:
        source_con = sqlite3.connect('file:' + pathname2url(source) + '?mode=ro')
        target_con = sqlite3.connect(destination)
        source_con.backup(target_con)
        logger.info('Backup succeeded', extra={'action': 'backup', 'status': 'success'})
        source_con.close()
        target_con.close()
    except Exception as e:
        logger.exception('Backup failed', extra={'action': 'backup', 'status': 'failure'})

        if source_con:
            source_con.close()

        if target_con:
            target_con.close()

        if raise_on_error:
            raise e

def listen_trigger(port):
    class Handler(http.server.BaseHTTPRequestHandler):
        def trigger(self):
            try:
                backup(raise_on_error=True)
                self.send_response(200)
                self.end_headers()
            except Exception as inst:
                self.send_response(500)
                self.end_headers()

        def do_GET(self):
            if (self.path == '/favicon.ico'):
                return

            self.trigger()

        def do_POST(self):
            self.trigger()

        def do_PUT(self):
            self.trigger()

    httpd = socketserver.TCPServer(('', port), Handler)
    try:
       httpd.serve_forever()
    except KeyboardInterrupt:
       pass
    httpd.server_close()

if config.get('schedule'):
    logger.info('Configure schedule')
    schedule_in_thread(config['schedule'], backup, runAtBegin=True)

if config.get('trigger', {}).get('port'):
    logger.info('Configure trigger')
    listen_trigger(int(config['trigger']['port']))

# Use TaskManager to avoid collision ?

