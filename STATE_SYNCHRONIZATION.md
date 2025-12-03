# QUIC State Synchronization & Server Migration

## Your Question: How Do Servers Sync State?

**Scenario:**
```
You're watching YouTube on Chrome:
- Connected to Server A (203.0.113.50)
- Downloaded 100MB of video so far
- Server A migrates you to Server B (203.0.113.51)
- Server B needs to know: "What was already sent? What's next?"
```

**Answer:** QUIC is **stateful**, and servers must **explicitly synchronize state** before migration.

---

## 1. QUIC Connection State

### What State Does QUIC Maintain?

Every QUIC connection has extensive state on BOTH sides:

```
Client State:
├── Connection IDs (mine and server's)
├── Packet numbers (sent and received)
├── Flow control windows (how much can I send/receive)
├── Stream state (which streams are open, closed, data buffered)
├── Congestion control (RTT, cwnd, ssthresh)
├── Crypto keys (1-RTT keys for encryption)
└── Application data (buffered, waiting to send/ack)

Server State:
├── Connection IDs (mine and client's)
├── Packet numbers (sent and received)
├── Flow control windows
├── Stream state (e.g., "Sent bytes 0-100MB on stream 4")
├── Congestion control
├── Crypto keys
└── Application data (e.g., "Next video chunk is bytes 100MB-101MB")
```

**Critical:** All this state must be preserved during migration!

---

## 2. Server-Side Migration State Transfer

### Problem Statement

```
Client watching YouTube video:
┌──────────┐
│  Chrome  │  "I've received bytes 0-100MB"
└─────┬────┘  "Next packet I expect: 100MB+1"
      │
      │ Connected to:
      v
┌──────────┐
│ Server A │  "I've sent bytes 0-100MB"
│ YouTube  │  "Next packet to send: 100MB+1"
└──────────┘  "Client has acked up to: 100MB"

Server A says: "Migrate to Server B"

How does Server B know:
  ❓ What was already sent?
  ❓ What was already acknowledged?
  ❓ What's the next packet to send?
  ❓ What are the crypto keys?
```

### QUIC Does NOT Automatically Sync State! ⚠️

**Key point:** QUIC protocol itself does NOT define server-to-server state synchronization.

**Why?** QUIC is an **end-to-end protocol** (client ↔ server), not a **server-to-server protocol**.

**Implication:** Server-side migration requires **application-level** or **infrastructure-level** state sharing.

---

## 3. How Server Migration Actually Works

### Approach 1: Load Balancer with Connection Routing

**Most common in practice (Google, Cloudflare, etc.)**

```
┌─────────────────────────────────────────────────────┐
│              Load Balancer (Stateful)                │
│                                                      │
│  Maintains mapping:                                  │
│    Connection ID → Backend Server                    │
│                                                      │
│  Example:                                            │
│    CID_ABC123 → Server A (203.0.113.50)             │
│    CID_DEF456 → Server B (203.0.113.51)             │
└─────────────────────┬────────────────────────────────┘
                      │
        ┌─────────────┴────────────┐
        v                          v
  ┌──────────┐              ┌──────────┐
  │ Server A │              │ Server B │
  │          │              │          │
  │ Holds    │              │ Holds    │
  │ state for│              │ state for│
  │ CID_ABC  │              │ CID_DEF  │
  └──────────┘              └──────────┘

Migration Process:
1. Client connects to LB with CID_ABC123
2. LB routes to Server A
3. Connection state lives ONLY on Server A
4. Server A advertises preferred_address with NEW CID_XYZ789
5. LB updates mapping: CID_XYZ789 → Server B
6. Client migrates to Server B using CID_XYZ789
7. Server B receives packets
8. Server B has NO state for this connection! ❌

Problem: Server B doesn't know what was already sent!
```

**Solution:** Server A must transfer state to Server B BEFORE advertising preferred address.

---

### Approach 2: Shared State Backend

**Used by large-scale deployments (YouTube, Netflix, etc.)**

