from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import pymysql
import datetime


HOST = 'localhost'
PORT = 8008


db = pymysql.connect(host="localhost", user="root",
                     password="admin123", database="nike")


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('content-length', 0))
        body = self.rfile.read(content_length)

        self.response(body)

        jsondata = json.loads(body)

        cur = db.cursor()

        for x in jsondata:
            cur.execute('INSERT INTO orders (name, quantity, datetime) VALUES (%s, %s, %s)',
                        (x['name'], x['quantity'], datetime.datetime.now()))

        db.commit()

    def response(self, content):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(content)

        print(self.headers)
        print("Received: "+str(json.loads(content))+"\n")


print('Listening on http://{}:{}...\n'.format(HOST, PORT))

httpd = HTTPServer((HOST, PORT), handler)
httpd.serve_forever()
