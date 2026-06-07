import fcntl
import random
import struct
import asyncio
import aiofiles.threadpool
import serial_asyncio
import meshtastic.mesh_pb2


# open_tun - open an async TUN file
def open_tun(name):
    tun = open("/dev/net/tun", "r+b", buffering=0)
    LINUX_IFF_TUN = 0x0001
    LINUX_IFF_NO_PI = 0x1000
    LINUX_TUNSETIFF = 0x400454CA
    flags = LINUX_IFF_TUN | LINUX_IFF_NO_PI
    ifs = struct.pack("16sH22s", bytes(name, encoding="ascii"), flags, b"")
    fcntl.ioctl(tun, LINUX_TUNSETIFF, ifs)
    return aiofiles.threadpool.wrap(tun)


# wakeup_packet - generate a wake up packet for the radio
def wakeup_packet():
    packet = meshtastic.mesh_pb2.ToRadio()
    packet.want_config_id = 1337
    return packet


# RadioTx - relay IP packets to the Mesh
class RadioTx():
    def __init__(self, tun, mesh_writer):
        self.tun = tun
        self.mesh_writer = mesh_writer
        self.packet_id = random.randint(0, 2**32 - 1)


    # clear_to_send - used to be clever throttling, but is dumb now
    async def clear_to_send(self):
        await asyncio.sleep(3)

    # tx_packets - endless loop of reading from TUN and writing to Mesh
    async def tx_packets(self):
        print("starting tx_packets")
        while True:
            print("waiting for IP!")
            header = await self.tun.read(20)
            total_length = struct.unpack(">H", header[2:4])[0]
            protocol = header[9]
            source_address = struct.unpack(">BBBB", header[12:16])
            destination_address = struct.unpack(">BBBB", header[16:20])
            print(header.hex())
            debug_payload = f"got ip packet: {source_address} -> {destination_address}, proto {protocol}, {total_length} bytes, packet id gonna be {self.packet_id}"
            print(debug_payload)
            if total_length > 200:
                print("packet too long, dropping")
            # heuristic to remove annoying packets that come up every time the device file is opened
            elif destination_address[0] == 224 and (destination_address[3] == 251 or destination_address[3] == 252):
                print("dropping mdns")
            else:
                rest = await self.tun.read(total_length - 20)
                await self.send_packet(header + rest)


    # send_packet - send a Meshtastic packet on primary channel 
    async def send_packet(self, payload):
        # just in case
        assert len(payload) <= 200

        await self.clear_to_send()

        # TODO: portnum should be 33 
        decoded = meshtastic.mesh_pb2.Data(portnum=1, payload=payload, want_response=True)
        mesh_packet = meshtastic.mesh_pb2.MeshPacket(to=(2**32 - 1), channel=0, id=self.packet_id, decoded=decoded)
        to_radio = meshtastic.mesh_pb2.ToRadio(packet=mesh_packet)
        print("sending ToRadio")
        print(to_radio)
        self.mesh_writer.write(b"\x94\xc3" + struct.pack(">H", to_radio.ByteSize()) + to_radio.SerializeToString())
        self.packet_id = (self.packet_id + 1) % 2**32
        await self.mesh_writer.drain()


# RadioRx - relay IP packets from the Mesh to TUN
class RadioRx():
    def __init__(self, tun, mesh_reader):
        self.tun = tun
        self.mesh_reader = mesh_reader


    # read_packet 
    async def read_packet(self):
        await self.mesh_reader.readuntil(b"\x94\xc3")
        length_bytes = await self.mesh_reader.readexactly(2)
        length = struct.unpack(">H", length_bytes)[0]
        data = await self.mesh_reader.readexactly(length)
        packet = meshtastic.mesh_pb2.FromRadio()
        packet.ParseFromString(data)

        return packet


    # rx_packets - endless loop of reading and handling Mesh packets
    async def rx_packets(self):
        print("starting rx_packets")
        while True:
            # there is a slight chance this explodes
            # because the node doesn't just output packet data
            # it also outputs regular ascii debug info
            # which may overflow the buffer at some point
            print("waiting for FromRadio!")
            packet = await self.read_packet()


async def main(loop):
    # init
    random.seed(None)
    mesh_reader, mesh_writer = await serial_asyncio.open_serial_connection(url="/dev/ttyUSB0", baudrate=115200)
    print("serial connection opened")
    tun = open_tun("tun-tastic")
    print("tun opened")
    
    # waking up
    packet = wakeup_packet()
    mesh_writer.write(b"\x94\xc3" + struct.pack(">H", packet.ByteSize()) + packet.SerializeToString())
    await mesh_writer.drain() 
    await asyncio.sleep(0.5)

    tx = RadioTx(tun, mesh_writer)
    rx = RadioRx(tun, mesh_reader)

    await asyncio.gather(rx.rx_packets(), tx.tx_packets())


loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
asyncio.run(main(loop))
