# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Temescal - LG Soundbar communication library."""

import asyncio
import json
import logging
import struct
from typing import Any, Callable, Optional

from Crypto.Cipher import AES

_LOGGER = logging.getLogger(__name__)

# EQ modes
equalisers = [
    "Standard", "Bass", "Flat", "Boost", "Treble and Bass", "User",
    "Music", "Cinema", "Night", "News", "Voice", "ia_sound",
    "Adaptive Sound Control", "Movie", "Bass Blast", "Dolby Atmos",
    "DTS Virtual X", "Bass Boost Plus", "DTS:X"
]

STANDARD = 0
BASS = 1
FLAT = 2
BOOST = 3
TREBLE_BASS = 4
USER_EQ = 5
MUSIC = 6
CINEMA = 7
NIGHT = 8
NEWS = 9
VOICE = 10
IA_SOUND = 11
ASC = 12
MOVIE = 13
BASS_BLAST = 14
DOLBY_ATMOS = 15
DTS_VIRTUAL_X = 16
BASS_BOOST_PLUS = 17
DTS_X = 18

# Input functions/sources
functions = [
    "Wifi", "Bluetooth", "Portable", "Aux", "Optical", "CP", "HDMI",
    "ARC", "Spotify", "Optical2", "HDMI2", "HDMI3", "LG TV", "Mic",
    "Chromecast", "Optical/HDMI ARC", "LG Optical", "FM", "USB_old", "USB"
]

WIFI = 0
BLUETOOTH = 1
PORTABLE = 2
AUX = 3
OPTICAL = 4
CP = 5
HDMI = 6
ARC = 7
SPOTIFY = 8
OPTICAL_2 = 9
HDMI_2 = 10
HDMI_3 = 11
LG_TV = 12
MIC = 13
C4A = 14
OPTICAL_HDMIARC = 15
LG_OPTICAL = 16
FM = 17
USB_OLD = 18
USB = 19


class Temescal:
    """LG Soundbar communication client."""

    def __init__(
        self,
        address: str,
        port: int = 9741,
        callback: Optional[Callable] = None,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ):
        """Initialize the Temescal client."""
        self.iv = b'\'%^Ur7gy$~t+f)%@'
        self.key = b'T^&*J%^7tr~4^%^&I(o%^!jIJ__+a0 k'
        self.address = address
        self.port = port
        self.callback = callback
        self.loop = loop or asyncio.get_event_loop()
        self._reader: Optional[asyncio.StreamReader] = None
        self._writer: Optional[asyncio.StreamWriter] = None
        self._listen_task: Optional[asyncio.Task] = None

    async def connect(self) -> bool:
        """Connect to the soundbar."""
        try:
            self._reader, self._writer = await asyncio.open_connection(
                self.address, self.port
            )
            _LOGGER.debug("Connected to %s:%s", self.address, self.port)
            
            if self.callback is not None and self._listen_task is None:
                self._listen_task = self.loop.create_task(self._listen())
            
            return True
        except Exception as err:
            _LOGGER.error("Failed to connect to %s:%s: %s", self.address, self.port, err)
            return False

    async def disconnect(self):
        """Disconnect from the soundbar."""
        if self._listen_task:
            self._listen_task.cancel()
            self._listen_task = None
        
        if self._writer:
            self._writer.close()
            await self._writer.wait_closed()
            self._writer = None
            self._reader = None

    async def _listen(self):
        """Listen for responses from the soundbar."""
        while True:
            try:
                if not self._reader:
                    break
                
                data = await self._reader.readexactly(1)
                
                if data[0] == 0x10:
                    length_data = await self._reader.readexactly(4)
                    length = struct.unpack(">I", length_data)[0]
                    encrypted_data = await self._reader.readexactly(length)
                    response = self._decrypt_packet(encrypted_data)
                    
                    if response and self.callback:
                        self.callback(json.loads(response))
            except asyncio.CancelledError:
                break
            except Exception as err:
                _LOGGER.error("Error in listen loop: %s", err)
                await asyncio.sleep(1)
                try:
                    await self.connect()
                except Exception:
                    pass

    def _encrypt_packet(self, data: str) -> bytes:
        """Encrypt a packet for transmission."""
        padlen = 16 - (len(data) % 16)
        data = data + (chr(padlen) * padlen)
        data_bytes = data.encode('utf-8')
        
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        encrypted = cipher.encrypt(data_bytes)
        length = len(encrypted)
        prelude = bytearray([0x10, 0x00, 0x00, 0x00, length])
        
        return bytes(prelude) + encrypted

    def _decrypt_packet(self, data: bytes) -> str:
        """Decrypt a packet from the soundbar."""
        try:
            cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
            decrypted = cipher.decrypt(data)
            padding = decrypted[-1]
            decrypted = decrypted[:-padding]
            return decrypted.decode('utf-8')
        except Exception as err:
            _LOGGER.error("Failed to decrypt packet: %s", err)
            return ""

    async def send_packet(self, data: dict[str, Any]):
        """Send a packet to the soundbar."""
        if not self._writer:
            if not await self.connect():
                return
        
        try:
            packet = self._encrypt_packet(json.dumps(data))
            self._writer.write(packet)
            await self._writer.drain()
        except Exception as err:
            _LOGGER.error("Failed to send packet: %s", err)
            # Try to reconnect
            try:
                await self.connect()
                packet = self._encrypt_packet(json.dumps(data))
                self._writer.write(packet)
                await self._writer.drain()
            except Exception:
                pass

    # Get methods
    async def get_eq(self):
        """Get equalizer information."""
        data = {"cmd": "get", "msg": "EQ_VIEW_INFO"}
        await self.send_packet(data)

    async def set_eq(self, eq: int):
        """Set equalizer mode."""
        data = {"cmd": "set", "data": {"i_curr_eq": eq}, "msg": "EQ_VIEW_INFO"}
        await self.send_packet(data)

    async def get_info(self):
        """Get speaker information."""
        data = {"cmd": "get", "msg": "SPK_LIST_VIEW_INFO"}
        await self.send_packet(data)

    async def get_func(self):
        """Get function/source information."""
        data = {"cmd": "get", "msg": "FUNC_VIEW_INFO"}
        await self.send_packet(data)

    async def get_settings(self):
        """Get settings information."""
        data = {"cmd": "get", "msg": "SETTING_VIEW_INFO"}
        await self.send_packet(data)

    async def get_product_info(self):
        """Get product information."""
        data = {"cmd": "get", "msg": "PRODUCT_INFO"}
        await self.send_packet(data)

    # Set methods
    async def set_func(self, value: int):
        """Set input function/source."""
        data = {"cmd": "set", "data": {"i_curr_func": value}, "msg": "FUNC_VIEW_INFO"}
        await self.send_packet(data)

    async def set_volume(self, value: int):
        """Set volume level."""
        data = {"cmd": "set", "data": {"i_vol": value}, "msg": "SPK_LIST_VIEW_INFO"}
        await self.send_packet(data)

    async def set_mute(self, enable: bool):
        """Set mute state."""
        data = {"cmd": "set", "data": {"b_mute": enable}, "msg": "SPK_LIST_VIEW_INFO"}
        await self.send_packet(data)

    async def set_night_mode(self, enable: bool):
        """Set night mode."""
        data = {"cmd": "set", "data": {"b_night_mode": enable}, "msg": "SETTING_VIEW_INFO"}
        await self.send_packet(data)

    async def set_woofer_level(self, value: int):
        """Set woofer level."""
        data = {"cmd": "set", "data": {"i_woofer_level": value}, "msg": "SETTING_VIEW_INFO"}
        await self.send_packet(data)