```
┌──────────────────────────────────────────────────────┐
│          Shared State Store (Redis, Memcached)        │
│                                                       │
│  Connection ID: ABC123                                │
│    • Packet numbers: sent=10000, acked=9995          │
│    • Stream 4: sent bytes 0-100MB                    │
│    • Stream 4: client acked bytes 0-99.5MB           │
│    • Crypto keys: [1-RTT keys]                       │
│    • Flow control: max_data=500MB, data_sent=100MB   │
│    • Congestion: RTT=50ms, cwnd=100, ssthresh=200    │
└──────────────┬──────────────────────┬─────────────────┘
               │                      │
       ┌───────┴────────┐    ┌────────┴─────────┐
       │   Server A     │    │   Server B       │
       │                │    │                  │
       │ Reads/writes   │    │ Reads/writes     │
       │ to shared      │    │ to shared        │
       │ state store    │    │ state store      │
       └────────────────┘    └──────────────────┘

Migration Process:
1. Client connected to Server A via CID_ABC123
2. Server A reads/writes state to Redis for ABC123
3. Server A decides to migrate → advertises preferred_address with CID_XYZ789
4. Server A writes to Redis: "CID_XYZ789 → same state as ABC123"
5. Client migrates to Server B using CID_XYZ789
6. Server B receives packet with CID_XYZ789
7. Server B reads state from Redis
8. Server B continues from where Server A left off! ✅

YouTube Example:
  Server A sent:     bytes 0-100MB (stream 4)
  Server A wrote to Redis: "CID_XYZ789: stream 4, offset 100MB"
  Server B reads from Redis: "stream 4, offset 100MB"
  Server B sends:    bytes 100MB-101MB (continues seamlessly!)
```

---

### Approach 3: State Transfer Protocol (Custom)

**Used by some CDNs (Fastly, Akamai, etc.)**

```
Server A                                    Server B
   │                                           │
   │  1. Decide to migrate                     │
   │                                           │
   │  2. Serialize connection state:           │
   │     • Packet numbers                      │
   │     • Stream offsets                      │
   │     • Crypto keys                         │
   │     • Flow control state                  │
   │                                           │
   │  3. Send state to Server B                │
   ├──────────── [State Transfer] ────────────>│
   │                                           │
   │                                           │ 4. Receive and deserialize state
   │                                           │
   │  5. Advertise preferred_address           │
   │     (Server B's IP + new CID)             │
   │                                           │
   │  6. Client migrates                       │
   │                                           │
   │                                           │ 7. Receive packets
   │                                           │ 8. Continue using transferred state ✅
   │                                           │
```

**Challenges:**
- State can be large (100s of KB for long-lived connections)
- Needs to be atomic (transfer + migration)
- Crypto keys must be securely transferred
- Race conditions (what if client sends packet during transfer?)

---

## 4. YouTube Example: Detailed State

### Scenario: Watching 1-hour 4K Video

**Connection State at Migration Time:**

```
Connection ID: 4a3f2e1b9c8d7a6f

Streams (HTTP/3):
  Stream 0 (Control):
    • Status: Open
    • Sent: 500 bytes (HTTP/3 control messages)
    • Received: 200 bytes
    • Acked: All

  Stream 4 (Video Data):
    • Status: Open
    • Sent: 104,857,600 bytes (100 MB)
    • Acked by client: 104,800,000 bytes (99.95 MB)
    • Buffered (not yet acked): 57,600 bytes (pending)
    • Next byte to send: 104,857,601

  Stream 8 (Audio Data):
    • Status: Open
    • Sent: 10,485,760 bytes (10 MB)
    • Acked by client: 10,485,760 bytes (all)
    • Next byte to send: 10,485,761

Packet Numbers:
  • Sent packet number: 15,324
  • Highest acked packet number: 15,320
  • Pending acks: packets 15,321-15,324

Flow Control:
  • max_data (connection-level): 500 MB
  • data_sent (connection-level): 115 MB
  • max_stream_data (stream 4): 200 MB
  • stream_data_sent (stream 4): 100 MB

Congestion Control:
  • RTT: 50 ms (smoothed)
  • RTT variance: 5 ms
  • Congestion window (cwnd): 1,000 packets
  • Slow start threshold (ssthresh): 500 packets
  • Bytes in flight: 57,600 bytes

Crypto:
  • 1-RTT encryption keys: [32 bytes each for send/recv]
  • Key phase: 0

User Context (Application-Level):
  • Video ID: dQw4w9WgXcQ
  • Quality: 4K (2160p)
  • Playback position: 15:32 (932 seconds)
  • Buffer: 30 seconds ahead
```

