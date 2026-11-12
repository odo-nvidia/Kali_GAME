#!/usr/bin/env python3
"""Serve synthetic mission pages on the container loopback interface only."""

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer


class TrainingHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("X-Training-Mode", "offline")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'")
        super().end_headers()

    def log_message(self, format, *args):
        pass


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, choices=(8080, 8081), required=True)
    parser.add_argument("--directory", required=True)
    args = parser.parse_args()
    handler = partial(TrainingHandler, directory=args.directory)
    server = ThreadingHTTPServer(("127.0.0.1", args.port), handler)
    server.daemon_threads = True
    server.serve_forever()


if __name__ == "__main__":
    main()
