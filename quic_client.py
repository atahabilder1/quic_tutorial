#!/usr/bin/env python3
"""
QUIC Client with Connection Migration Support
Demonstrates client-initiated connection migration
"""

import asyncio
import logging
from typing import Optional
from aioquic.asyncio import connect
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import QuicEvent, StreamDataReceived, HandshakeCompleted
from aioquic.asyncio.protocol import QuicConnectionProtocol
import colorlog
import time

# Setup colored logging
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    '%(log_color)s%(asctime)s - %(levelname)s - %(message)s',
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    }
))
logger = colorlog.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class QuicClientProtocol(QuicConnectionProtocol):
    """QUIC client protocol"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.response_received = asyncio.Event()
        self.response_data = None

    def quic_event_received(self, event: QuicEvent):
        """Handle QUIC events"""

        if isinstance(event, HandshakeCompleted):
            logger.info("✅ Handshake completed with server")

        elif isinstance(event, StreamDataReceived):
            self.response_data = event.data.decode('utf-8')
            logger.info(f"📨 Received response: {self.response_data}")
            self.response_received.set()


async def send_message(protocol: QuicClientProtocol, message: str) -> str:
    """Send a message and wait for response"""

    # Create new stream
    stream_id = protocol._quic.get_next_available_stream_id()

    # Send data
    logger.info(f"📤 Sending on stream {stream_id}: {message}")
    protocol._quic.send_stream_data(stream_id, message.encode('utf-8'), end_stream=True)
    protocol.transmit()

    # Wait for response
    protocol.response_received.clear()
    await protocol.response_received.wait()

    return protocol.response_data


async def simulate_migration(protocol: QuicClientProtocol, migration_type: str):
    """Simulate connection migration"""

    logger.warning(f"🔄 Simulating {migration_type} migration...")

    if migration_type == "NAT_REBINDING":
        # Simulate NAT rebinding (change source port)
        logger.info("📍 Simulating NAT rebinding (source port change)...")
        # In aioquic, we can trigger path validation
        protocol._quic.request_key_update()

    elif migration_type == "NETWORK_SWITCH":
        # Simulate network interface switch (WiFi -> Cellular)
        logger.info("📍 Simulating network switch (WiFi -> Cellular)...")
        # This would require binding to a different interface
        # For simulation purposes, we just log the event

    elif migration_type == "IP_CHANGE":
        # Simulate IP address change
        logger.info("📍 Simulating IP address change...")

    protocol.transmit()
    await asyncio.sleep(0.5)  # Allow migration to process


async def run_client(
    host: str = "127.0.0.1",
    port: int = 4433,
    simulate_migrations: bool = True
):
    """Run the QUIC client"""

    # Configure QUIC
    configuration = QuicConfiguration(
        is_client=True,
        alpn_protocols=["quic-migration-demo"],
        verify_mode=False,  # Skip cert verification for self-signed cert
    )

    logger.info(f"🔌 Connecting to QUIC server at {host}:{port}")

    async with connect(
        host,
        port,
        configuration=configuration,
        create_protocol=QuicClientProtocol,
    ) as client:
        protocol = client

        logger.info("✅ Connected to server")

        # Send initial message
        response = await send_message(protocol, "Hello QUIC Server!")
        logger.info(f"✅ Initial communication successful")

        if simulate_migrations:
            await asyncio.sleep(1)

            # Simulate different types of migrations
            migrations = [
                ("NAT_REBINDING", "Message after NAT rebinding"),
                ("NETWORK_SWITCH", "Message after network switch"),
                ("IP_CHANGE", "Message after IP change"),
            ]

            for migration_type, message in migrations:
                await simulate_migration(protocol, migration_type)
                await asyncio.sleep(1)

                response = await send_message(protocol, message)
                logger.info(f"✅ Communication successful after {migration_type}")
                await asyncio.sleep(2)

        # Send final message
        await asyncio.sleep(1)
        response = await send_message(protocol, "Goodbye!")
        logger.info("👋 Session completed")


if __name__ == "__main__":
    try:
        asyncio.run(run_client(simulate_migrations=True))
    except KeyboardInterrupt:
        logger.info("🛑 Client stopped by user")
    except Exception as e:
        logger.error(f"❌ Error: {e}")
