import socket
from urllib.parse import urlparse


class SSRFProtection:
    """
    Library that:
    - Extracts hostname from URL
    - Resolves hostname to an IP address
    - Checks the *resolved IP* against a blacklist
    """

    def __init__(self, blocked_ips=None):
        """
        Args:
            blocked_ips (list): List of IPs to block
                               (default: ['169.254.169.254', '127.0.0.1'])
        """
        self.blocked_ips = blocked_ips or ['169.254.169.254', '127.0.0.1']
        print(f"[LIB] Initialized with blocked IPs: {self.blocked_ips}")

    def _resolve_hostname(self, hostname: str) -> str:
        """
        Resolve hostname to a single IPv4 address string.
        Returns None if resolution fails.
        """
        hostname = hostname.strip().lower()
        print(f"[LIB] Resolving hostname: {hostname}")
        try:
            ip = socket.gethostbyname(hostname)
            print(f"[LIB] Resolved {hostname} → {ip}")
            return ip
        except socket.gaierror as e:
            print(f"[LIB] DNS failed for {hostname}: {e}")
            return None

    def extract_and_validate_ip(self, hostname: str) -> bool:
        """
        Main validation logic:
        - Resolve hostname to IP
        - Check resolved IP against blacklist
        """
        hostname = hostname.strip().lower()
        print(f"[LIB] Validating hostname: {hostname}")

        resolved_ip = self._resolve_hostname(hostname)
        if resolved_ip is None:
            # Could choose to block or allow on DNS failure; here we block.
            print("[LIB] No IP resolved → blocking")
            return False

        # Single, normalized check against blacklist
        if resolved_ip in self.blocked_ips:
            print(f"[LIB] BLOCKED resolved IP: {resolved_ip}")
            return False

        print(f"[LIB] Resolved IP {resolved_ip} PASSED")
        return True

    def is_safe(self, url: str) -> bool:
        """
        Public API:
        - Parse URL
        - Extract hostname
        - Validate via resolved IP check
        """
        print(f"\n🚨 [LIB] Validating URL: {url}")
        parsed = urlparse(url)
        hostname = (parsed.hostname or '').strip()
        if not hostname:
            print("[LIB] No hostname in URL → blocking")
            return False

        return self.extract_and_validate_ip(hostname)