#!/usr/bin/env python3
"""Local preview server for the built site (serves dist/ on :8787)."""
import http.server
import os
import socketserver

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist")
os.chdir(ROOT)

PORT = 8787
Handler = http.server.SimpleHTTPRequestHandler
socketserver.ThreadingTCPServer.allow_reuse_address = True
socketserver.ThreadingTCPServer.daemon_threads = True
with socketserver.ThreadingTCPServer(("127.0.0.1", PORT), Handler) as httpd:
    print(f"Serving {ROOT} at http://127.0.0.1:{PORT}")
    httpd.serve_forever()
