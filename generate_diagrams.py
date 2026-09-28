import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

def create_system_architecture_diagram(filename='extracted_assets/system_architecture_diagram.png'):
    fig, ax = plt.subplots(figsize=(11, 6.2), dpi=300)
    ax.set_facecolor('#ffffff')
    fig.patch.set_facecolor('#ffffff')
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 6.2)
    ax.axis('off')

    # Title
    ax.text(5.5, 5.85, 'AI-BASED SMART TRANSFORMER HEALTH MONITORING SYSTEM', 
            fontsize=13, fontweight='bold', color='#1A365D', ha='center', va='center', fontfamily='sans-serif')
    ax.text(5.5, 5.55, 'End-to-End AIoT Hardware Pipeline & Telemetry Architecture', 
            fontsize=10, color='#4A5568', ha='center', va='center', fontfamily='sans-serif')

    # Stage boxes definition: (x, y, w, h, header, color, border)
    stages = [
        {
            'x': 0.4, 'y': 1.1, 'w': 1.8, 'h': 4.0,
            'title': 'STAGE 1\nSENSING LAYER',
            'subtitle': 'Mini Transformer\n& Sensors',
            'header_bg': '#2B6CB0',
            'body_bg': '#EBF8FF',
            'border': '#3182CE',
            'items': [
                'Mini Step-Down\nTransformer Testbed',
                'Temp Sensor\n(LM35 / DS18B20)',
                'Current Sensor\n(ACS712 Module)',
                'Voltage Sensor\n(ZMPT101B Module)',
                'Oil Level Sensor\n(Float / Ultrasonic)'
            ]
        },
        {
            'x': 2.55, 'y': 1.1, 'w': 1.7, 'h': 4.0,
            'title': 'STAGE 2\nEDGE PROCESSING',
            'subtitle': 'ESP32 Microcontroller',
            'header_bg': '#2C7A7B',
            'body_bg': '#E6FFFA',
            'border': '#319795',
            'items': [
                'ESP32 Dual-Core\nMCU (32-bit)',
                'Multi-channel\nADC Sampling',
                'Signal Calibration\n& Noise Filter',
                'JSON Telemetry\nPayload Packaging',
                'Wi-Fi 802.11 b/g/n\nTransmitter'
            ]
        },
        {
            'x': 4.6, 'y': 1.1, 'w': 1.7, 'h': 4.0,
            'title': 'STAGE 3\nCLOUD STORAGE',
            'subtitle': 'Cloud DB & Ingestion',
            'header_bg': '#4A5568',
            'body_bg': '#EDF2F7',
            'border': '#718096',
            'items': [
                'FastAPI Backend\nREST & WebSockets',
                'Secure Wireless\nData Reception',
                'Time-Series DB\n(SQLite / Cloud DB)',
                'Historical Reading\nLogging Engine',
                'Sub-second Data\nPipeline (<1s)'
            ]
        },
        {
            'x': 6.65, 'y': 1.1, 'w': 1.8, 'h': 4.0,
            'title': 'STAGE 4\nAI HEALTH ENGINE',
            'subtitle': 'Intelligent Diagnostics',
            'header_bg': '#6B46C1',
            'body_bg': '#FAF5FF',
            'border': '#805AD5',
            'items': [
                'AI Rule-Based &\nML Analytics',
                'Multi-parameter\nCorrelation Matrix',
                'Health Decision:\n- NORMAL (Safe)\n- WARNING (Alert)\n- CRITICAL (Danger)',
                'Predictive Trend\nAnomaly Detection'
            ]
        },
        {
            'x': 8.8, 'y': 1.1, 'w': 1.8, 'h': 4.0,
            'title': 'STAGE 5\nOFFICIAL PORTAL',
            'subtitle': 'Web SCADA Dashboard',
            'header_bg': '#C53030',
            'body_bg': '#FFF5F5',
            'border': '#E53E3E',
            'items': [
                'Live Sensor Readout\n(Temp, V, I, Oil %)',
                'AI Condition Badge\n& Health Score %',
                'Interactive Chart.js\nTrend Visualizer',
                'Automated Alerts\n& Incident Center',
                'Remote Monitoring\nfor Grid Officials'
            ]
        }
    ]

    for s in stages:
        # Outer Card Box
        rect = patches.FancyBboxPatch((s['x'], s['y']), s['w'], s['h'],
                                      boxstyle="round,pad=0.08,rounding_size=0.15",
                                      facecolor=s['body_bg'], edgecolor=s['border'],
                                      linewidth=1.8, zorder=2)
        ax.add_patch(rect)

        # Header Box
        header_h = 0.95
        head_rect = patches.FancyBboxPatch((s['x'], s['y'] + s['h'] - header_h), s['w'], header_h,
                                           boxstyle="round,pad=0.06,rounding_size=0.15",
                                           facecolor=s['header_bg'], edgecolor=s['border'],
                                           linewidth=1.2, zorder=3)
        ax.add_patch(head_rect)

        # Header Text
        ax.text(s['x'] + s['w']/2, s['y'] + s['h'] - 0.35, s['title'],
                fontsize=8.5, fontweight='bold', color='#ffffff', ha='center', va='center', zorder=4)
        ax.text(s['x'] + s['w']/2, s['y'] + s['h'] - 0.72, s['subtitle'],
                fontsize=7.5, color='#E2E8F0', ha='center', va='center', zorder=4)

        # Body items
        item_y = s['y'] + s['h'] - 1.25
        for item in s['items']:
            # Small pill/box for each item
            num_lines = item.count('\n') + 1
            box_h = 0.38 + (num_lines - 1) * 0.16
            
            sub_rect = patches.FancyBboxPatch((s['x'] + 0.1, item_y - box_h), s['w'] - 0.2, box_h,
                                              boxstyle="round,pad=0.03,rounding_size=0.08",
                                              facecolor='#ffffff', edgecolor='#CBD5E0',
                                              linewidth=0.9, zorder=3)
            ax.add_patch(sub_rect)
            
            ax.text(s['x'] + s['w']/2, item_y - box_h/2, item,
                    fontsize=7.2, color='#2D3748', ha='center', va='center', zorder=4, fontweight='medium')
            item_y -= (box_h + 0.12)

    # Connecting Arrows between stages
    arrow_links = [
        (2.2, 3.2, 2.55, 3.2, 'Analog/Digital\nSignals'),
        (4.25, 3.2, 4.6, 3.2, 'Wi-Fi\nJSON Push'),
        (6.3, 3.2, 6.65, 3.2, 'Telemetry\nStream'),
        (8.45, 3.2, 8.8, 3.2, 'WebSockets\n& REST API')
    ]

    for (x1, y1, x2, y2, label) in arrow_links:
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(facecolor='#2B6CB0', edgecolor='#2B6CB0',
                                    arrowstyle="-|>", lw=2.2, mutation_scale=14),
                    zorder=5)
        ax.text((x1 + x2)/2, y1 + 0.36, label, fontsize=6.5, color='#1A365D',
                ha='center', va='center', fontweight='bold', zorder=5)

    # Footer note on diagram
    ax.text(5.5, 0.45, 'Hardware Prototype Testbed: Mini Step-Down Transformer with Safe Low-Voltage Physical Sensor Interfacing',
            fontsize=8.5, fontstyle='italic', color='#4A5568', ha='center', va='center')

    plt.tight_layout()
    plt.savefig(filename, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"Created {filename}")

