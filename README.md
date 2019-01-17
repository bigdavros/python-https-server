#Python HTTPS SimpleHTTPServer

##https extension of python -m SimpleHTTPServer

When creating XSS POC's I found that most websites would throw an error at the user if there wasn't a valid SSL certificate, which made the 
screenshots look bad because there would be an error in the URL bar showing the page was insecure.

This server uses an SSL certificate to create an SSL wrapper for the SimpleHTTPRequestHandler to do the same job as python -m SimpleHTTPServer
but with SSL to get around these errors. Whilst I was working on it I also added some argument handling so you could specify other 
certificates, ports, or hostnames and ips as required.

As it is just a wrapper for SimpleHTTPRequestHandler this shouldn't be used as a production server, just for demo's of POCs for short
durations, exactly in the same way you might use python -m SimpleHTTPServer.
