#!/usr/bin/env python3
"""Local preview server for the built site (serves dist/ on :8787)."""
import http.server
import os
import socketserver

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist")

PORT = 8787


class Handler(http.server.SimpleHTTPRequestHandler):
    """Serve dist/ by path, not by chdir.

    build.py deletes and recreates dist/ on every run. A server that had chdir'd into the
    old directory keeps a handle on a deleted inode and answers every request with
    FileNotFoundError, so the preview silently dies the first time you rebuild while it is
    running. Passing the directory per request instead means one server survives any
    number of rebuilds.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)


socketserver.ThreadingTCPServer.allow_reuse_address = True
socketserver.ThreadingTCPServer.daemon_threads = True
with socketserver.ThreadingTCPServer(("127.0.0.1", PORT), Handler) as httpd:
    print(f"Serving {ROOT} at http://127.0.0.1:{PORT}")
    httpd.serve_forever()