def create_dashboard_mockup(filename='extracted_assets/dashboard_mockup.png'):
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    fig.patch.set_facecolor('#0B0F19')
    ax.set_facecolor('#0B0F19')
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')

    # Top Navbar Card
    nav_rect = patches.FancyBboxPatch((0.4, 5.2), 9.2, 0.65, boxstyle="round,pad=0.03,rounding_size=0.08",
                                     facecolor='#161F30', edgecolor='#23334E', linewidth=1.2)
    ax.add_patch(nav_rect)
    ax.text(0.6, 5.52, 'TRANSFORMER HEALTH SCADA PORTAL', fontsize=9.5, fontweight='bold', color='#63B3ED')
    ax.text(4.4, 5.52, 'Unit: Mini-Transformer T001  |  Substation Lab Bay 3', fontsize=8.5, color='#CBD5E0')
    
    # Pulse indicator
    circle = plt.Circle((8.3, 5.52), 0.08, color='#48BB78', zorder=5)
    ax.add_patch(circle)
    ax.text(8.5, 5.52, 'ESP32 ONLINE', fontsize=7.5, fontweight='bold', color='#48BB78')

    # Overall AI Health Card
    health_rect = patches.FancyBboxPatch((0.4, 3.8), 9.2, 1.25, boxstyle="round,pad=0.04,rounding_size=0.1",
                                         facecolor='#132338', edgecolor='#2B6CB0', linewidth=1.5)
    ax.add_patch(health_rect)
    ax.text(0.7, 4.75, 'AI HEALTH ASSESSMENT ENGINE', fontsize=8.5, fontweight='bold', color='#A0AEC0')
    
    # Big Status Pill: NORMAL
    status_rect = patches.FancyBboxPatch((0.7, 4.0), 2.2, 0.6, boxstyle="round,pad=0.03,rounding_size=0.1",
                                         facecolor='#065F46', edgecolor='#10B981', linewidth=1.5)
    ax.add_patch(status_rect)
    ax.text(1.8, 4.3, 'STATUS: NORMAL', fontsize=9.5, fontweight='bold', color='#A7F3D0', ha='center', va='center')

    # Score Gauge representation
    ax.text(3.3, 4.35, '94%', fontsize=22, fontweight='bold', color='#10B981', va='center')
    ax.text(4.05, 4.35, 'Overall Health\nIndex Score', fontsize=8.5, color='#E2E8F0', va='center')

    # Diagnostics Text
    diag_text = 'Diagnosis: All operational telemetry values are strictly within permissible limits.\nCooling performance optimal; core temperature stable; no insulation stress detected.'
    ax.text(5.5, 4.35, diag_text, fontsize=8, color='#CBD5E0', va='center', linespacing=1.4)

    # 4 Metric Cards
    metrics = [
        {'x': 0.4, 'title': 'TEMPERATURE', 'val': '52.4 °C', 'status': 'NORMAL', 'color': '#10B981', 'range': 'Safe: <65°C | Warning: 65-80°C | Crit: >80°C'},
        {'x': 2.75, 'title': 'LOAD CURRENT', 'val': '1.85 A', 'status': 'NORMAL', 'color': '#10B981', 'range': 'Nominal: 0-2.5A | Warning: 2.5-3.0A'},
        {'x': 5.1, 'title': 'AC VOLTAGE', 'val': '228.6 V', 'status': 'NORMAL', 'color': '#10B981', 'range': 'Nominal: 215V - 240V AC'},
        {'x': 7.45, 'title': 'OIL LEVEL', 'val': '84.5 %', 'status': 'NORMAL', 'color': '#10B981', 'range': 'Normal: >60% | Crit: <40%'}
    ]

    for m in metrics:
        card = patches.FancyBboxPatch((m['x'], 2.05), 2.15, 1.55, boxstyle="round,pad=0.03,rounding_size=0.08",
                                     facecolor='#161F30', edgecolor='#2D3748', linewidth=1.2)
        ax.add_patch(card)
        ax.text(m['x'] + 0.15, 3.35, m['title'], fontsize=8, fontweight='bold', color='#A0AEC0')
        ax.text(m['x'] + 0.15, 2.9, m['val'], fontsize=16, fontweight='bold', color='#FFFFFF')
        
        # Pill
        pill = patches.FancyBboxPatch((m['x'] + 1.15, 3.2), 0.85, 0.28, boxstyle="round,pad=0.02,rounding_size=0.06",
                                      facecolor='#065F46', edgecolor=m['color'], linewidth=0.8)
        ax.add_patch(pill)
        ax.text(m['x'] + 1.57, 3.34, m['status'], fontsize=7, fontweight='bold', color='#A7F3D0', ha='center', va='center')
        
        # Range bar
        bar_bg = patches.Rectangle((m['x'] + 0.15, 2.45), 1.85, 0.08, facecolor='#2D3748')
        ax.add_patch(bar_bg)
        bar_fg = patches.Rectangle((m['x'] + 0.15, 2.45), 1.85 * 0.65, 0.08, facecolor=m['color'])
        ax.add_patch(bar_fg)
        
        ax.text(m['x'] + 0.15, 2.22, m['range'], fontsize=5.8, color='#718096')

    # Footer banner
    foot_rect = patches.FancyBboxPatch((0.4, 1.1), 9.2, 0.75, boxstyle="round,pad=0.03,rounding_size=0.08",
                                      facecolor='#161F30', edgecolor='#23334E', linewidth=1.2)
    ax.add_patch(foot_rect)
    ax.text(0.6, 1.48, 'TELEMETRY STATUS:', fontsize=8, fontweight='bold', color='#A0AEC0')
    ax.text(2.1, 1.48, 'Continuous 2s Stream  |  Packets Ingested: 1,842  |  No Packet Loss', fontsize=8, color='#CBD5E0')
    ax.text(6.8, 1.48, 'Last Sync: 22 Sep 2026, 19:08:42 IST', fontsize=8, color='#63B3ED', fontweight='bold')

    plt.tight_layout()
    plt.savefig(filename, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"Created {filename}")

