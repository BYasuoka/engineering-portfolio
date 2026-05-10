import json
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from budget_backend import summarize_budget_inputs


ROOT = Path(__file__).resolve().parent


class PortfolioHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/api/budget-summary":
            self.send_error(HTTPStatus.NOT_FOUND, "Endpoint not found.")
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length)

        try:
            payload = json.loads(raw_body.decode("utf-8"))
            summary = summarize_budget_inputs(
                gross_income=float(payload.get("gross_income", 0)),
                state_code=str(payload.get("state_code", "")).upper(),
                pretax_401k_percent=float(payload.get("pretax_401k_percent", 0)),
            )
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            self.send_response(HTTPStatus.BAD_REQUEST)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(exc)}).encode("utf-8"))
            return

        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(summary).encode("utf-8"))


def main():
    server = ThreadingHTTPServer(("127.0.0.1", 8000), PortfolioHandler)
    print("Serving Portfolio at http://127.0.0.1:8000")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
