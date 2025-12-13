sudo ip addr add 169.254.169.254/32 dev lo
sudo ip addr add 10.10.0.10/32 dev lo
sudo ip addr add 10.10.0.11/32 dev lo
sudo ip link set lo up