def create_dashboard_charts(filename='extracted_assets/dashboard_charts.png'):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5.5), dpi=300, gridspec_kw={'width_ratios': [1.3, 1.0]})
    fig.patch.set_facecolor('#0B0F19')

    # Chart 1: Real-time Multi-Parameter Trends
    ax1.set_facecolor('#161F30')
    t = np.linspace(0, 30, 60)
    # Simulated smooth trending telemetry
    temp = 48 + 4 * np.sin(t/5) + 0.6 * np.random.randn(len(t))
    current = 1.2 + 0.5 * np.sin(t/4) + 0.1 * np.random.randn(len(t))
    voltage = 227 + 2 * np.cos(t/6) + 0.3 * np.random.randn(len(t))
    oil = 86 - 0.08 * t + 0.1 * np.random.randn(len(t))

    l1 = ax1.plot(t, temp, color='#F6AD55', label='Temperature (°C)', lw=2.2)
    l4 = ax1.plot(t, oil, color='#4FD1C5', label='Oil Level (%)', lw=2.2)

    ax1_sub = ax1.twinx()
    l2 = ax1_sub.plot(t, current, color='#63B3ED', label='Current (A)', lw=2, linestyle='--')
    l3 = ax1_sub.plot(t, voltage/100, color='#B794F4', label='Voltage (V/100)', lw=1.8, linestyle=':')

    ax1.set_title('Real-Time Parameter Trends (Chart.js Visualization)', fontsize=10.5, fontweight='bold', color='#E2E8F0', pad=12)
    ax1.set_xlabel('Time Window (Past 30 Minutes)', fontsize=8, color='#A0AEC0')
    ax1.set_ylabel('Temperature (°C) / Oil Level (%)', fontsize=8, color='#A0AEC0')
    ax1_sub.set_ylabel('Current (A) / Voltage (Scale)', fontsize=8, color='#A0AEC0')
    ax1.grid(True, linestyle='--', alpha=0.2, color='#718096')
    ax1.tick_params(colors='#CBD5E0', labelsize=7)
    ax1_sub.tick_params(colors='#CBD5E0', labelsize=7)

    # Combined Legend
    lines = l1 + l4 + l2 + l3
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper left', fontsize=7.2, facecolor='#1A202C', edgecolor='#4A5568', labelcolor='#E2E8F0')

    # Chart 2 / Panel 2: Incident & Alert Log Panel
    ax2.set_facecolor('#161F30')
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.axis('off')

    ax2.text(5, 9.3, 'Active Alerts & Incident Log Center', fontsize=10.5, fontweight='bold', color='#E2E8F0', ha='center')
    ax2.text(5, 8.7, 'Real-time Event Logging & Threshold Monitoring', fontsize=8, color='#A0AEC0', ha='center')

    alerts = [
        {'time': '19:04:12', 'sev': 'CRITICAL', 'msg': 'Temperature spiked to 82.5°C\n(Exceeds 80°C threshold)', 'color': '#E53E3E', 'bg': '#742A2A'},
        {'time': '18:52:30', 'sev': 'WARNING', 'msg': 'Load current surged to 2.85 A\n(Near rated limit 3.0A)', 'color': '#ED8936', 'bg': '#7B341E'},
        {'time': '18:30:15', 'sev': 'INFO', 'msg': 'Oil Level calibrated at 84.5%\n(Optimal level detected)', 'color': '#319795', 'bg': '#234E52'},
        {'time': '18:00:00', 'sev': 'SYSTEM', 'msg': 'ESP32 Node Connected & Synced\nCloud Database Initialized', 'color': '#4299E1', 'bg': '#2A4365'}
    ]

    y_pos = 7.4
    for al in alerts:
        box = patches.FancyBboxPatch((0.5, y_pos - 1.2), 9.0, 1.15, boxstyle="round,pad=0.03,rounding_size=0.06",
                                    facecolor='#1A2436', edgecolor=al['color'], linewidth=1.2)
        ax2.add_patch(box)
        
        # Severity Tag
        tag = patches.FancyBboxPatch((0.8, y_pos - 0.5), 2.2, 0.38, boxstyle="round,pad=0.02,rounding_size=0.04",
                                     facecolor=al['bg'], edgecolor=al['color'], linewidth=0.8)
        ax2.add_patch(tag)
        ax2.text(1.9, y_pos - 0.31, al['sev'], fontsize=7.2, fontweight='bold', color='#FFFFFF', ha='center', va='center')
        
        # Timestamp
        ax2.text(3.3, y_pos - 0.31, al['time'], fontsize=7.5, color='#A0AEC0', va='center')
        
        # Message
        ax2.text(0.8, y_pos - 0.85, al['msg'], fontsize=7.5, color='#E2E8F0', linespacing=1.2, va='center')
        
        y_pos -= 1.45

    # Bottom status on panel 2
    bot = patches.FancyBboxPatch((0.5, 0.5), 9.0, 0.65, boxstyle="round,pad=0.02,rounding_size=0.05",
                                facecolor='#1A202C', edgecolor='#4A5568', linewidth=0.8)
    ax2.add_patch(bot)
    ax2.text(5, 0.82, 'Audited Log: Auto-synced to Cloud Database | Zero Missed Events', fontsize=7.5, color='#CBD5E0', ha='center', va='center')

    plt.tight_layout()
    plt.savefig(filename, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"Created {filename}")

if __name__ == '__main__':
    create_system_architecture_diagram()
    create_dashboard_mockup()
    create_dashboard_charts()
