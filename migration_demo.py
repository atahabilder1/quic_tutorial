#!/usr/bin/env python3
"""
QUIC Migration Demo - Interactive Scenarios
Demonstrates different connection migration scenarios
"""

import asyncio
import logging
from typing import List, Dict
import colorlog

# Setup colored logging
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    '%(log_color)s%(levelname)s: %(message)s',
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


class MigrationScenario:
    """Represents a QUIC connection migration scenario"""

    def __init__(self, name: str, description: str, steps: List[Dict]):
        self.name = name
        self.description = description
        self.steps = steps

    def explain(self):
        """Print explanation of the scenario"""
        print(f"\n{'='*70}")
        print(f"📚 Scenario: {self.name}")
        print(f"{'='*70}")
        print(f"\n{self.description}\n")
        print("Steps:")
        for i, step in enumerate(self.steps, 1):
            print(f"  {i}. {step['description']}")
            if 'detail' in step:
                print(f"     → {step['detail']}")
        print(f"\n{'='*70}\n")


# Define migration scenarios
SCENARIOS = [
    MigrationScenario(
        name="NAT Rebinding",
        description=(
            "NAT rebinding occurs when a client behind a NAT device gets a new "
            "source port assigned. This is common when NAT mappings timeout or "
            "when the NAT device reassigns ports."
        ),
        steps=[
            {
                'description': "Client establishes QUIC connection through NAT",
                'detail': "NAT maps internal IP:port to external IP:port1"
            },
            {
                'description': "NAT mapping times out or is reassigned",
                'detail': "NAT assigns new external port2 to same connection"
            },
            {
                'description': "Client packets arrive from new source port",
                'detail': "Server receives packets from same IP but different port"
            },
            {
                'description': "Server validates new path using PATH_CHALLENGE",
                'detail': "Ensures client actually owns the new path"
            },
            {
                'description': "Migration completes, connection continues seamlessly",
                'detail': "No data loss or connection interruption"
            }
        ]
    ),

    MigrationScenario(
        name="Network Interface Switch (WiFi to Cellular)",
        description=(
            "This scenario occurs when a mobile device switches from WiFi to cellular "
            "network (or vice versa). The IP address changes completely, but QUIC "
            "maintains the connection using Connection IDs."
        ),
        steps=[
            {
                'description': "Client connected via WiFi (IP: 192.168.1.100)",
                'detail': "Active QUIC connection with Connection ID ABC123"
            },
            {
                'description': "WiFi signal weakens, client switches to cellular",
                'detail': "New IP address assigned: 10.20.30.40"
            },
            {
                'description': "Client sends packet with same Connection ID from new IP",
                'detail': "Server identifies connection by Connection ID, not IP"
            },
            {
                'description': "Server initiates path validation",
                'detail': "Sends PATH_CHALLENGE to new IP address"
            },
            {
                'description': "Client responds with PATH_RESPONSE",
                'detail': "Confirms ownership of new network path"
            },
            {
                'description': "Server switches to new path",
                'detail': "Connection migrated successfully without handshake"
            }
        ]
    ),

    MigrationScenario(
        name="Client Address Change (ISP Reassignment)",
        description=(
            "When a client's ISP changes their IP address (e.g., DHCP lease renewal, "
            "connection reset), QUIC can maintain the connection without re-establishing."
        ),
        steps=[
            {
                'description': "Client using IP address 203.0.113.10",
                'detail': "Stable QUIC connection with server"
            },
            {
                'description': "ISP assigns new IP address 203.0.113.25",
                'detail': "Could be due to DHCP renewal or connection reset"
            },
            {
                'description': "Client continues using same Connection ID",
                'detail': "QUIC connection state remains intact"
            },
            {
                'description': "Server detects address change and validates",
                'detail': "Ensures new address is legitimate"
            },
            {
                'description': "Connection migrates to new address",
                'detail': "Application layer unaware of the change"
            }
        ]
    ),

    MigrationScenario(
        name="Server-Preferred Address Migration",
        description=(
            "Server can advertise a preferred address for the client to migrate to. "
            "This is useful for load balancing or when the server has multiple "
            "network interfaces."
        ),
        steps=[
            {
                'description': "Client connects to server's public address",
                'detail': "Initial connection to load balancer or public IP"
            },
            {
                'description': "Server sends PREFERRED_ADDRESS transport parameter",
                'detail': "Provides alternative address for better routing"
            },
            {
                'description': "Client validates server's preferred address",
                'detail': "Sends PATH_CHALLENGE to new address"
            },
            {
                'description': "Server responds from preferred address",
                'detail': "PATH_RESPONSE confirms availability"
            },
            {
                'description': "Client migrates connection to preferred address",
                'detail': "Better routing or direct connection established"
            }
        ]
    ),

    MigrationScenario(
        name="Multi-Path QUIC (Future Extension)",
        description=(
            "While not in the base QUIC spec, multi-path extensions allow using "
            "multiple network paths simultaneously for redundancy and performance."
        ),
        steps=[
            {
                'description': "Client has WiFi and Cellular connections",
                'detail': "Both interfaces available simultaneously"
            },
            {
                'description': "Establish primary path via WiFi",
                'detail': "Main data transfer uses WiFi"
            },
            {
                'description': "Probe cellular path in background",
                'detail': "Keep cellular path validated and ready"
            },
            {
                'description': "WiFi becomes congested or unreliable",
                'detail': "Detected via RTT increase or packet loss"
            },
            {
                'description': "Seamlessly shift traffic to cellular path",
                'detail': "No interruption in data flow"
            },
            {
                'description': "Can split traffic across both paths",
                'detail': "Aggregate bandwidth or provide redundancy"
            }
        ]
    )
]


