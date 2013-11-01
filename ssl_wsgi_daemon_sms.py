#!/usr/bin/env python

from wsgiref.simple_server import make_server
from cgi import parse_qs, escape
import _mysql
import os
import ssl
from wsgiref.simple_server import WSGIServer, WSGIRequestHandler
import sys, time
import logging
from pygsm import GsmModem
from daemon3 import Daemon

LOGFILE = '/var/log/daemonpython.log'

# Configure logging
logging.basicConfig(filename=LOGFILE,level=logging.DEBUG,format='%(asctime)s %(clientip)s %(user)s %(hostnam)-8s %(message)s')

s={'clientip': 'ip' , 'user': 'user', 'hostnam': 'user'}
            
class gsmmodule(object):
  def __init__(self, modem):
    self.modem = modem

  def sendsms(self,s,num,msg):
          self.modem.send_sms(num,msg)
          logging.debug('data sent on sms msg=%s num=%s',msg,num,extra=s)

class HTTPSMixIn:
    keypath  ="/home/test/sslserver/server.key"
    certpath ="/home/test/sslserver/server.crt"
    def set_credentials( self, keypath, certpath):
        self.keypath = keypath #it have to be ssl cert not tls ones
        self.certpath = certpath

    def finish_request(self, request, client_address):
        # Note: accessing self.* from here might not be thread-safe,
        # which could be an issue when using ThreadingMixIn.
        # In practice, the GIL probably prevents any trouble with read access.
        ssock = ssl.wrap_socket( request,
            keyfile=self.keypath, certfile=self.certpath, server_side=True)
        self.RequestHandlerClass(ssock, client_address, self)
        ssock.close()

class SecureWSGIServer(HTTPSMixIn, WSGIServer):
    pass

class SecureWSGIRequestHandler( WSGIRequestHandler):
    #xxx todo: set SSL_PROTOCOL, maybe others
    def get_environ( self):
        env = WSGIRequestHandler.get_environ( self)
        if isinstance( self.request, ssl.SSLSocket):
            env['HTTPS'] = 'on'
        return env

html = """
<html>
<body>
   <form method="get" action="ssl_wsgi_daemon_sms_server.wsgi">
      <p>
         Mesage: <input type="text" name="msg">
         </p>
         Numero: <input type="text" name="num">
         </p>
      <p>
         <input type="submit" value="Submit">
         </p>
      </form>
   <p>
      Mesage: %s<br>
      </p>
      %s
   </body>
</html>"""

def application(environ, start_response):
   # Returns a dictionary containing lists as values.
   #logging.debug('starting application',extra=s)
   d = parse_qs(environ['QUERY_STRING'])
   ip=environ['REMOTE_ADDR']
   user=environ['USER']
   hostnam=environ['REMOTE_ADDR']
   s={'clientip': ip ,'user': user, 'hostnam': hostnam}
   logging.debug('variables loded',extra=s)
   try:         
            logging.debug('starting the user',extra=s)
            # In this idiom you must issue a list containing a default value.
            msg = d.get('msg', [''])[0] # Returns the first msg value.
            num = d.get('num', [''])[0] # Returns a list of num.

            # Always escape user input to avoid script injection
            msg = escape(msg)
            num = escape(num)

            response_body = html % (msg or 'Empty',num or 'No num')
            logging.debug('user served',extra=s)
            if msg :
                     myDB = _mysql.connect(host="192.168.0.120",db="test",user="root",passwd="066abde")
                     myDB.query(" INSERT INTO test(name,ip,tel) VALUES ('%s','%s','%s') ;" % (msg,ip,num) )
                     myDB.close()
                     logging.debug('data sent succefly msg=%s num=%s',msg,num,extra=s)
                     app.sendsms(s,num,msg) 
            status = '200 OK'
   except Exception, e:
          logging.exception('Error ---------------',extra=s)

   # Now content type is text/html
   response_headers = [('Content-Type', 'text/html'),
                  ('Content-Length', str(len(response_body)))]
   start_response(status, response_headers)

   return [response_body]
   
class MyDaemon(Daemon):
        def run(self):
		try:
                            # Instantiate the WSGI server.
                            # It will receive the request, pass it to the application
                            # and send the application's response to the client
                            httpd = make_server(
                               '192.168.0.101', # The host name.
                               8090, # A port number where to wait for the request.
                               application, # Our application object name, in this case a function.
                               server_class=SecureWSGIServer, #up there ;)
                               handler_class=SecureWSGIRequestHandler #up there also
                               )
                            # Wait for request, serve it .
                            httpd.serve_forever()
                            logging.debug('srver started succefuly',extra=s)
		except Exception, e:
                            logging.exception('Error ------------- ',extra=s)

Daisy13_on_D1="/dev/ttyS1"
gsm = GsmModem(port=Daisy13_on_D1,baudrate=115200,logger=GsmModem.debug_logger).boot()
z = gsm.wait_for_network()
app = gsmmodule(gsm)
if __name__ == "__main__":
        daemon = MyDaemon('/tmp/daemon-example.pid')
        if len(sys.argv) == 2:
                if 'start' == sys.argv[1]:
                        #gsm.boot()
                        daemon.start()
                elif 'stop' == sys.argv[1]:
                        #app.sendsms(s,"0633466667","sms server stoping") #activate this to secure server
                        logging.debug('srver stoping',extra=s)
                        daemon.stop()
                elif 'restart' == sys.argv[1]:
                        gsm.boot()
                        app = gsmmodule(gsm)
                        daemon.restart()
                else:
                        print "Unknown command"
                        sys.exit(2)
                sys.exit(0)
        else:
                print "usage: %s start|stop|restart" % sys.argv[0]
                sys.exit(2)
