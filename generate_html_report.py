#!/usr/bin/env python3
"""
Generate HTML report with Tailwind CSS for Meshtastic file transfer tests
"""

import json
import sys
from datetime import datetime


def generate_html_report(test_results):
    """Generate beautiful HTML report with Tailwind CSS"""
    
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Meshtastic File Transfer Speed Test Results</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes slideIn {
            from { opacity: 0; transform: translateX(-20px); }
            to { opacity: 1; transform: translateX(0); }
        }
        .fade-in {
            animation: fadeIn 0.6s ease-out;
        }
        .slide-in {
            animation: slideIn 0.5s ease-out;
        }
        .table-row {
            transition: all 0.3s ease;
        }
        .table-row:hover {
            transform: scale(1.02);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
        }
        .metric-card {
            transition: all 0.3s ease;
        }
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 30px rgba(0, 0, 0, 0.15);
        }
    </style>
</head>
<body class="bg-gradient-to-br from-gray-50 to-gray-100 min-h-screen py-8 px-4">
    <div class="max-w-7xl mx-auto">
        <!-- Header -->
        <div class="text-center mb-8 fade-in">
            <h1 class="text-5xl font-bold text-gray-800 mb-2">📡 Meshtastic File Transfer Test</h1>
            <p class="text-xl text-gray-600">Performance Analysis & Signal Quality Report</p>
            <p class="text-sm text-gray-500 mt-2">Generated: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
        </div>

        <!-- Summary Cards -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
"""
    
    # Calculate summary statistics
    total_tests = len(test_results)
    avg_throughput = sum(r.get('throughput_kbps', 0) for r in test_results) / total_tests if total_tests > 0 else 0
    avg_snr = sum(r.get('snr', 0) for r in test_results if r.get('snr')) / len([r for r in test_results if r.get('snr')]) if any(r.get('snr') for r in test_results) else 0
    total_success = sum(r.get('messages_successful', 0) for r in test_results)
    total_sent = sum(r.get('messages_sent', 0) for r in test_results)
    success_rate = (total_success / total_sent * 100) if total_sent > 0 else 0
    
    html += f"""
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
                        <p class="text-3xl font-bold text-gray-800 mt-2">{success_rate:.1f}%</p>
                    </div>
                    <div class="text-4xl">✅</div>
                </div>
            </div>
            
            <div class="metric-card bg-white rounded-xl shadow-lg p-6 border-l-4 border-purple-500 slide-in" style="animation-delay: 0.3s">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-sm font-medium text-gray-600">Average SNR</p>
                        <p class="text-3xl font-bold text-gray-800 mt-2">{avg_snr:.2f} dB</p>
                    </div>
                    <div class="text-4xl">📶</div>
                </div>
            </div>
            
            <div class="metric-card bg-white rounded-xl shadow-lg p-6 border-l-4 border-orange-500 slide-in" style="animation-delay: 0.4s">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-sm font-medium text-gray-600">Total Tests</p>
                        <p class="text-3xl font-bold text-gray-800 mt-2">{total_tests}</p>
                    </div>
                    <div class="text-4xl">📊</div>
                </div>
            </div>
        </div>

        <!-- Detailed Results Table -->
        <div class="bg-white rounded-xl shadow-xl overflow-hidden fade-in" style="animation-delay: 0.5s">
            <div class="px-6 py-4 bg-gradient-to-r from-blue-600 to-blue-700">
                <h2 class="text-2xl font-bold text-white">Detailed Test Results</h2>
            </div>
            
            <div class="overflow-x-auto">
                <table class="w-full">
                    <thead class="bg-gray-50">
                        <tr>
                            <th class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">From → To</th>
                            <th class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">File Size</th>
                            <th class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Time</th>
                            <th class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Throughput</th>
                            <th class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Messages</th>
                            <th class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">SNR</th>
                            <th class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Status</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-200">
