# Pytastic
This program is intended to provide a Meshtastic-IP bridge using TUN. It expects a connected Meshtastic node on `/dev/ttyUSB0`.

## Setup
### Dependencies
`pyserial-asyncio`

### TUN device
Example setup:  
`ip tuntap add dev tun-tastic mode tun`  
`ip addr add 192.168.124.1/24 dev tun-tastic`  
`ip addr del <ipv6 address> dev tun-tastic`  
`ip link set dev tun-tastic mtu 200`  
`ip link set dev tun-tastic up`  

## Benchmark
Benchmarking was done on 2 nodes 0 hops away with Long Range - Moderate preset.  

```bash
$ ping 192.168.124.1 -c 4 -W 100
PING 192.168.124.1 (192.168.124.1) 56(84) bytes of data.
64 bytes from 192.168.124.1: icmp_seq=1 ttl=64 time=23593 ms
64 bytes from 192.168.124.1: icmp_seq=2 ttl=64 time=26945 ms
64 bytes from 192.168.124.1: icmp_seq=3 ttl=64 time=29835 ms
64 bytes from 192.168.124.1: icmp_seq=4 ttl=64 time=34567 ms

--- 192.168.124.1 ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3078ms
rtt min/avg/max/mdev = 23592.809/28734.868/34567.138/4027.135 ms, pipe 4
```

```bash
$ time curl -v --max-time 90000 --connect-timeout 90000 "http://192.168.124.1:8080/readme.md"
*   Trying 192.168.124.1:8080...
* Established connection to 192.168.124.1 (192.168.124.1 port 8080) from 192.168.124.2 port 32890 
* using HTTP/1.x
> GET /readme.md HTTP/1.1
> Host: 192.168.124.1:8080
> User-Agent: curl/8.20.0
> Accept: */*
> 
* Request completely sent off
* HTTP 1.0, assume close after body
< HTTP/1.0 200 OK
< Server: SimpleHTTP/0.6 Python/3.14.5
< Date: Mon, 08 Jun 2026 17:31:30 GMT
< Content-type: text/markdown
< Content-Length: 424
< Last-Modified: Sun, 07 Jun 2026 16:14:02 GMT
< 
# Pytastic
This program is intended to provide a Meshtastic-IP bridge using TUN. It expects a connected Meshtastic node on /dev/ttyUSB0.

# Setup
## Dependencies
pyserial-asyncio

## TUN device
Example setup:  
ip tuntap add dev tun-tastic mode tun  
ip addr add 192.168.124.1/24 dev tun-tastic  
ip addr del <ipv6 address> dev tun-tastic  
ip link set dev tun-tastic mtu 200  
ip link set dev tun-tastic up  
* shutting down connection #0

real 3m31.007s
user 0m0.025s
sys 0m0.015s
```
