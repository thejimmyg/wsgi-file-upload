import cgi
import os
import sys
from wsgiref.simple_server import make_server

class FileUploadApp(object):
    def __init__(self, root):
        self.root = root

    def __call__(self, environ, start_response):
        if environ['REQUEST_METHOD'] == 'POST':
            post = cgi.FieldStorage(
                fp=environ['wsgi.input'],
                environ=environ,
                keep_blank_values=True
            )
            fileitem = post["userfile"]
            if fileitem.file:
                filename = fileitem.filename.decode('utf8').replace('\\','/').split('/')[-1].strip()
                if not filename:
                    raise Exception('No valid filename specified')
                file_path = os.path.join(self.root, filename)
                # Using with makes Python automatically close the file for you
                counter = 0
                with open(file_path, 'wb') as output_file:
                    # In practice, sending these messages doesn't work
                    # environ['wsgi.errors'].write('Receiving upload ...\n') 
                    # environ['wsgi.errors'].flush()
                    # print 'Receiving upload ...\n'
                    while 1:
                        data = fileitem.file.read(1024)
                        # End of file
                        if not data:
                            break
                        output_file.write(data)
                        counter += 1
                        if counter == 100:
                            counter = 0
                            # environ['wsgi.errors'].write('.') 
                            # environ['wsgi.errors'].flush()
                            # print '.',
            # Injection attack possible on the filename - should escape!
            body = u"File uploaded successfully to <tt>%s</tt>. Its filename is <tt>%s</tt>"%(
                filename, 
                cgi.escape(fileitem.filename),
            )
        else:
            body = u"""
<html>
<head><title>Upload</title></head>
<body>
<form name="test" method="post" action="" enctype="multipart/form-data">
File: <input type="file" name="userfile" />
      <input type="submit" name="submit" value="Submit" />
</form>
<p>Note: files with the same name with overwrite any existing files.</p>
</body>
</html>
"""
        start_response(
            '200 OK', 
            [
                ('Content-type', 'text/html; charset=utf8'),
                ('Content-Length', str(len(body))),
            ]
        )
        return [body.encode('utf8')]

def main():
    if len(sys.argv) != 3:
        print "Usage: python upload.py 8082 /tmp/upload"
        sys.exit(1)
    PORT = int(sys.argv[1])
    ROOT = sys.argv[2]
    httpd = make_server('', PORT, FileUploadApp(ROOT))
    print "Serving HTTP on port %s..."%(PORT)
    # Respond to requests until process is killed
    httpd.serve_forever()

if __name__ == '__main__':
    main()