"""
    
    # Generate table rows
    for i, result in enumerate(test_results):
        from_node = result.get('port', 'Unknown').split('/')[-1]
        to_node = result.get('target_node', 'Unknown')
        file_size = result.get('file_size_mb', 0)
        total_time = result.get('total_time', 0)
        throughput_kbps = result.get('throughput_kbps', 0)
        throughput_mbps = result.get('throughput_mbps', 0)
        messages_sent = result.get('messages_sent', 0)
        messages_successful = result.get('messages_successful', 0)
        messages_failed = result.get('messages_failed', 0)
        snr = result.get('snr', None)
        success_rate = (messages_successful / messages_sent * 100) if messages_sent > 0 else 0
        
        # Determine status color
        if success_rate >= 95:
            status_color = "bg-green-100 text-green-800"
            status_text = "Excellent"
        elif success_rate >= 80:
            status_color = "bg-yellow-100 text-yellow-800"
            status_text = "Good"
        else:
            status_color = "bg-red-100 text-red-800"
            status_text = "Poor"
        
        # SNR color
        snr_color = "text-gray-600"
        snr_badge = ""
        if snr is not None:
            if snr > 10:
                snr_color = "text-green-600"
                snr_badge = "bg-green-100 text-green-800"
            elif snr > 5:
                snr_color = "text-yellow-600"
                snr_badge = "bg-yellow-100 text-yellow-800"
            else:
                snr_color = "text-red-600"
                snr_badge = "bg-red-100 text-red-800"
        
        html += f"""
                        <tr class="table-row bg-white hover:bg-gray-50" style="animation-delay: {0.6 + i*0.1}s">
                            <td class="px-6 py-4 whitespace-nowrap">
                                <div class="flex items-center">
                                    <div class="text-sm font-medium text-gray-900">{from_node}</div>
                                    <div class="mx-2 text-gray-400">→</div>
                                    <div class="text-sm font-medium text-gray-900">{to_node}</div>
                                </div>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap">
                                <div class="text-sm text-gray-900">{file_size:.2f} MB</div>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap">
                                <div class="text-sm text-gray-900">{total_time:.2f}s</div>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap">
                                <div class="text-sm font-semibold text-blue-600">{throughput_kbps:.2f} kbps</div>
                                <div class="text-xs text-gray-500">{throughput_mbps:.4f} Mbps</div>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap">
                                <div class="text-sm text-gray-900">{messages_successful}/{messages_sent}</div>
                                <div class="text-xs text-gray-500">{success_rate:.1f}%</div>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap">
"""
        if snr is not None:
            html += f"""
                                <span class="px-2 py-1 text-xs font-semibold rounded-full {snr_badge}">
                                    {snr:.2f} dB
                                </span>
"""
        else:
            html += """
                                <span class="text-xs text-gray-400">N/A</span>
"""
        html += f"""
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap">
                                <span class="px-2 py-1 text-xs font-semibold rounded-full {status_color}">
                                    {status_text}
                                </span>
                            </td>
                        </tr>
"""
    
    html += """
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Additional Metrics -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-8">
"""
    
    # Add detailed metrics for each test
    for i, result in enumerate(test_results):
        from_node = result.get('port', 'Unknown').split('/')[-1]
        to_node = result.get('target_node', 'Unknown')
        
        html += f"""
            <div class="bg-white rounded-xl shadow-lg p-6 fade-in" style="animation-delay: {0.8 + i*0.1}s">
                <h3 class="text-lg font-bold text-gray-800 mb-4">{from_node} → {to_node}</h3>
                <div class="space-y-3">
                    <div class="flex justify-between items-center">
                        <span class="text-sm text-gray-600">Bytes/sec:</span>
                        <span class="text-sm font-semibold text-gray-800">{result.get('bytes_per_second', 0):,.0f}</span>
                    </div>
                    <div class="flex justify-between items-center">
                        <span class="text-sm text-gray-600">Messages/sec:</span>
                        <span class="text-sm font-semibold text-gray-800">{result.get('messages_per_second', 0):.2f}</span>
                    </div>
"""
        if result.get('channel_utilization') is not None:
            html += f"""
                    <div class="flex justify-between items-center">
                        <span class="text-sm text-gray-600">Channel Utilization:</span>
                        <span class="text-sm font-semibold text-gray-800">{result.get('channel_utilization', 0)*100:.1f}%</span>
                    </div>
"""
        if result.get('air_util_tx') is not None:
            html += f"""
                    <div class="flex justify-between items-center">
                        <span class="text-sm text-gray-600">Air Util TX:</span>
                        <span class="text-sm font-semibold text-gray-800">{result.get('air_util_tx', 0)*100:.2f}%</span>
                    </div>
"""
        html += """
                </div>
            </div>
"""
    
    html += """
        </div>

        <!-- Footer -->
        <div class="mt-8 text-center text-gray-500 text-sm fade-in">
            <p>Meshtastic Mesh Network Performance Test</p>
            <p class="mt-2">Configuration: UA_433, SHORT_FAST preset</p>
        </div>
    </div>
</body>
</html>
"""
    
    return html


if __name__ == "__main__":
    # Load test results
    test_results = []
    
    # Try to load JSON files
    import glob
    json_files = glob.glob("test_*.json")
    
    for json_file in json_files:
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    test_results.append(data)
        except:
            pass
    
    # If no JSON files, check command line args
    if not test_results and len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            try:
                with open(arg, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        test_results.append(data)
            except:
                pass
    
    if not test_results:
        print("No test results found. Please run tests first.")
        sys.exit(1)
    
    # Generate HTML
    html = generate_html_report(test_results)
    
    # Write to file
    output_file = "mesh_speed_test_report.html"
    with open(output_file, 'w') as f:
        f.write(html)
    
    print(f"HTML report generated: {output_file}")
    print(f"Tests included: {len(test_results)}")

