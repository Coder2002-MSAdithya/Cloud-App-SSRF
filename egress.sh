# 1) Flush existing OUTPUT rules
sudo iptables -F OUTPUT

# 2) Default policy: ACCEPT
sudo iptables -P OUTPUT ACCEPT

# 3) Allow replies for already-established connections
sudo iptables -A OUTPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT

# 4) Allow ONLY outbound DNS queries (UDP/TCP port 53)
sudo iptables -A OUTPUT -p udp --dport 53 -j ACCEPT
sudo iptables -A OUTPUT -p tcp --dport 53 -j ACCEPT

# 5) Block outbound traffic to metadata / private ranges, with logging

# 169.254.0.0/16 (metadata / link-local)
sudo iptables -A OUTPUT -d 169.254.0.0/16 -j LOG --log-prefix "EGRESS BLOCK 169.254: " --log-level 4
sudo iptables -A OUTPUT -d 169.254.0.0/16 -j REJECT --reject-with icmp-port-unreachable

# 10.0.0.0/8
sudo iptables -A OUTPUT -d 10.0.0.0/8 -j LOG --log-prefix "EGRESS BLOCK 10/8: " --log-level 4
sudo iptables -A OUTPUT -d 10.0.0.0/8 -j REJECT --reject-with icmp-port-unreachable

# 172.16.0.0/12
sudo iptables -A OUTPUT -d 172.16.0.0/12 -j LOG --log-prefix "EGRESS BLOCK 172.16/12: " --log-level 4
sudo iptables -A OUTPUT -d 172.16.0.0/12 -j REJECT --reject-with icmp-port-unreachable

# 192.168.0.0/16
sudo iptables -A OUTPUT -d 192.168.0.0/16 -j LOG --log-prefix "EGRESS BLOCK 192.168/16: " --log-level 4
sudo iptables -A OUTPUT -d 192.168.0.0/16 -j REJECT --reject-with icmp-port-unreachable
