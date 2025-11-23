# Meshtastic Repeater Network Configuration

This directory contains configuration scripts for a 3-node Meshtastic repeater network:

- **bb14**: REPEATER node (relays messages between clients)
- **666c**: CLIENT node (IP: 192.168.0.11)
- **7284**: CLIENT node (IP: 192.168.0.10)

## Network Architecture

```
[7284] ----(LoRa)----> [bb14] ----(LoRa)----> [666c]
CLIENT                REPEATER                CLIENT
```

**Routing Pattern:**
- 7284 sends packets to bb14
- bb14 relays packets to 666c
- 666c and 7284 do NOT see each other directly (isolated)

## Configuration Order

**IMPORTANT:** Configure nodes in this order:

1. **First:** Configure bb14 (repeater) - generates channel URL
2. **Second:** Configure 666c (client) - uses channel URL from bb14
3. **Third:** Configure 7284 (client) - uses channel URL from bb14

## Prerequisites

- All nodes must be powered on
- bb14 must be connected via USB serial port
- 666c and 7284 must be connected to Wi-Fi (TCP/IP enabled)
- Python3 and meshtastic CLI installed: `pip3 install meshtastic`

## Usage

### Step 1: Configure bb14 (Repeater)

```bash
# Auto-detect bb14 USB port
./configure_bb14_repeater.sh

# Or specify port manually
./configure_bb14_repeater.sh /dev/cu.usbserial-XXXX
```

This script will:
- Set bb14 role to REPEATER
- Set rebroadcast mode to ALL
- Configure LoRa: UA_433 region, SHORT_FAST preset
- Set hop limit to 3
- Generate `primary_channel_url.txt` for clients

### Step 2: Configure 666c (Client)

```bash
# Uses channel URL from primary_channel_url.txt (generated in step 1)
./configure_666c_client.sh

# Or specify channel URL manually
./configure_666c_client.sh "https://meshtastic.org/e/#..."
```

This script will:
- Set 666c role to CLIENT
- Set rebroadcast mode to ALL
- Configure LoRa: UA_433 region, SHORT_FAST preset (matches repeater)
- Set hop limit to 3
- Synchronize PRIMARY channel with bb14

### Step 3: Configure 7284 (Client)

```bash
# Uses channel URL from primary_channel_url.txt (generated in step 1)
./configure_7284_client.sh

# Or specify channel URL manually
./configure_7284_client.sh "https://meshtastic.org/e/#..."
```

This script will:
- Set 7284 role to CLIENT
- Set rebroadcast mode to ALL
- Configure LoRa: UA_433 region, SHORT_FAST preset (matches repeater)
- Set hop limit to 3
- Synchronize PRIMARY channel with bb14

## Configuration Details

### Shared Settings (All Nodes)

- **LoRa Region:** UA_433 (433 MHz - Ukraine)
- **Modem Preset:** SHORT_FAST (fastest data speed)
- **Hop Limit:** 3
- **PRIMARY Channel:** Same channel URL (synchronized)
- **TX Enabled:** Yes

### bb14 (Repeater) Specific

- **Role:** REPEATER (always rebroadcasts, higher routing priority)
- **Rebroadcast Mode:** ALL
- **Connection:** USB serial port

### 666c & 7284 (Clients) Specific

- **Role:** CLIENT
- **Rebroadcast Mode:** ALL
- **Connection:** TCP/IP (192.168.0.11 and 192.168.0.10)

## Physical Placement

For optimal routing isolation:

1. **bb14** should be positioned between 7284 and 666c
2. **7284** should be within range of bb14, ideally out of direct range of 666c
3. **666c** should be within range of bb14, ideally out of direct range of 7284

Even if 7284 and 666c can hear each other, the REPEATER role gives bb14 higher priority in routing decisions.

## Verification

After configuration, verify the setup:

```bash
# Check bb14 (repeater)
python3 -m meshtastic --port <bb14_port> --info | grep -E "role|rebroadcast|region"

# Check 666c (client)
python3 -m meshtastic --host 192.168.0.11 --info | grep -E "role|rebroadcast|region"

# Check 7284 (client)
python3 -m meshtastic --host 192.168.0.10 --info | grep -E "role|rebroadcast|region"

# Query visible nodes from each device
python3 ../query_node_neighbors.py --ip 192.168.0.10  # From 7284
python3 ../query_node_neighbors.py --ip 192.168.0.11  # From 666c
```

## Testing

1. **Send test message from 7284 to 666c:**
   ```bash
   python3 -m meshtastic --host 192.168.0.10 --sendtext "Test from 7284" --dest !9ee8666c
   ```

2. **Send test message from 666c to 7284:**
   ```bash
   python3 -m meshtastic --host 192.168.0.11 --sendtext "Test from 666c" --dest !9ee87284
   ```

3. **Monitor routing through bb14:**
   - Messages should route: 7284 → bb14 → 666c
   - Messages should route: 666c → bb14 → 7284

## Troubleshooting

### Nodes can't see each other

- Verify all nodes share the same PRIMARY channel URL
- Check that LoRa region and modem preset match on all nodes
- Ensure bb14 is set to REPEATER role
- Check physical placement (all nodes should be in range of bb14)

### Direct communication between clients

- If 7284 and 666c can hear each other directly, routing will still prefer bb14 (REPEATER has higher priority)
- For strict isolation, ensure physical separation or use different channels (not recommended)

### Configuration not applying

- Wait a few seconds after each configuration command
- Restart devices if needed: `python3 -m meshtastic --port <port> --reboot`
- Verify connection: `python3 -m meshtastic --port <port> --info`

## Files

- `configure_bb14_repeater.sh` - Configure bb14 as REPEATER
- `configure_666c_client.sh` - Configure 666c as CLIENT
- `configure_7284_client.sh` - Configure 7284 as CLIENT
- `primary_channel_url.txt` - Generated channel URL (created by bb14 script)
- `README.md` - This file

