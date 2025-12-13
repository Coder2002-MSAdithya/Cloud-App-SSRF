# Default: allow established traffic
sudo iptables -A OUTPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# Block metadata / link-local
sudo iptables -A OUTPUT -d 169.254.0.0/16 -j REJECT

# Block RFC1918 private ranges
sudo iptables -A OUTPUT -d 10.0.0.0/8     -j REJECT
sudo iptables -A OUTPUT -d 172.16.0.0/12  -j REJECT
sudo iptables -A OUTPUT -d 192.168.0.0/16 -j REJECT

# Allow everything else (public IPv4)
sudo iptables -A OUTPUT -j ACCEPT