# Pytastic
This is program is intended to provide a Meshtastic-IP bridge using TUN. It expects a connected Meshtastic node on `/dev/ttyUSB0`.

# Setup
## Dependencies
`aiofiles` and `pyserial-asyncio`

## TUN device
Example setup:  
`ip tuntap add dev tun-tastic mode tun`
`ip addr add 192.168.124.1/24 dev tun-tastic`
`ip addr del <ipv6 address> dev tun-tastic`
`ip link set dev tun-static mtu 200`
`ip link set dev tun-tastic up`
