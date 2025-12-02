# QUIC Protocol Connection Migration Simulator

A comprehensive simulation environment for understanding QUIC connection migration. This project demonstrates how QUIC maintains connections even when network paths change (IP addresses, ports, or interfaces).

## What is QUIC Connection Migration?

Unlike TCP which identifies connections by the 4-tuple (source IP, source port, destination IP, destination port), QUIC uses **Connection IDs**. This allows connections to survive network changes such as:

- WiFi to cellular handoffs
- NAT rebinding (port changes)
- IP address changes
- Network interface switches

## Do You Need Docker?

**Short answer: No, Docker is not required.**

You can run this simulation directly on your local machine. However, Docker can be useful if you want to:

1. **Simulate network conditions** (latency, packet loss)
2. **Test with network namespaces** (true IP isolation)
3. **Avoid dependency conflicts** with your system Python

### Running Locally (Recommended for Learning)

This is the simplest approach and perfect for understanding QUIC migration:

```bash
# Install dependencies
pip install -r requirements.txt

# Generate certificates
python generate_certs.py

# Terminal 1: Start server
python quic_server.py

# Terminal 2: Run client
python quic_client.py

# Or explore interactively
python migration_demo.py
```

### Running with Docker (Optional)

If you want network isolation or advanced testing:

```bash
# Build image
docker build -t quic-migration .

# Run server
docker run -p 4433:4433/udp quic-migration python quic_server.py

# Run client (in another terminal)
docker run --network host quic-migration python quic_client.py
```

## Project Structure

```
quic/
├── requirements.txt           # Python dependencies
├── generate_certs.py         # Generate self-signed certificates
├── quic_server.py            # QUIC server with migration tracking
├── quic_client.py            # QUIC client with migration simulation
├── migration_demo.py         # Interactive learning tool
├── README.md                 # This file
└── Dockerfile               # Optional Docker setup
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

The main dependency is `aioquic`, a Python implementation of QUIC.

### 2. Generate Certificates

QUIC requires TLS, so we need certificates:

```bash
python generate_certs.py
```

This creates `cert.pem` and `key.pem` for testing.

### 3. Interactive Learning

Start with the interactive demo to understand concepts:

```bash
python migration_demo.py
```

This provides:
- Explanations of QUIC migration concepts
- Step-by-step scenarios
- Benefits and use cases

### 4. Run Live Simulation

**Terminal 1 - Start the server:**
```bash
python quic_server.py
```

You should see:
```
🚀 Starting QUIC server on 127.0.0.1:4433
📋 Server supports connection migration
```

**Terminal 2 - Run the client:**
```bash
python quic_client.py
```

Watch both terminals to see:
- Connection establishment
- Data exchange
- Simulated migration events
- Migration tracking

## Understanding the Code

### Server (quic_server.py)

Key components:

1. **MigrationTracker** (line 37): Tracks and logs migration events
2. **QuicServerProtocol** (line 61): Handles QUIC events and detects migrations
3. **Migration Detection** (line 85): Compares client addresses to detect changes

The server automatically:
- Detects when client address/port changes
- Validates new paths
- Continues serving without interruption
- Tracks migration count

### Client (quic_client.py)

Key components:

1. **QuicClientProtocol** (line 34): Handles client-side QUIC events
2. **simulate_migration()** (line 66): Simulates different migration types
3. **send_message()** (line 51): Sends data and waits for response

The client can simulate:
- **NAT_REBINDING**: Source port changes
- **NETWORK_SWITCH**: Interface changes (WiFi → Cellular)
- **IP_CHANGE**: Full IP address change

### Demo Tool (migration_demo.py)

An educational tool that explains:
- QUIC migration concepts
- Real-world scenarios
- Step-by-step migration processes
- Benefits and use cases

## Migration Scenarios Explained

### 1. NAT Rebinding

**What happens:**
- Client behind NAT, source port changes
- Server receives packets from same IP but different port

**QUIC handles it:**
- Connection ID remains same
- Server validates new path
- Connection continues seamlessly

### 2. Network Interface Switch (WiFi → Cellular)

**What happens:**
- Mobile device switches from WiFi to cellular
- Completely new IP address

**QUIC handles it:**
- Connection ID identifies the connection
- Path validation with CHALLENGE/RESPONSE
- Zero application-level interruption

### 3. IP Address Change (ISP Reassignment)

**What happens:**
- DHCP lease renewal gives new IP
- Or connection reset by ISP

**QUIC handles it:**
- Connection state preserved
- Automatic path validation
- Transparent to application

### 4. Server-Preferred Address

**What happens:**
- Server advertises better route
- Client can migrate to preferred address

**QUIC handles it:**
- Server sends PREFERRED_ADDRESS
- Client validates and migrates
- Better routing or load balancing

## Key QUIC Migration Features

### Connection IDs
- Unlike TCP's 4-tuple, QUIC uses Connection IDs
- Allows network path to change
- Can be rotated for privacy

### Path Validation
- PATH_CHALLENGE frame to new address
- PATH_RESPONSE proves ownership
- Prevents address spoofing

### Zero-RTT Migration
- After initial validation, subsequent migrations are fast
- No handshake overhead
- Minimal latency impact

### Bidirectional
- Client can migrate (most common)
- Server can suggest preferred address
- Both validate new paths

## Benefits

1. **Seamless Mobility**: Switch networks without disconnection
2. **Better User Experience**: No interruptions in video, downloads, or games
3. **Reduced Latency**: No connection re-establishment overhead
4. **Privacy**: Rotate Connection IDs to prevent tracking
5. **Resilience**: Survive NAT rebindings and network changes

## Common Use Cases

- **Mobile Apps**: Maintain connections when switching WiFi/cellular
- **Video Conferencing**: Continue calls during network transitions
- **Downloads**: Large downloads survive network changes
- **Gaming**: Uninterrupted gameplay on mobile
- **IoT Devices**: Resilient connections for embedded systems

## Troubleshooting

### Port Already in Use
If you see "Address already in use":
```bash
# Find process using port 4433
lsof -i :4433

