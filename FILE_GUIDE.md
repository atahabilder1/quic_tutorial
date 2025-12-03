# File Guide - What Each File Does

## Overview

This project contains multiple types of files for learning QUIC protocol:

1. **Jupyter Notebooks (.ipynb)** - Interactive tutorials
2. **Python Scripts (.py)** - Executable programs
3. **Markdown Files (.md)** - Documentation
4. **Configuration Files** - Project setup

---

## Jupyter Notebooks (Learning Files)

### `quic_migration_simple.ipynb` ⭐ START HERE
**Purpose:** Basic introduction to QUIC connection migration

**What it teaches:**
- What are Connection IDs?
- How packets look during migration
- Complete migration simulation (WiFi → Cellular)
- TCP vs QUIC comparison
- Real-world example (video download)

**How to use:**
1. Open in Jupyter browser
2. Run cells one by one (Shift+Enter)
3. Read output carefully
4. Takes ~30 minutes

**What it does internally:**
- Simulates QUIC connections in Python
- Creates fake packets with Connection IDs
- Shows migration step-by-step
- Visualizes timeline

---

### `path_validation_deep_dive.ipynb` ⭐ FOR RESEARCH
**Purpose:** Deep technical details for academic papers

**What it teaches:**
- Path validation state machine
- Timeout calculations & retries
- Multiple paths simultaneously
- Preferred address (server-initiated)
- State synchronization
- Anti-amplification

**How to use:**
1. Open after finishing simple notebook
2. Execute cells sequentially
3. Focus on Parts 2, 4, 6, 7, 8
4. Takes ~45-60 minutes

**What it does internally:**
- Implements PathManager class
- Simulates timeout scenarios
- Demonstrates retry logic
- Shows Connection ID lifecycle
- Calculates RTT and validation timeouts

---

### `quic_comprehensive_tutorial.ipynb` ⭐ COMPLETE UNDERSTANDING
**Purpose:** Comprehensive networking knowledge from basics

**What it teaches:**
- OSI Model (7 layers explained)
- IP-based vs Connection ID-based protocols
- Why TCP, FTP, SSH break on network change
- Why QUIC survives
- Firewall deep packet inspection
- What firewalls can/cannot see
- NAT (Network Address Translation)
- NAT rebinding problem

**How to use:**
1. For complete understanding from scratch
2. Best if you're learning networking
3. Explains concepts multiple times
4. Takes ~1-2 hours

**What it does internally:**
- Visualizes packet structures
- Compares HTTP, HTTPS, QUIC packets
- Simulates firewall perspective
- Demonstrates NAT behavior

---

## Python Script Files (Executable Programs)

### `generate_certs.py`
**Purpose:** Creates SSL/TLS certificates for QUIC

**What it does:**
```bash
python3 generate_certs.py
```