**All of this must be transferred to Server B!**

---

## 5. State Synchronization Methods Comparison

| Method | Pros | Cons | Used By |
|--------|------|------|---------|
| **Shared State Store** | • Simple to implement<br>• Highly available<br>• Servers can crash without data loss | • Latency (network round-trip)<br>• Single point of failure (if Redis down)<br>• Complexity (Redis cluster) | Google, YouTube, Facebook |
| **Stateless Load Balancer + Connection Pinning** | • No state transfer needed<br>• Server owns all state | • Can't migrate to different server<br>• Defeats purpose of server migration | Small deployments |
| **Direct State Transfer** | • Fast (server-to-server)<br>• No external dependency | • Complex protocol<br>• Race conditions<br>• Security (key transfer) | Some CDNs |
| **No Migration (Graceful Shutdown)** | • Simple<br>• No state sync needed | • Connections drop<br>• Bad user experience | Many legacy deployments |

---

## 6. QUIC Protocol-Level Considerations

### What QUIC Provides

✅ **Connection IDs:** Allow packets to be routed to correct server
✅ **Packet numbers:** Monotonically increasing (prevent replay)
✅ **Crypto keys:** Symmetric keys for encryption (both sides have same keys)
✅ **Frames:** Structured data (STREAM, ACK, etc.)

### What QUIC Does NOT Provide

❌ **Server-to-server state transfer:** Not defined in RFC 9000
❌ **State serialization format:** Each implementation different
❌ **Synchronization protocol:** Application-specific
❌ **Consistency guarantees:** No transactional state transfer

---

## 7. Practical Example: Google QUIC Migration

### Google's Approach (Simplified)

```
Architecture:
┌─────────────────────────────────────────┐
│  Google Front End (GFE) - Load Balancer │
│                                         │
│  Stateless routing based on CID         │
│    CID → Hash → Backend Server          │
└─────────────────┬───────────────────────┘
                  │
        ┌─────────┴──────────┐
        │                    │
  ┌─────▼─────┐      ┌───────▼────┐
  │ Backend A │      │ Backend B  │
  │           │      │            │
  │ Chubby    │      │ Chubby     │
  │ (shared   │      │ (shared    │
  │  state)   │      │  state)    │
  └───────────┘      └────────────┘
        │                    │
        └──────────┬─────────┘
                   │
         ┌─────────▼──────────┐
         │  Chubby / Spanner   │
         │  (Distributed DB)   │
         │                     │
         │  Connection state   │
         │  stored here        │
         └─────────────────────┘

Migration Process:
1. Client connects via GFE with CID_1
2. GFE hashes CID_1 → routes to Backend A
3. Backend A stores state in Chubby under key "CID_1"
4. Backend A decides to migrate
5. Backend A generates NEW CID_2 for Backend B
6. Backend A stores in Chubby: "CID_2 → copy of CID_1 state"
7. Backend A sends preferred_address with CID_2
8. Client migrates to CID_2
9. GFE hashes CID_2 → routes to Backend B
10. Backend B reads state from Chubby under "CID_2"
11. Backend B continues connection seamlessly! ✅
```

### Why This Works:

✅ **Shared state store (Chubby/Spanner):** All backends can read/write
✅ **Stateless routing (GFE):** Just hashes CID, doesn't keep state
✅ **Atomic migration:** State written before preferred_address sent
✅ **Fault tolerance:** If Backend A crashes, state still in Chubby

---

## 8. Challenges in State Synchronization

### Challenge 1: Atomicity

**Problem:**
```
Timeline:
T=0: Server A sends preferred_address (CID_2 → Server B)
T=1: Client receives preferred_address
T=2: Server A writes state to shared store
T=3: Client sends packet to Server B with CID_2
T=4: Server B tries to read state → NOT THERE YET! ❌

Race condition: Client migrated before state was written!
```

**Solution:**
```
1. Server A writes state to shared store FIRST
2. Server A confirms write successful
3. THEN Server A sends preferred_address
4. Now client can migrate safely
```

### Challenge 2: Large State Size

**Problem:**
- Long-lived connection: 10,000+ packets
- Many streams: 100+ streams
- State size: 100s of KB

