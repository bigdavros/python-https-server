#!/usr/bin/env python3
from http.server import HTTPServer, SimpleHTTPRequestHandler, HTTPStatus
from argparse import RawTextHelpFormatter, ArgumentParser
import ssl,sys

'''
https extension of python -m SimpleHTTPServer

When creating XSS POC's I found that most websites would throw an error at the user if there wasn't a valid SSL certificate, which made the 
screenshots look bad because there would be an error in the URL bar showing the page was insecure.

This server uses an SSL certificate to create an SSL wrapper for the SimpleHTTPRequestHandler to do the same job as python -m SimpleHTTPServer
but with SSL to get around these errors. Whilst I was working on it I also added some argument handling so you could specify other 
certificates, ports, or hostnames and ips as required.

As it is just a wrapper for SimpleHTTPRequestHandler this shouldn't be used as a production server, just for demo's of POCs for short
durations, exactly in the same way you might use python -m SimpleHTTPServer.

@b1gdave

'''

#Defaults
ip = "0.0.0.0"
port = 443
cert = "cert.pem"
helpdesc = 'Simple HTTPS server in Python. Starts a server on '+ip+':'+str(port)+' using "'+cert+'" as the server certificate. Can bind to any port,\nip, or hostname available to the server. May require sudo/run as admin for protected ports (e.g. 80 or 443).\n\nTo create a new server certifcate use the command: openssl req -new -x509 -keyout '+cert+' -out '+cert+' -days 365 -nodes\n(requires openssl to be installed)\n\nNOT A REPLACEMENT FOR A PRODUCTION SERVER. Relies on python\'s SimpleHTTPRequestHandler which has limited checks.'

parser = ArgumentParser(description=helpdesc,formatter_class=RawTextHelpFormatter)
parser.add_argument('--host', dest='ip', help='ip addr or hostname to listen on (default: '+ip+')')
parser.add_argument('--port', dest='port', help='port to listen on (default: '+str(port)+')')
parser.add_argument('--cert', dest='cert', help='pem certificate to use (default: '+cert+')')
options = parser.parse_args()

#Overwrite defaults with options if specified
if options.ip :	ip = options.ip
if options.port : port = options.port
if options.cert : cert = options.cert

#Start the server
try:
	httpd = HTTPServer((str(ip),int(port)), SimpleHTTPRequestHandler)
	httpd.socket = ssl.wrap_socket (httpd.socket, certfile='./'+str(cert), server_side=True)
	print("Server started https://"+str(ip)+":"+str(port)+"/ ["+str(cert)+"]")
	httpd.serve_forever()
except KeyboardInterrupt as e:
	print("\nStopped https://"+str(ip)+":"+str(port)+"/ ["+str(cert)+"]") 
except Exception as error:
	e = str(error)
	print("Could not start server https://"+str(ip)+":"+str(port)+"/ ["+str(cert)+"]. For help try: "+str(sys.argv[0])+" -h\n\nWarnings:")
	if "[Errno 99]" in e:
		print("Cannot assign address: "+ip+" ("+e+")")
	if "[Errno 98] Address already in use" in e:
		print("Port "+str(port)+" is unavailable\n\t- Try lsof -nP | grep -E '^C.*PID|:443.*\(LISTEN\)' on linux or netstat -ano | find \":443\" | find \"LISTENING\" on windows and see what's locking the port.\n\t"+
		"- VMWare shared VM's are shared over 443 by default and VMWare binds to all addresses. Go to menu Edit -> Preferences -> Shared VMs and click on \"Disable Sharing\", \n\t  or change the port (may require sudo/administrator privs on VMWare and restart).")
	if "[SSL] PEM lib" in e:
		print("Check the permissions on file "+cert)
	if "[Errno 2]" in e:
		print("File cert.pem not found\n\t- Make sure you have a .pem file, use -h to see command to create a new one\n\t- Make sure .pem is readable to process running the server ("+e+")")	
	print(e)
