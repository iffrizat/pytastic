# Pytastic
This program is intended to provide a Meshtastic-IP bridge using TUN. It expects a connected Meshtastic node on `/dev/ttyUSB0`.

# Setup
## Dependencies
`pyserial-asyncio`

## TUN device
Example setup:  
`ip tuntap add dev tun-tastic mode tun`  
`ip addr add 192.168.124.1/24 dev tun-tastic`  
`ip addr del <ipv6 address> dev tun-tastic`  
`ip link set dev tun-tastic mtu 200`  
`ip link set dev tun-tastic up`  
