#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler, HTTPStatus
from urllib.parse import urlparse, parse_qs
from argparse import RawTextHelpFormatter, ArgumentParser
import ssl, sys, socket

# Defaults
ip = "0.0.0.0"
port = 443
cert = "cert.pem"
helpdesc = 'Simple HTTPS server in Python that logs GET and POST variables.\nStarts a server on '+ip+':'+str(port)+' using "'+cert+'" as the server certificate. Can bind to any port,\nip, or hostname available to the server. May require sudo/run as admin for protected ports (e.g. 80 or 443).\n\nTo create a new server certifcate use the command: openssl req -new -x509 -keyout '+cert+' -out '+cert+' -days 365 -nodes\n(requires openssl to be installed)\n\nNOT A REPLACEMENT FOR A PRODUCTION SERVER.'

parser = ArgumentParser(description=helpdesc, formatter_class=RawTextHelpFormatter)
parser.add_argument('--host', dest='ip', help='ip addr or hostname to listen on (default: '+ip+')')
parser.add_argument('--port', dest='port', help='port to listen on (default: '+str(port)+')')
parser.add_argument('--cert', dest='cert', help='pem certificate to use (default: '+cert+')')
options = parser.parse_args()

# Overwrite defaults with options if specified
if options.ip: ip = options.ip
if options.port: port = options.port
if options.cert: cert = options.cert

# --- Custom Request Handler ---
class VariableLoggingHandler(BaseHTTPRequestHandler):
    def _send_response(self, text):
        """Helper to send a basic HTTP 200 response back to the client."""
        self.send_response(HTTPStatus.OK)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(text.encode('utf-8'))

    def do_GET(self):
        print(f"\n--- GET Request from {self.client_address[0]} ---")
        parsed_path = urlparse(self.path)
        print(f"Path: {parsed_path.path}")
        
        # Parse and print GET variables
        get_vars = parse_qs(parsed_path.query)
        if get_vars:
            print("GET Variables:")
            for key, values in get_vars.items():
                print(f"  {key}: {values}")
        else:
            print("No GET variables found.")
            
        self._send_response("GET request logged.\n")

    def do_POST(self):
        print(f"\n--- POST Request from {self.client_address[0]} ---")
        parsed_path = urlparse(self.path)
        print(f"Path: {parsed_path.path}")
        
        # Check for GET variables embedded in the POST URL
        get_vars = parse_qs(parsed_path.query)
        if get_vars:
            print("GET Variables (in URL):")
            for key, values in get_vars.items():
                print(f"  {key}: {values}")

        # Parse and print POST variables
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 0:
            post_data = self.rfile.read(content_length).decode('utf-8')
            print("POST Body:")
            
            # Attempt to parse as standard URL-encoded form data
            post_vars = parse_qs(post_data)
            if post_vars:
                print("Parsed POST Variables:")
                for key, values in post_vars.items():
                    print(f"  {key}: {values}")
            else:
                # If it's JSON, raw text, or multipart, just print the raw body
                print(f"  Raw Data: {post_data}")
        else:
            print("No POST body found.")
            
        self._send_response("POST request logged.\n")


# Start the server
try:
    # 1. Create the modern SSL context for a server
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

    # 2. Load your certificate (this works exactly like the old certfile argument)
    context.load_cert_chain(certfile='./'+str(cert))

    # 3. Set up your server using the custom logging handler
    httpd = HTTPServer((str(ip), int(port)), VariableLoggingHandler)

    # 4. Wrap the socket using the context instead of the old ssl module method
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

    print("Server started https://"+str(ip)+":"+str(port)+"/ ["+str(cert)+"]")
    print("Listening for incoming GET and POST requests...")
    httpd.serve_forever()

except KeyboardInterrupt:
    print("\nStopped https://"+str(ip)+":"+str(port)+"/ ["+str(cert)+"]") 
except Exception as error:
    e = str(error)
    print("Could not start server https://"+str(ip)+":"+str(port)+"/ ["+str(cert)+"]. For help try: "+str(sys.argv[0])+" -h\n\nWarnings:")
    if "[Errno 99]" in e:
        print("Cannot assign address: "+ip+" ("+e+")")
    if "[Errno 98] Address already in use" in e:
        print("Port "+str(port)+" is unavailable\n\t") 
    if "[SSL] PEM lib" in e:
        print("Check the permissions on file "+cert)
    if "[Errno 2]" in e:
        print("File cert.pem not found\n\t- Make sure you have a .pem file, use -h to see command to create a new one\n\t- Make sure .pem is readable to process running the server ("+e+")")    
    print(e)