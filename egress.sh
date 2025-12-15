iptables -F OUTPUT
iptables -P OUTPUT ACCEPT
iptables -A OUTPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
iptables -A OUTPUT  -p udp --dport 53 -j ACCEPT
iptables -A OUTPUT  -p tcp --dport 53 -j ACCEPT
iptables -A FORWARD -p udp --dport 53 -j ACCEPT
iptables -A FORWARD -p tcp --dport 53 -j ACCEPT
iptables -A OUTPUT -d 169.254.0.0/16 -j REJECT
iptables -A FORWARD -d 169.254.0.0/16 -j REJECT
iptables -A OUTPUT -d 10.0.0.0/8 -j REJECT
iptables -A FORWARD -d 10.0.0.0/8 -j REJECT
iptables -A OUTPUT -d 172.16.0.0/12 -j REJECT
iptables -A FORWARD -d 172.16.0.0/16 -j REJECT
iptables -A OUTPUT -d 192.168.0.0/16 -j REJECT
iptables -A FORWARD -d 192.168.0.0/16 -j REJECT