# Kill it or change port in server/client code
```

### Certificate Errors
If you see certificate errors:
```bash
# Regenerate certificates
python generate_certs.py
```

### Module Not Found
If you see import errors:
```bash
# Ensure aioquic is installed
pip install --upgrade aioquic
```

### No Migration Events Visible

The current simulation uses localhost loopback, which limits true network path changes. To see real migrations:

1. **Use multiple network interfaces**:
   - Bind client to WiFi interface
   - Switch to ethernet interface
   - Observe migration in logs

2. **Use network namespaces** (Linux):
   ```bash
   # Create namespace with different routing
   sudo ip netns add test
   ```

3. **Use Docker with custom networks**:
   - More realistic network simulation
   - Control network conditions

## Advanced Topics

### Simulating Real Network Changes

To properly test migration, you need actual network path changes:

```python
# Bind to specific interface
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('192.168.1.100', 0))  # Bind to WiFi IP
# Then switch to cellular IP
```

### Adding Packet Loss

Use `tc` (traffic control) on Linux:

```bash
# Add 10% packet loss
sudo tc qdisc add dev eth0 root netem loss 10%

# Add latency
sudo tc qdisc add dev eth0 root netem delay 100ms
```

### Multi-Path QUIC

While not in base spec, you can explore multi-path extensions:
- Use multiple paths simultaneously
- Aggregate bandwidth
- Failover redundancy

## Further Reading

- [QUIC RFC 9000](https://www.rfc-editor.org/rfc/rfc9000.html) - Official QUIC spec
- [Connection Migration (RFC 9000 Section 9)](https://www.rfc-editor.org/rfc/rfc9000.html#name-connection-migration)
- [aioquic Documentation](https://github.com/aiortc/aioquic)
- [Cloudflare QUIC Blog](https://blog.cloudflare.com/the-road-to-quic/)

## Next Steps

1. **Run the interactive demo**: `python migration_demo.py`
2. **Study the scenarios**: Understand each migration type
3. **Run live simulation**: See migrations in action
4. **Modify the code**: Add your own scenarios
5. **Experiment**: Try different network conditions

## License

This is an educational project for learning QUIC connection migration.
