#!/usr/bin/env python3
"""
Generate HTML table with Tailwind CSS for all-device-pairs speed test results
"""

import json
import sys
from datetime import datetime


def generate_html_table(json_file):
    """Generate beautiful HTML table from JSON results"""
    
    # Load results
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    results = data.get('results', [])
    timestamp = data.get('timestamp', datetime.now().isoformat())
    
    if not results:
        print("No results found in JSON file")
        return
    
    # Calculate statistics
    total_tests = len(results)
    successful = len([r for r in results if r.get('successful', 0) > 0])
    avg_throughput = sum(r.get('throughput_kbps', 0) for r in results if r.get('throughput_kbps', 0) > 0) / successful if successful > 0 else 0
    
    # Build device list
    devices = set()
    for result in results:
        devices.add(result.get('from_name', 'Unknown'))
        devices.add(result.get('to_name', 'Unknown'))
    devices = sorted(list(devices))
    
    # Build matrix
    matrix = {}
    for result in results:
        key = (result.get('from_name', 'Unknown'), result.get('to_name', 'Unknown'))
        matrix[key] = {
            'throughput': result.get('throughput_kbps', 0),
            'success_rate': (result.get('successful', 0) / result.get('message_count', 30)) * 100 if result.get('message_count', 30) > 0 else 0,
            'avg_time': result.get('avg_time', 0),
            'snr': result.get('snr'),
            'successful': result.get('successful', 0),
            'total': result.get('message_count', 30)
        }
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Meshtastic All-Device-Pairs Speed Test Results</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        @keyframes slideIn {{
            from {{ opacity: 0; transform: translateX(-20px); }}
            to {{ opacity: 1; transform: translateX(0); }}
        }}
        .fade-in {{
            animation: fadeIn 0.6s ease-out;
        }}
        .slide-in {{
            animation: slideIn 0.5s ease-out;
        }}
        .table-row {{
            transition: all 0.3s ease;
        }}
        .table-row:hover {{
            transform: scale(1.01);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }}
        .metric-card {{
            transition: all 0.3s ease;
        }}
        .metric-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
        }}
        .throughput-cell {{
            font-weight: 600;
        }}
        .throughput-excellent {{ color: #10b981; }}
        .throughput-good {{ color: #f59e0b; }}
        .throughput-poor {{ color: #ef4444; }}
    </style>
</head>
<body class="bg-gradient-to-br from-gray-50 to-gray-100 min-h-screen py-8 px-4">
    <div class="max-w-7xl mx-auto">
        <!-- Header -->
        <div class="text-center mb-8 fade-in">
            <h1 class="text-5xl font-bold text-gray-800 mb-2">📡 Meshtastic Speed Test</h1>
            <p class="text-xl text-gray-600">All-Device-Pairs Transmission Analysis</p>
            <p class="text-sm text-gray-500 mt-2">Generated: {datetime.fromisoformat(timestamp).strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>

        <!-- Summary Cards -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div class="metric-card bg-white rounded-xl shadow-lg p-6 border-l-4 border-blue-500 slide-in" style="animation-delay: 0.1s">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-sm font-medium text-gray-600">Average Throughput</p>
                        <p class="text-3xl font-bold text-gray-800 mt-2">{avg_throughput:.2f} kbps</p>
                    </div>
                    <div class="text-4xl">⚡</div>
                </div>
            </div>
            
            <div class="metric-card bg-white rounded-xl shadow-lg p-6 border-l-4 border-green-500 slide-in" style="animation-delay: 0.2s">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-sm font-medium text-gray-600">Success Rate</p>
                        <p class="text-3xl font-bold text-gray-800 mt-2">{(successful/total_tests*100):.1f}%</p>
                    </div>
                    <div class="text-4xl">✅</div>
                </div>
            </div>
            
            <div class="metric-card bg-white rounded-xl shadow-lg p-6 border-l-4 border-purple-500 slide-in" style="animation-delay: 0.3s">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-sm font-medium text-gray-600">Total Tests</p>
                        <p class="text-3xl font-bold text-gray-800 mt-2">{total_tests}</p>
                    </div>
                    <div class="text-4xl">📊</div>
                </div>
            </div>
        </div>

        <!-- Speed Matrix Table -->
        <div class="bg-white rounded-xl shadow-xl overflow-hidden fade-in mb-8" style="animation-delay: 0.4s">
            <div class="px-6 py-4 bg-gradient-to-r from-blue-600 to-blue-700">
                <h2 class="text-2xl font-bold text-white">Transmission Speed Matrix (kbps)</h2>
            </div>
            
            <div class="overflow-x-auto p-6">
                <table class="w-full">
                    <thead>
                        <tr class="bg-gray-50">
                            <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider border-b">From \\ To</th>
"""
    
    # Table headers
    for device in devices:
        html += f"""                            <th class="px-4 py-3 text-center text-xs font-semibold text-gray-700 uppercase tracking-wider border-b">{device}</th>
"""
    
    html += """                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-200">
"""
    
    # Table rows
    for i, from_dev in enumerate(devices):
        html += f"""                        <tr class="table-row bg-white hover:bg-gray-50" style="animation-delay: {0.5 + i*0.1}s">
                            <td class="px-4 py-4 whitespace-nowrap text-sm font-semibold text-gray-900 border-r">{from_dev}</td>
"""
        for to_dev in devices:
            if from_dev == to_dev:
                html += """                            <td class="px-4 py-4 text-center text-sm text-gray-400">---</td>
"""
            else:
                key = (from_dev, to_dev)
                if key in matrix:
                    data = matrix[key]
                    throughput = data['throughput']
                    success_rate = data['success_rate']
                    
                    # Color coding
                    if throughput >= 10:
                        color_class = "throughput-excellent"
                    elif throughput >= 8:
                        color_class = "throughput-good"
                    else:
                        color_class = "throughput-poor"
                    
                    html += f"""                            <td class="px-4 py-4 text-center">
                                <div class="throughput-cell {color_class}">{throughput:.2f}</div>
                                <div class="text-xs text-gray-500 mt-1">{success_rate:.0f}%</div>
                            </td>
"""
                else:
                    html += """                            <td class="px-4 py-4 text-center text-sm text-gray-400">N/A</td>
"""
        
        html += """                        </tr>
"""
    
    html += """                    </tbody>
                </table>
            </div>
        </div>

        <!-- Detailed Results Table -->
        <div class="bg-white rounded-xl shadow-xl overflow-hidden fade-in" style="animation-delay: 0.6s">
            <div class="px-6 py-4 bg-gradient-to-r from-green-600 to-green-700">
                <h2 class="text-2xl font-bold text-white">Detailed Test Results</h2>
            </div>
            
            <div class="overflow-x-auto">
                <table class="w-full">
                    <thead class="bg-gray-50">
                        <tr>
                            <th class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">From → To</th>
                            <th class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Success</th>
                            <th class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Avg Time</th>
                            <th class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Throughput</th>
                            <th class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">SNR</th>
                            <th class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Status</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-200">
"""
    
    # Detailed rows
    for i, result in enumerate(results):
        from_name = result.get('from_name', 'Unknown')
        to_name = result.get('to_name', 'Unknown')
        successful = result.get('successful', 0)
        total = result.get('message_count', 30)
        success_rate = (successful / total * 100) if total > 0 else 0
        avg_time = result.get('avg_time', 0)
        throughput = result.get('throughput_kbps', 0)
        snr = result.get('snr')
        
        # Status
        if success_rate >= 95:
            status_color = "bg-green-100 text-green-800"
            status_text = "Excellent"
        elif success_rate >= 80:
            status_color = "bg-yellow-100 text-yellow-800"
            status_text = "Good"
        else:
            status_color = "bg-red-100 text-red-800"
            status_text = "Poor"
        
        html += f"""                        <tr class="table-row bg-white hover:bg-gray-50" style="animation-delay: {0.7 + i*0.05}s">
                            <td class="px-6 py-4 whitespace-nowrap">
                                <div class="flex items-center">
                                    <div class="text-sm font-medium text-gray-900">{from_name}</div>
                                    <div class="mx-2 text-gray-400">→</div>
                                    <div class="text-sm font-medium text-gray-900">{to_name}</div>
                                </div>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap">
                                <div class="text-sm text-gray-900">{successful}/{total}</div>
                                <div class="text-xs text-gray-500">{success_rate:.1f}%</div>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap">
                                <div class="text-sm text-gray-900">{avg_time*1000:.1f} ms</div>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap">
                                <div class="text-sm font-semibold text-blue-600">{throughput:.2f} kbps</div>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap">
"""
        if snr is not None:
            snr_color = "text-green-600" if snr > 10 else "text-yellow-600" if snr > 5 else "text-red-600"
            html += f"""                                <span class="text-sm {snr_color} font-semibold">{snr:.2f} dB</span>
"""
        else:
            html += """                                <span class="text-xs text-gray-400">N/A</span>
"""
        html += f"""                            </td>
                            <td class="px-6 py-4 whitespace-nowrap">
                                <span class="px-2 py-1 text-xs font-semibold rounded-full {status_color}">
                                    {status_text}
                                </span>
                            </td>
                        </tr>
"""
    
    html += """                    </tbody>
                </table>
            </div>
        </div>

        <!-- Footer -->
        <div class="mt-8 text-center text-gray-500 text-sm fade-in">
            <p>Meshtastic Mesh Network Performance Test</p>
            <p class="mt-2">Configuration: UA_433, SHORT_FAST preset | 30 messages per test</p>
        </div>
    </div>
</body>
</html>
"""
    
    return html


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 generate_speed_table_html.py <json_file>")
        sys.exit(1)
    
    json_file = sys.argv[1]
    html = generate_html_table(json_file)
    
    output_file = "mesh_speed_table.html"
    with open(output_file, 'w') as f:
        f.write(html)
    
    print(f"HTML table generated: {output_file}")

