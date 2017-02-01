#!/usr/bin/env python
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib
from urlparse import urlparse
import ast

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((host, port))

        return clientSocket

    def get_code(self, data):
        headers = self.get_headers(data)
        code = headers[0].split(' ')[1] # first header will be http\1.1 code message
        return code

    def get_headers(self,data):
        headerBlob = data.split('\r\n\r\n')[0]
        print headerBlob
        headers = headerBlob.split('\r\n')
        return headers

    def get_body(self, data):
        body = data.split('\r\n\r\n')[1]
        return body

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return str(buffer)

    def parseURL(self, url):
        parsedURL = urlparse(url)
        hostname = parsedURL.hostname
        path = parsedURL.path
        port = parsedURL.port

        if (not hostname):
            url = "http://" + url
            parsedURL = urlparse(url)
            hostname = parsedURL.hostname
            path = parsedURL.path
            port = parsedURL.port

        if (not path):
            path = "/"

        if (not port):
            port = 80

        return [hostname, path, port]

    def createRequest(self, method, urlList, args=None):
        host = urlList[0]
        path = urlList[1]
        port = urlList[2]

        #print("Host: %s Path: %s Port: %s" % (host, path, port))

        statusLine = method + " " + path + " HTTP/1.1\r\n"
        headerHost = "Host: " + host + "\r\n"
        headerAccept = "Accept: */*\r\n"
        request = statusLine + headerHost + headerAccept

        body = ""
        if (method == "POST"):
            length = 0
            if (args):
                if (type(args) is str): #is args a string and not already a dictionary?
                    if (args.find('{') > -1): #is the string a dictionary?
                        try:
                            #Jacob Gabrielson, http://stackoverflow.com/questions/988228/convert-a-string-representation-of-a-dictionary-to-a-dictionary
                            args = ast.literal_eval(args)
                        except (ValueError, SyntaxError, TypeError):
                            print "String of dictionary is malformed."
                            args = None
                    elif (args.find('=') > -1): #is stringa list of params?
                        varList = re.split("&|;", args)
                        args = {}
                        for var in varList:
                            pair = var.split("=")
                            args[pair[0]] = pair[1]

                body = urllib.urlencode(args)
                length = len(body)
                
            headerContentLength = "Content-Length: " + str(length) + "\r\n"
            headerContentType = "Content-Type: application/x-www-form-urlencoded\r\n"
            request += headerContentLength + headerContentType

        close = "Connection: close\r\n"
        delimiterLine = "\r\n"
        request += close + delimiterLine + body

        #print request

        return request

    def GET(self, url, args=None):
        urlList = self.parseURL(url)
        host = urlList[0]
        path = urlList[1]
        port = urlList[2]

        request = self.createRequest("GET", urlList)

        socket = self.connect(host, port)
        socket.sendall(request)

        response = self.recvall(socket)

        code = self.get_code(response)
        body = self.get_body(response)

        print body
        return HTTPResponse(int(code), body)

    def POST(self, url, args=None):
        urlList = self.parseURL(url)
        host = urlList[0]
        path = urlList[1]
        port = urlList[2]

        request = self.createRequest("POST", urlList, args)

        socket = self.connect(host, port)
        socket.sendall(request)

        response = self.recvall(socket)

        code = self.get_code(response)
        body = self.get_body(response)

        print body
        return HTTPResponse(int(code), body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )

if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print client.command( sys.argv[2], sys.argv[1] )
    else:
        print client.command( sys.argv[2], sys.argv[1], sys.argv[3] )
