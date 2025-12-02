# QUIC Migration - Quick Start Guide

## Setup (5 minutes)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Generate SSL Certificates

```bash
python generate_certs.py
```

You should see: `✅ Generated cert.pem and key.pem`

## Learning Paths

### Path 1: Interactive Learning (Recommended for Beginners)

**Start here if you're new to QUIC!**

```bash
python migration_demo.py
```

This interactive tool lets you:
- Learn QUIC migration concepts
- Explore different migration scenarios
- See step-by-step explanations

### Path 2: Jupyter Notebooks (Best for Deep Understanding)

**Perfect for understanding packet-level details**

Start Jupyter:
```bash
jupyter notebook
```

Then open these notebooks in order:

1. **quic_migration_tutorial.ipynb** - QUIC Connection Migration basics
   - Understanding Connection IDs
   - Path validation
   - Migration scenarios
   - Packet inspection

2. **http3_simulation.ipynb** - HTTP/3 over QUIC
   - HTTP/3 requests and responses
   - Migration during downloads
   - Multiplexing demo
   - Performance comparisons

### Path 3: Live Demo (See It In Action)

**Watch real QUIC connections with migration**

Terminal 1 - Start server:
```bash
python quic_server.py
```

Terminal 2 - Run client:
```bash
python quic_client.py
```

Watch both terminals to see:
- Connection establishment
- Data exchange
- Migration events
- Path validation

## What to Expect

### Migration Demo Output
```
🚀 QUIC CONNECTION MIGRATION - INTERACTIVE DEMO
==================================================================

What would you like to explore?

1. 📚 Learn about QUIC Migration Concepts
2. ✨ See Benefits of Connection Migration
3. 🎯 Explore Migration Scenarios
...
```

### Live Demo Output

Server terminal:
```
🚀 Starting QUIC server on 127.0.0.1:4433
✅ Handshake completed | Connection ID: 4a3f2e1b...
📨 Received on stream 0: Hello QUIC Server!
🔄 MIGRATION #1 detected | (old IP) -> (new IP)
```

Client terminal:
```
🔌 Connecting to QUIC server at 127.0.0.1:4433
✅ Connected to server
📤 Sending: Hello QUIC Server!
🔄 Simulating NAT rebinding migration...
📨 Received response: Echo: Hello QUIC Server! | Migrations: 1
```

### Jupyter Notebook Experience

Interactive cells showing:
- Packet structure visualization
- Connection ID inspection
- Step-by-step migration process
- TCP vs QUIC comparisons
- HTTP/3 request/response flow

## Common Questions

### Do I need Docker?

**No!** Docker is optional. Everything works on your local machine.

Use Docker if you want:
- Network isolation
- Advanced network simulation
- Easy cleanup

### Can I see real network migrations?

The local demo simulates migrations. For real migrations:

1. Run server on one machine
2. Run client on another (laptop/phone)
3. Switch networks on the client device
4. Watch the connection migrate!

### What if I see errors?

**Port in use:**
```bash
# Change port in quic_server.py and quic_client.py
# Or kill the process using port 4433
lsof -i :4433
```

**Certificate errors:**
```bash
# Regenerate certificates
python generate_certs.py
```

**Import errors:**
```bash
# Upgrade aioquic
pip install --upgrade aioquic
```

## Next Steps

After the quick start:

1. **Read the full README.md** - Comprehensive documentation
2. **Modify the code** - Add your own scenarios
3. **Experiment with packet capture** - Use Wireshark
4. **Read QUIC RFC 9000** - Specification details

## Project Structure

```
quic/
├── QUICKSTART.md              ← You are here
├── README.md                  ← Full documentation
├── requirements.txt           ← Python dependencies
│
├── generate_certs.py          ← SSL certificate generator
│
├── migration_demo.py          ← Interactive learning tool
├── quic_server.py            ← QUIC server with migration tracking
├── quic_client.py            ← QUIC client with migration simulation
│
├── quic_migration_tutorial.ipynb  ← Jupyter: QUIC basics
├── http3_simulation.ipynb         ← Jupyter: HTTP/3 demo
│
├── Dockerfile                 ← Optional Docker setup
└── docker-compose.yml         ← Optional Docker orchestration
```

## Tips for Learning

1. **Start with concepts** - Run `migration_demo.py` first
2. **Hands-on exploration** - Open the Jupyter notebooks
3. **See it live** - Run the server/client demo
4. **Experiment** - Modify code and observe changes
5. **Read the code** - All files are well-commented

## Resources

- [QUIC RFC 9000](https://www.rfc-editor.org/rfc/rfc9000.html)
- [aioquic Documentation](https://github.com/aiortc/aioquic)
- [HTTP/3 Explained](https://http3-explained.haxx.se/)
- [Cloudflare QUIC Blog](https://blog.cloudflare.com/tag/quic/)

## Get Help

If you encounter issues:
1. Check the README.md troubleshooting section
2. Review the code comments
3. Ensure all dependencies are installed
4. Try regenerating certificates

Happy learning! 🚀
