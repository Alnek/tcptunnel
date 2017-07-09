#!/usr/bin/python

import wsgiref.handlers
from wsgiref.simple_server import make_server

import gzip
import StringIO

handlers = []

class Response(object):
    pass

def Register(handler):
    def wrapper(*args, **kwargs):
        return handler(*args, **kwargs)
    handlers.append(wrapper)
    return wrapper

def Method(*method):
    def exact_decorator(handler):
        def method_validator(*args, **kwargs):
            env = args[0]
            if env['REQUEST_METHOD'] in method:
                return handler(*args, **kwargs)
            else:
                return None

        return method_validator
    return exact_decorator

def Path(*path):
    def exact_decorator(handler):
        def path_validator(*args, **kwargs):
            env = args[0]
            if env['PATH_INFO'] in path:
                return handler(*args, **kwargs)
            else:
                return None

        return path_validator
    return exact_decorator
    
def Data(handler):
    def data_validator(*args, **kwargs):
        env = args[0]
        try:
            length = int(env.get('CONTENT_LENGTH', '0'))
        except ValueError:
            length = 0

        if length != 0:
            data = env['wsgi.input'].read(length)
            kwargs['data'] = data;
            return handler(*args, **kwargs)
        else:
            kwargs['data'] = None;
            return handler(*args, **kwargs)

    return data_validator
    
def Gzip(handler):
    def do_gzip(input_string):
        out = StringIO.StringIO()
        with gzip.GzipFile(fileobj=out, mode="w") as f:
            f.write(input_string)
        return out.getvalue()
        
    def gzipper(*args, **kwargs):
        response = handler(*args, **kwargs)
        response.headers.append(('Content-Encoding', 'gzip'));
        response.content = do_gzip(response.content)
        return response

    return gzipper

@Register
@Path('/echo')
@Method('POST')
@Data
def debug(environ, data):
    content = data

    response = Response()
    response.status = '200 OK'
    response.headers = [('Content-type','text/plain')]
    response.content = content
    return response
    
@Register
@Path('/env', '/test')
@Method('GET', 'POST')
@Data
@Gzip
def debug(environ, data):
    content = ''
    for k in environ:
        content += k + '=' + str(environ[k])+'\n'

    response_headers = [('Content-type','text/plain')]

    response = Response()
    response.status = '200 OK'
    response.headers = [('Content-type','text/plain')]
    response.content = content
    return response

def default(environ):
    response = Response()
    response.status = '400 Bad Request'
    response.headers = [('Content-type','text/plain')]
    response.content = 'Bad Request'
    return response

def find_handler(environ, start_response):
    for handler in handlers:
        response = handler(environ)
        if response != None:
            start_response(response.status, response.headers)
            return [response.content]

    response = default(environ)
    start_response(response.status, response.headers)
    return [response.content]

if __name__ == '__main__':
    port = 8080
    httpd = make_server('', port, find_handler)
    print "Serving on port %d..." % (port)
    httpd.serve_forever()
