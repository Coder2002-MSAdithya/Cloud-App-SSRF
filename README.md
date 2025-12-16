# DNS Rebinding–Based SSRF: Host-Level Demonstration and Mitigation

This project demonstrates a **Server-Side Request Forgery (SSRF)** vulnerability caused by
**DNS rebinding**, and shows how enforcing **host-level egress controls** effectively
prevents the attack. The entire setup runs locally and does not rely on any cloud provider.

> **Repository note:**  
> The complete and working host-based demonstration and mitigation are implemented in the
> `main` branch. The `containers` branch contains an experimental and incomplete
> container-only approach.

---

## What is DNS Rebinding?

DNS rebinding is an attack technique where a single domain name resolves to different IP
addresses over time. An attacker-controlled DNS server can initially return a benign
public IP to pass validation checks and later return a private or link-local IP when the
actual network request is made.

In the context of SSRF, this creates a **time-of-check–to–time-of-use (TOCTOU)** flaw

The Python microservices are vulnerable to a DNS rebinding base SSRF because ssrf lib.py performs a single socket.gethostbyname()
validation during URL parsing but trusts the second DNS resolution performed by requests.get(),
allowing rebinding attacks to succeed, as a result of which sensitive metadata can be retrieved
despite validation (by sending request to the metadata IP).

---

## System Overview

The setup consists of:
- Three Python microservices that fetch user-supplied URLs
- A fake metadata service simulating a cloud Instance Metadata Service (IMDS)
- An attacker-controlled DNS domain used for rebinding
- Host-level egress filtering using `iptables`

Each microservice performs naive SSRF protection by resolving the hostname and checking the
IP against a blacklist.


## Step-by-Step Demonstration

### 1. Bind the Metadata IP (bind.sh)

To simulate IMDS locally, the metadata IP (`169.254.169.254`) is bound to the host network
interface using the provided script:

```bash
sudo ./bind.sh
```
### 2. Run the metadata service
Start the fake metadata service, which listens on 169.254.169.254:80
```bash
sudo python3 metadata_server.py
```
### 3. Run the Python apps
Start the three microservices in separate terminals:
```bash
python3 app1.py   # port 8081
python3 app2.py   # port 8082
python3 app3.py   # port 8083
```
Each service accepts a URL parameter and attempts to fetch it.```

### 4. Trigger the SSRF
To make DNS rebinding work on `rb.adithya-ms.co.in`, the parent zone `adithya-ms.co.in`
was configured to delegate this subdomain to a custom nameserver. An NS record for `rb.adithya-ms.co.in`
was added, pointing to ns1.adithya-ms.co.in. An A record mapped `ns1.adithya-ms.co.in`
to the VPS public IP running `rebinder_actual.py`, the Python nameserver code for this sub-
domain. All queries for rb.adithya-ms.co.in are now answered by this attacker-controlled
rebinding server.

Send a request using the attacker-controlled domain:
```bash
curl "http://localhost:8081/resize?url=http://rb.adithya-ms.co.in"
```
Due to DNS rebinding, the hostname may resolve to a public IP during validation and to the
metadata IP during the actual request, resulting in unauthorized access to metadata 
(need to try multiple times for successful attack).

### 5. A word about rebinder.py
Since my VPS has a limited validity of 1 month (expires 13th Jan 2026), rb.adithya-ms.co.in may NOT get resolved after that (rb subdomain zone has delegated to my VPS)
So, `rebinder.py` artificially resolves a domain name `rb.evil.com` randomly among a benign public IP and the internal metadata IP
To use `rebinder.py` for simulating DNS rebinding locally, you need to modify `/etc/resolv.conf` on an Ubuntu machine and use 127.0.0.1 as your primary nameserver. The server process in `rebinder.py` runs on port 53 as expected by DNS clients on the system
and also queries a public DNS if the domain name to be resolved is NOT `rb.evil.com`

### 5. Implement the egress filter using iptables
To prevent SSRF, outbound traffic is restricted at the host kernel level using `iptables`
```bash
sudo ./egress.sh
```
This script contains some `iptables` commands that restrict outbound traffic from the host, 
allows DNS and established connections but blocks all outbound access to
link-local and private IP ranges, including the metadata service.

After applying this mitigation, the SSRF attack fails consistently, even though DNS
rebinding may still occur.