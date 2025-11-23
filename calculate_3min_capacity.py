#!/usr/bin/env python3
"""
Calculate maximum file size that can be transmitted in 3 minutes
Based on actual measured Meshtastic performance
"""

import json

# Measured performance from speed tests
MEASURED_THROUGHPUT_KBPS = 11.48  # From speed test results
MEASURED_MESSAGES_PER_SEC = 9.56  # From speed test results
MEASURED_BYTES_PER_SEC = 1434.51  # From speed test results
MEASURED_LATENCY_MS = 105  # Average latency per message

# Theoretical limits from documentation
SHORT_FAST_THEORETICAL_KBPS = 10.94  # From Meshtastic docs
MAX_MESSAGE_SIZE = 240  # bytes (approximate, with overhead)
MESSAGE_OVERHEAD = 50  # bytes (approximate overhead per message)

# Time period
TIME_MINUTES = 3
TIME_SECONDS = TIME_MINUTES * 60

print("="*70)
print("MESHTASTIC 3-MINUTE TRANSMISSION CAPACITY CALCULATION")
print("="*70)
print(f"\nTime Period: {TIME_MINUTES} minutes ({TIME_SECONDS} seconds)")
print(f"Configuration: UA_433, SHORT_FAST preset")
print()

# Calculation 1: Based on measured throughput
print("="*70)
print("CALCULATION 1: Based on Measured Performance")
print("="*70)
print(f"Measured Throughput: {MEASURED_THROUGHPUT_KBPS:.2f} kbps")
print(f"Measured Messages/sec: {MEASURED_MESSAGES_PER_SEC:.2f}")
print(f"Measured Bytes/sec: {MEASURED_BYTES_PER_SEC:.2f}")
print()

# Calculate capacity
measured_bits = MEASURED_THROUGHPUT_KBPS * 1000 * TIME_SECONDS
measured_bytes = measured_bits / 8
measured_kb = measured_bytes / 1024
measured_mb = measured_kb / 1024

print(f"Capacity in {TIME_MINUTES} minutes:")
print(f"  Bits:     {measured_bits:,.0f}")
print(f"  Bytes:    {measured_bytes:,.0f}")
print(f"  KB:       {measured_kb:,.2f}")
print(f"  MB:       {measured_mb:.4f}")
print()

# Calculation 2: Based on message rate
print("="*70)
print("CALCULATION 2: Based on Message Rate")
print("="*70)
max_messages = MEASURED_MESSAGES_PER_SEC * TIME_SECONDS
print(f"Maximum messages in {TIME_MINUTES} minutes: {max_messages:,.0f}")
print()

# Calculate with message size limits
effective_message_size = MAX_MESSAGE_SIZE - MESSAGE_OVERHEAD
total_payload_bytes = max_messages * effective_message_size
total_payload_kb = total_payload_bytes / 1024
total_payload_mb = total_payload_kb / 1024

print(f"With message size limit ({MAX_MESSAGE_SIZE} bytes, {MESSAGE_OVERHEAD} bytes overhead):")
print(f"  Effective payload per message: {effective_message_size} bytes")
print(f"  Total payload capacity: {total_payload_bytes:,.0f} bytes")
print(f"  Total payload capacity: {total_payload_kb:,.2f} KB")
print(f"  Total payload capacity: {total_payload_mb:.4f} MB")
print()

# Calculation 3: Theoretical maximum (SHORT_FAST)
print("="*70)
print("CALCULATION 3: Theoretical Maximum (SHORT_FAST)")
print("="*70)
theoretical_bits = SHORT_FAST_THEORETICAL_KBPS * 1000 * TIME_SECONDS
theoretical_bytes = theoretical_bits / 8
theoretical_kb = theoretical_bytes / 1024
theoretical_mb = theoretical_kb / 1024

print(f"Theoretical SHORT_FAST capacity ({SHORT_FAST_THEORETICAL_KBPS} kbps):")
print(f"  Bits:     {theoretical_bits:,.0f}")
print(f"  Bytes:    {theoretical_bytes:,.0f}")
print(f"  KB:       {theoretical_kb:,.2f}")
print(f"  MB:       {theoretical_mb:.4f}")
print()

# Summary
print("="*70)
print("SUMMARY")
print("="*70)
print(f"Recommended maximum file size for {TIME_MINUTES}-minute transmission:")
print(f"  Based on measured performance: {measured_mb:.4f} MB ({measured_kb:.2f} KB)")
print(f"  Based on message rate:         {total_payload_mb:.4f} MB ({total_payload_kb:.2f} KB)")
print(f"  Theoretical maximum:            {theoretical_mb:.4f} MB ({theoretical_kb:.2f} KB)")
print()
print(f"Practical recommendation: {min(measured_mb, total_payload_mb):.4f} MB")
print(f"  ({min(measured_kb, total_payload_kb):.2f} KB)")
print()

# Additional metrics
print("="*70)
print("ADDITIONAL METRICS")
print("="*70)
print(f"Time per message: {MEASURED_LATENCY_MS:.0f} ms")
print(f"Messages per minute: {MEASURED_MESSAGES_PER_SEC * 60:.1f}")
print(f"Bytes per minute: {MEASURED_BYTES_PER_SEC * 60:,.0f}")
print(f"KB per minute: {(MEASURED_BYTES_PER_SEC * 60) / 1024:.2f}")
print()

# Real-world considerations
print("="*70)
print("REAL-WORLD CONSIDERATIONS")
print("="*70)
print("⚠️  These calculations assume:")
print("   - 100% channel availability")
print("   - No interference")
print("   - No retransmissions needed")
print("   - Optimal signal conditions (SNR > 10 dB)")
print()
print("📊 Actual capacity may be lower due to:")
print("   - Background mesh traffic (node info, position updates)")
print("   - Channel utilization from other nodes")
print("   - Retransmissions on errors")
print("   - Protocol overhead")
print()
print("💡 Recommended: Use 70-80% of calculated capacity for reliability")
recommended_capacity = min(measured_mb, total_payload_mb) * 0.75
recommended_capacity_kb = min(measured_kb, total_payload_kb) * 0.75
print(f"   Safe capacity: {recommended_capacity:.4f} MB ({recommended_capacity_kb:.2f} KB)")
print()

