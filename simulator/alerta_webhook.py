
import json
from http.server import BaseHTTPRequestHandler, HTTPServer


class AlertHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        tamanho = int(self.headers.get("Content-Length", 0))
        corpo = self.rfile.read(tamanho)
        dados = json.loads(corpo)

        print("\nNOTIFICACAO GRAFANA RECEBIDA")
        print("Status:", dados.get("status"))

        for alerta in dados.get("alerts", []):
            loja = alerta.get("labels", {}).get("loja_id")
            print("Loja:", loja)
            print("Estado:", alerta.get("status"))

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")


print("Receptor de alertas na porta 8099")
HTTPServer(("0.0.0.0", 8099), AlertHandler).serve_forever()