**Impact:**
- Latency: Time to serialize + transfer + deserialize
- Network: Bandwidth consumed by state transfer

**Solution:**
- Compress state (gzip)
- Transfer only essential state (active streams, not closed ones)
- Incremental updates (delta encoding)

### Challenge 3: Crypto Key Security

**Problem:**
- 1-RTT keys are symmetric secrets
- Must be transferred securely to Server B
- If leaked → connection can be decrypted

**Solution:**
- Encrypt state transfer (TLS between servers)
- Use secure RPC (gRPC with mTLS)
- Store keys in Hardware Security Module (HSM)

### Challenge 4: Packet Reordering

**Problem:**
```
T=0: Client sends packet#100 to Server A
T=1: Server A migrates
T=2: Client sends packet#101 to Server B
T=3: Packet#100 arrives at Server B (network reordering)

Server B receives packets out-of-order across migration!
```

**Solution:**
- QUIC handles this naturally (packet numbers are monotonic)
- Server B buffers packet#100
- Server B waits for state transfer
- Server B processes in order once state is available

---

## 9. Your Research Context

### For QUIC-Exfil Attack:

**Attacker does NOT need state sync!** 🔥

```
Why?

Normal server migration:
  • Server A has state (sent 100MB)
  • Server A transfers state to Server B
  • Server B continues (sends 100MB+1)
  • Client expects continuity

Malicious "migration" (QUIC-Exfil):
  • Malware spoofs migration to Attacker Server
  • Attacker Server receives exfiltrated data
  • Attacker Server does NOT need to continue connection
  • Attacker just collects data and drops packets
  • Client eventually times out and reconnects
  • Attack already succeeded!
```

**Key insight:** Attack exploits migration mechanism WITHOUT needing to maintain connection continuity.

### For Your Defense:

**Detecting lack of continuity:**

```
Normal migration:
  • Server B continues sending data
  • Stream offsets increase monotonically
  • ACKs keep flowing
  • RTT stable

Malicious migration:
  • Attacker Server does NOT send new data (doesn't have it!)
  • Stream offsets do NOT increase
  • Connection eventually fails
  • Client retries or reconnects

Detection signal:
  ✅ Monitor for migrations that don't result in continued communication
  ✅ Expect ACKs after migration (attacker may not send)
  ✅ Expect data transmission to resume (attacker may not have data)
```

---

## 10. Summary

### Does QUIC automatically sync state between servers?

❌ **NO** - QUIC is an end-to-end protocol, not server-to-server

### How do servers sync state for migration?

✅ **Shared state store** (Redis, Chubby, Spanner)
✅ **Direct state transfer** (custom protocol)
✅ **Connection pinning** (no migration, defeats purpose)

### What state needs to be synced?

✅ Packet numbers (sent, acked)
✅ Stream offsets (how much data sent/received per stream)
✅ Flow control windows
✅ Congestion control state (RTT, cwnd, etc.)
✅ Crypto keys (1-RTT symmetric keys)
✅ Application state (e.g., video playback position)

### Example: YouTube video

```
Server A:
  • Stream 4: sent bytes 0-100MB
  • Client acked: bytes 0-99.5MB
  • Next byte to send: 100MB+1

Migration:
  Server A writes to Redis:
    "CID_XYZ: stream 4, offset 100MB, acked 99.5MB"

  Server B reads from Redis:
    "CID_XYZ: stream 4, offset 100MB, acked 99.5MB"

  Server B sends:
    bytes 100MB-101MB (continues seamlessly!)
```

### Does attacker need to sync state?

❌ **NO** - QUIC-Exfil attack doesn't maintain continuity
✅ Attacker just collects exfiltrated data and drops connection
✅ Client eventually times out (attack already succeeded)

---

## Related Files

- `server_side_migration.ipynb` - Preferred address mechanism
- `path_validation_deep_dive.ipynb` - Part 8 (State Synchronization)
- `PAPER_SUMMARY.md` - QUIC-Exfil attack (no state sync needed)
- `RESEARCH_OPPORTUNITIES.md` - Use lack of continuity as detection signal!

---

**Bottom line:** Server-side migration requires explicit state synchronization, but QUIC doesn't define how. Large deployments use shared state stores (Redis, Chubby, Spanner). Attackers don't need state sync, which creates a detection opportunity!
