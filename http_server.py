__author__ = 'dan bordeanu'


import threading
import urlparse
import BaseHTTPServer
import sys
import optparse
from helpers import logger_settings
from os import curdir, sep


class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        """

        :rtype : object
        """
        url = urlparse.urlparse(self.path)
        assert isinstance(url.query, object)
        query = urlparse.parse_qs(url.query)
        response = ''

        if url.path == '/login-web/query':
            if not query.has_key('username'):
                self.send_error(400)
                return
            logger_settings.logger.info('%s Request for %s', self.server.name(), query['username'][0])
            response = 'User name %s\n' % query['username']
            self.send_response(200)
            self.end_headers()

        elif url.path.startswith('/login-web/'):
            username = url.path.split("/", 2)[2]
            logger_settings.logger.info("%s: Result for %s", self.server.name(), username)
            response = 'user nanme:%s\n' %username
            self.send_response(200)
            self.end_headers()

        elif url.path.endswith('.html'):
            file_open = open(curdir + sep + self.path)
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(file_open.read())
            file_open.close()

        else:
            logger_settings.logger.info('%s: invalid GET:%s', self.server.name(), url.path)
            self.send_error(501)
            return
        self.send_header('Content-lenght', len(response))
        self.send_header('Content-Type', 'text/html')
        self.end_headers()

        if response:
            self.wfile.write(response)
            self.wfile.flush()
            return


class HTTPServer(BaseHTTPServer.HTTPServer, threading.Thread):
    def __init__(self, name, port):
        """

        :rtype : object
        """
        BaseHTTPServer.HTTPServer.__init__(self, ('127.0.0.1', port), RequestHandler)

        threading.Thread.__init__(self)
        assert isinstance(name, object)
        self.service_name = name
        assert isinstance(port, object)
        self.service_port = port

    def name(self):
        return self.service_name

    def run(self):
        logger_settings.logger.info("%s: listening on port %d", self.service_name, self.service_port)
        self.serve_forever()
        logger_settings.logger.info("%s: stopped", self.service_name)

    def stop(self):
        self.shutdown()


if __name__ == '__main__':

    parser = optparse.OptionParser()
    parser.add_option('--http-port', dest='http_port', type='int',  default=8000, help='local HTTP server listen port')
    (opts, args) = parser.parse_args()
    if args:
        logger_settings.logger.info('no args')
        parser.error("no arguments allowed")
        sys.exit(1)
    try:
        httpd = HTTPServer('http', opts.http_port)
        httpd.start()
    except KeyboardInterrupt:
        httpd.stop()
        httpd.join()

    logger_settings.logger.info('Done')
    sys.exit(0)