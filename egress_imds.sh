sudo iptables -A OUTPUT -d 169.254.0.0/16 -j LOG --log-prefix "EGRESS BLOCK 169.254: " --log-level 4
sudo iptables -A OUTPUT -d 169.254.0.0/16 -j REJECT --reject-with icmp-port-unreachable