def print_migration_concepts():
    """Print key QUIC migration concepts"""
    print("\n" + "="*70)
    print("🔑 KEY QUIC MIGRATION CONCEPTS")
    print("="*70 + "\n")

    concepts = {
        "Connection ID": (
            "Unlike TCP which identifies connections by 4-tuple (src IP, src port, "
            "dst IP, dst port), QUIC uses Connection IDs. This allows the IP addresses "
            "and ports to change while maintaining the same connection."
        ),
        "Path Validation": (
            "Before using a new network path, QUIC validates it using PATH_CHALLENGE "
            "and PATH_RESPONSE frames. This prevents address spoofing attacks."
        ),
        "Connection Migration": (
            "The process of changing the network path (IP/port) of an existing QUIC "
            "connection. Only the client can initiate migration (server can suggest)."
        ),
        "NAT Rebinding": (
            "When a NAT device changes the external port mapping, causing packets to "
            "arrive from a different source port. This is the simplest form of migration."
        ),
        "Active Migration": (
            "Client intentionally changes network paths (e.g., WiFi to cellular). "
            "Requires path validation before switching."
        ),
        "Preferred Address": (
            "Server can advertise a preferred address during handshake for the client "
            "to migrate to, useful for load balancing."
        ),
        "Connection ID Lifecycle": (
            "QUIC endpoints can issue new Connection IDs to peer, allowing smooth "
            "rotation and privacy benefits."
        ),
        "Zero-RTT Migration": (
            "After path validation completes, future migrations to validated paths "
            "can happen without additional RTT overhead."
        )
    }

    for concept, explanation in concepts.items():
        print(f"📌 {concept}")
        print(f"   {explanation}\n")

    print("="*70 + "\n")


def print_migration_benefits():
    """Print benefits of QUIC connection migration"""
    print("\n" + "="*70)
    print("✨ BENEFITS OF QUIC CONNECTION MIGRATION")
    print("="*70 + "\n")

    benefits = [
        ("Seamless Network Switching",
         "Move between WiFi, cellular, or ethernet without connection drops"),
        ("Mobile Resilience",
         "Perfect for mobile devices that frequently change networks"),
        ("No Connection Re-establishment",
         "Avoid expensive handshakes and connection setup overhead"),
        ("Maintained Application State",
         "Application continues without knowing about network changes"),
        ("Reduced Latency",
         "No need to wait for TCP handshake + TLS handshake again"),
        ("Better User Experience",
         "Video calls, downloads, games continue uninterrupted"),
        ("Privacy Benefits",
         "Connection IDs can be rotated to prevent tracking"),
        ("Load Balancing",
         "Servers can guide clients to better network paths"),
    ]

    for i, (benefit, description) in enumerate(benefits, 1):
        print(f"{i}. {benefit}")
        print(f"   → {description}\n")

    print("="*70 + "\n")


def interactive_menu():
    """Display interactive menu for exploring scenarios"""
    print("\n" + "="*70)
    print("🚀 QUIC CONNECTION MIGRATION - INTERACTIVE DEMO")
    print("="*70 + "\n")

    while True:
        print("\nWhat would you like to explore?")
        print("\n1. 📚 Learn about QUIC Migration Concepts")
        print("2. ✨ See Benefits of Connection Migration")
        print("3. 🎯 Explore Migration Scenarios:")
        for i, scenario in enumerate(SCENARIOS, 1):
            print(f"   {3}.{i} - {scenario.name}")
        print("4. 🏃 Run Live Demo (requires server running)")
        print("5. 📖 View All Scenarios")
        print("0. 🚪 Exit\n")

        choice = input("Enter your choice: ").strip()

        if choice == "0":
            print("\n👋 Goodbye!\n")
            break
        elif choice == "1":
            print_migration_concepts()
        elif choice == "2":
            print_migration_benefits()
        elif choice == "5":
            for scenario in SCENARIOS:
                scenario.explain()
                input("\nPress Enter to continue...")
        elif choice.startswith("3."):
            try:
                scenario_idx = int(choice.split(".")[1]) - 1
                if 0 <= scenario_idx < len(SCENARIOS):
                    SCENARIOS[scenario_idx].explain()
                else:
                    print("❌ Invalid scenario number")
            except:
                print("❌ Invalid input")
        elif choice == "4":
            print("\n🏃 To run the live demo:")
            print("   1. In terminal 1: python quic_server.py")
            print("   2. In terminal 2: python quic_client.py")
            print("   3. Watch the migration events in both terminals!\n")
        else:
            print("❌ Invalid choice. Please try again.")


if __name__ == "__main__":
    try:
        interactive_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!\n")
