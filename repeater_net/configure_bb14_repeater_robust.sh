#!/bin/bash
#
# Robust configuration script for bb14 (REPEATER node)
# Handles device reboots during configuration
#

set -e

PORT="${1:-/dev/cu.usbmodem9C139EE7BB141}"

echo "=========================================="
echo "Configuring bb14 as REPEATER"
echo "Port: $PORT"
echo "=========================================="
echo ""

wait_for_device() {
    local port=$1
    local max_attempts=10
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if python3 -m meshtastic --port "$port" --info >/dev/null 2>&1; then
            echo "✅ Device ready"
            sleep 2
            return 0
        fi
        echo "   Waiting for device... ($attempt/$max_attempts)"
        sleep 3
        attempt=$((attempt + 1))
    done
    return 1
}

configure_with_retry() {
    local port=$1
    local setting=$2
    local value=$3
    local description=$4
    local max_attempts=3
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        echo "   Attempt $attempt: Setting $description..."
        if timeout 10 python3 -m meshtastic --port "$port" --set "$setting" "$value" 2>&1 | grep -q "Set\|Writing"; then
            echo "✅ $description set successfully"
            sleep 3  # Wait for potential reboot
            wait_for_device "$port" && return 0
        fi
        echo "   Retrying..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "⚠️  Warning: $description may not have been set (device may have rebooted)"
    wait_for_device "$port"
    return 0
}

# Step 1: Verify initial connection
echo "1. Verifying connection to bb14..."
if ! python3 -m meshtastic --port "$PORT" --info | grep -q "bb14"; then
    echo "❌ Error: Could not connect to bb14 on $PORT"
    exit 1
fi
echo "✅ Connected"
echo ""

# Step 2: Set REPEATER role
echo "2. Setting device role to REPEATER..."
configure_with_retry "$PORT" "device.role" "REPEATER" "REPEATER role"
echo ""

# Step 3: Set rebroadcast mode
echo "3. Setting rebroadcast mode to ALL..."
configure_with_retry "$PORT" "device.rebroadcast_mode" "ALL" "Rebroadcast mode"
echo ""

# Step 4: Set LoRa region
echo "4. Setting LoRa region to UA_433..."
configure_with_retry "$PORT" "lora.region" "UA_433" "LoRa region"
echo ""

# Step 5: Set modem preset
echo "5. Setting modem preset to SHORT_FAST..."
configure_with_retry "$PORT" "lora.modem_preset" "SHORT_FAST" "Modem preset"
echo ""

# Step 6: Set hop limit
echo "6. Setting hop limit to 3..."
configure_with_retry "$PORT" "lora.hop_limit" "3" "Hop limit"
echo ""

# Step 7: Enable TX
echo "7. Ensuring TX is enabled..."
configure_with_retry "$PORT" "lora.tx_enabled" "true" "TX enabled"
echo ""

# Step 8: Get PRIMARY channel URL
echo "8. Getting PRIMARY channel URL..."
wait_for_device "$PORT"
CHANNEL_URL=$(python3 -m meshtastic --port "$PORT" --info 2>/dev/null | grep "Primary channel URL" | cut -d: -f2- | xargs)

if [ -z "$CHANNEL_URL" ]; then
    echo "⚠️  Warning: Could not get channel URL"
else
    echo "✅ PRIMARY channel URL: $CHANNEL_URL"
    echo "$CHANNEL_URL" > primary_channel_url.txt
    echo "✅ Channel URL saved to primary_channel_url.txt"
fi
echo ""

# Final verification
echo "9. Verifying final configuration..."
wait_for_device "$PORT"
echo ""
python3 -m meshtastic --port "$PORT" --info | grep -E "role|rebroadcast|region|modemPreset|hop" || true
echo ""

echo "=========================================="
echo "✅ bb14 REPEATER configuration complete!"
echo "=========================================="
echo ""
echo "Configuration summary:"
echo "  Role: REPEATER"
echo "  Rebroadcast Mode: ALL"
echo "  Region: UA_433 (433 MHz)"
echo "  Modem Preset: SHORT_FAST"
echo "  Hop Limit: 3"
if [ -n "$CHANNEL_URL" ]; then
    echo "  PRIMARY Channel URL: $CHANNEL_URL"
fi
echo ""
echo "Next steps:"
echo "  1. Configure 666c client: ./configure_666c_client.sh"
echo "  2. Configure 7284 client: ./configure_7284_client.sh"
echo ""