**Output:**
- `cert.pem` - Public certificate (server's identity)
- `key.pem` - Private key (server's secret)

**Why needed:**
- QUIC requires encryption (TLS 1.3 built-in)
- Cannot run QUIC without certificates
- Creates self-signed cert for testing

**Technical details:**
- Uses Python cryptography library
- Generates 2048-bit RSA key pair
- Certificate valid for 365 days
- Works for localhost and 127.0.0.1

**When to run:**
- ONCE before starting server
- Re-run if certificates expire
- Re-run if you delete cert.pem/key.pem

---

### `quic_server.py`
**Purpose:** Real QUIC server that accepts connections

**What it does:**
```bash
python3 quic_server.py
```

**Behavior:**
1. Starts QUIC server on localhost:4433
2. Waits for client connections
3. Accepts QUIC handshake
4. Receives data from client
5. Sends response back
6. Detects when client migrates
7. Validates new path
8. Continues communication

**Technical details:**
- Uses aioquic library
- Implements MigrationTracker class
- Tracks client address changes
- Logs all migration events
- Handles PATH_CHALLENGE/RESPONSE

**What you see in terminal:**
```
🚀 Starting QUIC server on 127.0.0.1:4433
✅ Handshake completed | Connection ID: 4a3f2e1b...
📨 Received on stream 0: Hello QUIC Server!
🔄 MIGRATION #1 detected | (old IP) -> (new IP)
📤 Sent response: Echo: Hello QUIC Server! | Migrations: 1
```

**How it detects migration:**
```python
# Server stores last client address
self.last_client_addr = "192.168.1.100:50000"

# New packet arrives
current_addr = "10.20.30.40:50001"  # Different!

# But same Connection ID
if current_addr != self.last_client_addr:
    # MIGRATION DETECTED!
    self.migration_tracker.record_migration(...)
```

---

### `quic_client.py`
**Purpose:** Real QUIC client that connects to server

**What it does:**
```bash
python3 quic_client.py
```

**Behavior:**
1. Connects to QUIC server at localhost:4433
2. Performs QUIC handshake
3. Sends initial message
4. Simulates migration (changes address)
5. Sends more messages from new address
6. Receives responses
7. Demonstrates migration works

**Technical details:**
- Uses aioquic library
- Can simulate different migration types:
  - NAT rebinding (port change)
  - Network switch (IP change)
  - Multiple migrations
- Tracks response times

**What you see in terminal:**
```
🔌 Connecting to QUIC server at 127.0.0.1:4433
✅ Connected to server
📤 Sending: Hello QUIC Server!
📨 Received response: Echo: Hello QUIC Server! | Migrations: 0
🔄 Simulating NAT rebinding migration...
📤 Sending: Message after migration
📨 Received response: Echo: ... | Migrations: 1
```

**How it simulates migration:**
```python
# In real scenario, this would be automatic
# when network changes (WiFi -> Cellular)

# But for demo, we trigger it manually:
protocol._quic.request_key_update()

# This causes QUIC to probe new paths
# Server sees packets from "new" address
# (In real migration, IP would actually change)
```

**Note:** The script simulates migration logically. For REAL migration, you'd need:
- Client on one machine/network
- Server on another machine
- Actually switch networks on client

---

### `migration_demo.py`
**Purpose:** Interactive menu to explore QUIC concepts

**What it does:**
```bash
python3 migration_demo.py
```

**Features:**
1. Interactive text-based menu
2. Explains QUIC migration concepts
3. Shows different scenarios:
   - NAT rebinding
   - WiFi → Cellular switch
   - Server-preferred address
   - Multi-path QUIC
4. Displays step-by-step explanations

**What you see:**
```
🚀 QUIC CONNECTION MIGRATION - INTERACTIVE DEMO
==================================================================

What would you like to explore?

1. 📚 Learn about QUIC Migration Concepts
2. ✨ See Benefits of Connection Migration
3. 🎯 Explore Migration Scenarios
4. 🏃 Run Live Demo
0. 🚪 Exit
```

**Technical details:**
- Pure Python (no QUIC library needed)
- Educational tool, not actual QUIC
- Prints detailed explanations
- Interactive learning

**When to use:**
- Want quick overview without notebooks
- Prefer terminal over Jupyter
- Want to understand concepts before code

---

### `test_real_migration.py`
**Purpose:** Verify aioquic supports migration

**What it does:**
```bash
python3 test_real_migration.py
```

**Behavior:**
1. Creates QUIC client and server objects
2. Checks for migration-related methods
3. Lists available features
4. Confirms aioquic supports migration

**Output:**
```
Testing Real Migration Support in aioquic
==================================================================

1. Creating QUIC configurations...
   ✅ Client and server connections created

3. Connection Details:
   Client has Connection IDs: True
   Server has Connection IDs: True
   Client has network paths: True
   Server has network paths: True

4. Migration Methods Available:
   ✅ _get_or_create_network_path
   ✅ _handle_path_challenge_frame
   ✅ _handle_path_response_frame

RESULT: aioquic FULLY SUPPORTS Connection Migration!
```

**Technical details:**
- Tests aioquic library capabilities
- Checks for required methods
- Verifies RFC 9000 compliance

**When to run:**
- After installing aioquic
- To verify library version
- For debugging

---

### `verify_migration_support.py`
**Purpose:** Detailed migration feature check

**What it does:**
```bash
python3 verify_migration_support.py
```

**Behavior:**
- Similar to test_real_migration.py
- More detailed output
- Lists all migration features
- Compares implementations

**When to run:**
- Want detailed capability list
- Comparing QUIC implementations
- For research/paper citations

---

## Documentation Files (.md)

### `README.md`
**Purpose:** Main project documentation

**Contains:**
- Project overview
- What is QUIC migration?
- Do you need Docker? (No!)
- Quick start guide
- File structure
- Installation instructions
- Troubleshooting

**When to read:** First time seeing project

---

### `QUICKSTART.md`
**Purpose:** Fast setup guide

**Contains:**
- 3-step setup
- Learning paths
- Common questions
- Next steps

**When to read:** Want to start immediately

---

### `COMPREHENSIVE_GUIDE.md`
**Purpose:** Technical reference for papers

**Contains:**
- QUIC architecture
- Connection migration protocol
- Packet structure
- Research methodology
- Metrics for papers
- Academic references

**When to read:** Writing research paper

---

### `COMPLETE_REFERENCE.md`
**Purpose:** Complete networking knowledge

**Contains:**
- OSI model detailed
- IP-based vs Connection ID protocols
- Firewall analysis
- NAT traversal
- Security implications

**When to read:** Want complete understanding

---

### `FILE_GUIDE.md`
**Purpose:** This file! Explains all other files

---

## Configuration Files

### `requirements.txt`
**Purpose:** Lists required Python libraries

**Contains:**
```
aioquic>=0.9.25
asyncio
colorlog>=6.7.0
cryptography>=41.0.0
jupyter>=1.0.0
ipython>=8.12.0
notebook>=7.0.0
scapy>=2.5.0
```

**Install with:**
```bash
pip install -r requirements.txt
```

---

### `.gitignore`
**Purpose:** Tells Git what files NOT to track

**Ignores:**
- `venv/` - Virtual environment (large!)
- `*.pem` - Certificates (sensitive!)
- `__pycache__/` - Python cache
- `.ipynb_checkpoints/` - Jupyter checkpoints
- Other temporary files

**Why important:**
- Keeps Git repo clean
- Prevents uploading secrets
- Reduces repo size

---

### `Dockerfile`
**Purpose:** Docker container definition (optional)

**Contains:**
- Base image
- Install commands
- Configuration

**Note:** NOT required! Running natively is easier.

---

### `docker-compose.yml`
**Purpose:** Docker orchestration (optional)

**Contains:**
- Service definitions
- Network configuration
- Volume mounts

**Note:** NOT required! You can ignore Docker entirely.

---

## File Relationships

```
User Learning Path:
┌─────────────────────────────────────────────┐
│ 1. READ: README.md or QUICKSTART.md        │
│    Understand what project is about        │
└────────────────┬────────────────────────────┘
                 │
                 v
┌─────────────────────────────────────────────┐
│ 2. SETUP: Install requirements             │
│    pip install -r requirements.txt         │
└────────────────┬────────────────────────────┘
                 │
                 v
┌─────────────────────────────────────────────┐
│ 3. GENERATE: Certificates                   │
│    python3 generate_certs.py               │
└────────────────┬────────────────────────────┘
                 │
                 v
┌─────────────────────────────────────────────┐
│ 4. LEARN: Choose your path                  │
│    A) Interactive: python3 migration_demo.py│
│    B) Jupyter: quic_migration_simple.ipynb  │
│    C) Terminal: quic_server.py + client.py  │
└────────────────┬────────────────────────────┘
                 │
                 v
┌─────────────────────────────────────────────┐
│ 5. DEEP DIVE: Advanced notebooks            │
│    - path_validation_deep_dive.ipynb       │
│    - quic_comprehensive_tutorial.ipynb     │
└────────────────┬────────────────────────────┘
                 │
                 v
┌─────────────────────────────────────────────┐
│ 6. RESEARCH: Reference documents            │
│    - COMPREHENSIVE_GUIDE.md                 │
│    - COMPLETE_REFERENCE.md                  │
└─────────────────────────────────────────────┘
```

---

## Quick Reference: What to Run When

### First Time Setup:
```bash
cd /home/anik/code/quic
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 generate_certs.py
```

### To Learn Concepts:
```bash
python3 migration_demo.py
# OR
jupyter notebook
# Then open: quic_migration_simple.ipynb
```

### To See Real QUIC:
```bash
# Terminal 1:
python3 quic_server.py

# Terminal 2:
python3 quic_client.py
```

### For Research/Paper:
```bash
jupyter notebook
# Open: path_validation_deep_dive.ipynb
# Read: COMPREHENSIVE_GUIDE.md
```

---

## Summary Table

| File | Type | Purpose | When to Use |
|------|------|---------|-------------|
| `quic_migration_simple.ipynb` | Notebook | Basic tutorial | Learning QUIC |
| `path_validation_deep_dive.ipynb` | Notebook | Technical details | Research/Paper |
| `quic_comprehensive_tutorial.ipynb` | Notebook | Complete networking | Learning from scratch |
| `generate_certs.py` | Script | Create certificates | Once at setup |
| `quic_server.py` | Script | QUIC server | See real QUIC |
| `quic_client.py` | Script | QUIC client | See real QUIC |
| `migration_demo.py` | Script | Interactive menu | Quick learning |
| `test_real_migration.py` | Script | Verify support | Debugging |
| `verify_migration_support.py` | Script | Feature check | Research |
| `README.md` | Doc | Main overview | First read |
| `QUICKSTART.md` | Doc | Fast start | Impatient users |
| `COMPREHENSIVE_GUIDE.md` | Doc | Research ref | Writing paper |
| `COMPLETE_REFERENCE.md` | Doc | Full details | Deep understanding |
| `FILE_GUIDE.md` | Doc | This file | Understanding project |

---

## Need Help?

**"I want to understand QUIC quickly"**
→ Run: `python3 migration_demo.py`

**"I want interactive learning"**
→ Open Jupyter: `quic_migration_simple.ipynb`

**"I'm writing a research paper"**
→ Open: `path_validation_deep_dive.ipynb`
→ Read: `COMPREHENSIVE_GUIDE.md`

**"I want to see it actually work"**
→ Run server and client scripts

**"I'm confused about files"**
→ You're reading the right file!

**"I want to understand networking from basics"**
→ Open: `quic_comprehensive_tutorial.ipynb`
