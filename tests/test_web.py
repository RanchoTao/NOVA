import http.client
import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from nova.engine import NovaEngine
from nova.webapp import make_handler


class TestWeb(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(NovaEngine()))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def request(self, method, path, data=None, headers=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=5)
        conn.request(method, path, body=data, headers=headers or {})
        resp = conn.getresponse()
        body = resp.read()
        code = resp.status
        conn.close()
        return code, body

    def test_health_and_html(self):
        code, body = self.request("GET", "/api/health")
        self.assertEqual(code, 200)
        self.assertEqual(json.loads(body)["mode"], "template-demo")
        code, body = self.request("GET", "/")
        self.assertEqual(code, 200)
        self.assertIn("震撼首发", body.decode())

    def test_roll_and_origin_protection(self):
        headers = {"Content-Type": "application/json"}
        code, body = self.request("POST", "/api/roll", json.dumps({"count": 2, "seed": 3}), headers)
        self.assertEqual(code, 200)
        self.assertEqual(len(json.loads(body)["ideas"]), 2)
        code, body = self.request("POST", "/api/roll", '{"count":9}', headers)
        self.assertEqual(code, 400)
        code, body = self.request("POST", "/api/roll", '{}', {**headers, "Origin": "https://example.com"})
        self.assertEqual(code, 403)
        code, body = self.request("POST", "/api/roll", '{}', {"Content-Type": "text/plain"})
        self.assertEqual(code, 415)


if __name__ == "__main__":
    unittest.main()
