#!/bin/bash
#
# Check signal quality from all nodes after bb14 repositioning
#

echo "=========================================="
echo "SIGNAL QUALITY CHECK - After bb14 Move"
echo "=========================================="
echo ""

echo "1. bb14 (REPEATER) - 192.168.0.15"
echo "----------------------------------------"
python3 ../query_node_neighbors.py --ip 192.168.0.15 2>&1 | grep -A15 "REMOTE LORA NODES" | grep -E "7284|666c|SNR|Node ID"
echo ""

echo "2. 7284 (CLIENT) - 192.168.0.10"
echo "----------------------------------------"
python3 ../query_node_neighbors.py --ip 192.168.0.10 2>&1 | grep -A15 "REMOTE LORA NODES" | grep -E "bb14|666c|SNR|Node ID"
echo ""

echo "3. 666c (CLIENT) - 192.168.0.11"
echo "----------------------------------------"
python3 ../query_node_neighbors.py --ip 192.168.0.11 2>&1 | grep -A15 "REMOTE LORA NODES" | grep -E "bb14|7284|SNR|Node ID"
echo ""

echo "=========================================="
echo "SIGNAL QUALITY SUMMARY"
echo "=========================================="
echo ""

# Extract SNR values
BB14_TO_7284=$(python3 ../query_node_neighbors.py --ip 192.168.0.15 2>&1 | grep -A5 "7284" | grep "SNR" | awk '{print $2}')
BB14_TO_666C=$(python3 ../query_node_neighbors.py --ip 192.168.0.15 2>&1 | grep -A5 "666c" | grep "SNR" | awk '{print $2}')
7284_TO_BB14=$(python3 ../query_node_neighbors.py --ip 192.168.0.10 2>&1 | grep -A5 "bb14" | grep "SNR" | awk '{print $2}')
7284_TO_666C=$(python3 ../query_node_neighbors.py --ip 192.168.0.10 2>&1 | grep -A5 "666c" | grep "SNR" | awk '{print $2}')
666C_TO_BB14=$(python3 ../query_node_neighbors.py --ip 192.168.0.11 2>&1 | grep -A5 "bb14" | grep "SNR" | awk '{print $2}')
666C_TO_7284=$(python3 ../query_node_neighbors.py --ip 192.168.0.11 2>&1 | grep -A5 "7284" | grep "SNR" | awk '{print $2}')

echo "bb14 → 7284: ${BB14_TO_7284:-N/A}"
echo "bb14 → 666c: ${BB14_TO_666C:-N/A}"
echo "7284 → bb14: ${7284_TO_BB14:-N/A}"
echo "7284 → 666c: ${7284_TO_666C:-N/A}"
echo "666c → bb14: ${666C_TO_BB14:-N/A}"
echo "666c → 7284: ${666C_TO_7284:-N/A}"
echo ""

