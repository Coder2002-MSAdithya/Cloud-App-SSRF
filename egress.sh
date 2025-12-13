#!/usr/bin/env bash

# 1) Flush existing OUTPUT rules
sudo iptables -F OUTPUT

# 2) Default policy: ACCEPT (we will explicitly REJECT what we care about)
sudo iptables -P OUTPUT ACCEPT

# 3) Allow replies for already-established connections
sudo iptables -A OUTPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT

# 4) Allow ONLY outbound DNS queries (UDP/TCP port 53) to any resolver
sudo iptables -A OUTPUT -p udp --dport 53 -j ACCEPT
sudo iptables -A OUTPUT -p tcp --dport 53 -j ACCEPT

# 5) Block outbound traffic to metadata / private ranges (any protocol/port)
sudo iptables -A OUTPUT -d 169.254.0.0/16 -j REJECT --reject-with icmp-port-unreachable
sudo iptables -A OUTPUT -d 10.0.0.0/8     -j REJECT --reject-with icmp-port-unreachable
sudo iptables -A OUTPUT -d 172.16.0.0/12  -j REJECT --reject-with icmp-port-unreachable
sudo iptables -A OUTPUT -d 192.168.0.0/16 -j REJECT --reject-with icmp-port-unreachable