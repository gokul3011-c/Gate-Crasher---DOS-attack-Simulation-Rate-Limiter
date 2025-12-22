<div align="center">
  <img src="DOSRL%20logo.png" alt="GATE & CRASHER Logo" width="300" height="300" style="border-radius: 50%; object-fit: cover; border: 4px solid #3498db; box-shadow: 0 6px 12px rgba(0,0,0,0.3); background: white; padding: 5px;">
</div>

# GATE & CRASHER - DoS Simulator & Rate Limiter

**Educational Cybersecurity Simulation Platform**

A professional-grade desktop application for simulating Denial-of-Service (DoS) attacks and rate limiting defense mechanisms. Designed for cybersecurity education and research.

## Project Overview

GATE & CRASHER provides a controlled environment to study DoS attack vectors, rate limiting algorithms, auto-blacklisting, and machine learning-based anomaly detection. All operations run locally on localhost with no external network access.

## Key Features

### Security Defenses
- **Sliding Window Rate Limiting**: Configurable limits (default: 5 req/10s)
- **Auto-Blacklisting**: IP blocking after 3 violations (configurable duration)
- **Defense Chain Visualization**: Real-time firewall → limiter → application status
- **ML Anomaly Detection**: Isolation Forest + Logistic Regression models

### Monitoring & Analytics
- **Live Statistics**: Requests sent, 200 OK, 429/403 blocked ratios
- **System Resource Tracking**: CPU/RAM utilization via psutil
- **Blacklist Management**: Active IP table with expiration timers
- **CSV Reporting**: Comprehensive attack simulation logs

### Attack Simulation
- **HTTP Flood** (1-200 RPS configurable)
- **Burst Attacks** (high-intensity spikes)
- **Randomized Attacks** (random timing patterns)
- **Slowloris** (partial header connections)
- **Botnet Simulation** (IP spoofing via headers)
- **UDP Flood** (64-2048B payloads)
- **TCP SYN-like** (connection exhaustion)

## System Requirements

| Component | Requirement |
|-----------|-------------|
| **Python** | 3.8+ |
| **Core Dependencies** | `flask requests psutil` |
| **ML Features** | `numpy scikit-learn` |
| **OS** | Windows/Linux/macOS |
| **Ports** | 5000(HTTP), 5001(UDP), 5002(TCP) |

## Quick Start

Before launching the application, ensure you have Python 3.8+ installed on your system.

### Installation Steps

1. **Install required dependencies**:
   ```bash
   pip install flask requests psutil numpy scikit-learn
   ```

2. **Optional enhancements** (for full functionality):
   - For basic operation: `pip install flask requests psutil`
   - For system monitoring: `pip install psutil`
   - For ML features: `pip install numpy scikit-learn`

3. **Launch the application**:
   ```bash
   python dos_simulator.py
   ```

### Initial Setup

Upon first launch, you'll see the GATE CRASHER landing page with:
- Large circular DOSRL logo
- Project title and description
- Two action buttons: "PROJECT INFO" and "START APPLICATION"

Click "START APPLICATION" to proceed to the main interface.

### Detailed Usage Guide

#### 1. Starting the Application
- Run `python dos_simulator.py` to launch the application
- The application will open with a landing page featuring the GATE CRASHER logo
- Click "START APPLICATION" to proceed to the main interface

#### 2. Main Interface Overview
The main interface consists of several sections:
- **Server Control Panel**: Manage the target server (localhost:5000)
- **Attacker Control Panel**: Configure and launch attack simulations
- **Parameters Section**: Adjust rate limiting thresholds
- **Statistics Dashboard**: View real-time attack and defense metrics
- **Logging Area**: Monitor events and system status

#### 3. Setting Up the Target Server
- Click "Start Server" in the Server Control Panel
- The server will begin listening on localhost:5000
- Status indicators will show "Online" when ready

#### 4. Configuring Attack Parameters
- Select an attack mode from the dropdown (Flood, Burst, Randomized, Slowloris, Botnet, UDP Flood, TCP SYN-like)
- Adjust Requests Per Second (RPS) using the spinbox (1-200 range)
- For UDP/TCP attacks, additional parameters can be configured in the code

#### 5. Executing Attacks
- Click "Start Attack" to begin the simulation
- Monitor real-time statistics in the dashboard
- View blocking actions and system resource usage
- Stop the attack at any time with "Stop Attack"

#### 6. Rate Limiting Configuration
- Adjust "Max Requests" to set threshold (default: 5 requests)
- Modify time window in the application code if needed (default: 10 seconds)
- Violation thresholds for blacklisting can be tuned

#### 7. Monitoring and Analysis
- Real-time counters show requests sent, successful responses, and blocked attempts
- System resource usage (CPU/RAM) displayed when psutil is available
- Active blacklist entries shown with expiration timers
- Machine Learning anomaly detection status (when enabled)

#### 8. Exporting Results
- Click "Generate Report" to create a CSV summary
- View detailed logs with "View Logs" (opens attack_log.csv)
- Reports and logs contain timestamps, event types, and performance metrics

### Usage Workflow
1. Start Server → localhost:5000 (rate limited endpoint)
2. Configure Parameters → Adjust limits/RPS/modes
3. Execute Attack → Monitor defense activation
4. Analyze Results → Generate CSV reports

## Technical Architecture

The GATE CRASHER application follows a modular architecture with three primary components:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Tkinter GUI   │◄──►│   Flask Server   │◄──►│ Attack Simulator│
└─────────┬───────┘    └──────┬──────────┘    └──────┬──────────┘
          │                   │                       │
          └─────────┬─────────┼───────────────┬───────┘
                    │         │               │
              ┌─────▼──┐ ┌────▼────┐ ┌──────▼─────┐
              │CSV Log │ │ML Models│ │System Monitor│
              └────────┘ └──────────┘ └─────────────┘
```

### Component Overview

1. **Tkinter GUI**: 
   - Provides the user interface for controlling attacks and monitoring defenses
   - Built with Python's standard GUI toolkit for cross-platform compatibility
   - Features dark/light theme switching capability

2. **Flask Server**: 
   - Implements the target server running on localhost:5000
   - Integrates rate limiting and blacklisting mechanisms
   - Handles incoming HTTP requests and applies defensive measures

3. **Attack Simulator**: 
   - Generates various types of DoS attacks (HTTP, UDP, TCP)
   - Supports multiple attack vectors and configurable intensity
   - Manages concurrent attack threads for realistic simulation

4. **Supporting Modules**:
   - **CSV Log**: Records all events and metrics for analysis
   - **ML Models**: Provides anomaly detection using Isolation Forest and Logistic Regression
   - **System Monitor**: Tracks CPU and memory usage during simulations

### Rate Limiting Algorithm

Sliding Window Implementation:
├── Request timestamp deque (maxlen=window_duration)
├── Prune expired timestamps (>window_duration)
├── Block if len(deque) >= max_requests
└── Track violations → auto-blacklist after threshold

### Attack Mode Specifications

| Mode      | Protocol | Characteristics  | Parameters             |
| --------- | -------- | ---------------- | ---------------------- |
| Flood     | HTTP     | Constant RPS     | 1-200 req/s            |
| Burst     | HTTP     | Spike patterns   | RPS multiplier         |
| Randomized| HTTP     | Random timing    | Variable intervals     |
| Slowloris | HTTP     | Slow headers     | Connection timeout     |
| Botnet    | HTTP     | IP rotation      | X-Forwarded-For spoof  |
| UDP Flood | UDP:5001 | Packet bursts    | 64-2048B, 10-1000 pkts |
| TCP SYN   | TCP:5002 | Conn. exhaustion | Port-specific          |

## Educational Applications

- **Cybersecurity Training**: DoS defense implementation
- **Penetration Testing**: Attack vector familiarization
- **Research**: ML-based intrusion detection
- **Academic**: Network security coursework

## File Structure

```
├── dos_simulator.py       # Core application (1100+ lines)
├── attack_log.csv         # Runtime logs
├── simulation_report.csv   # Summary reports
├── DOSRL logo.png         # Branding
├── Project_info.html      # Documentation
└── README.md              # This file
```

### File Descriptions

- **dos_simulator.py**: The main application containing all logic for the GUI, server, attack simulation, and ML components
- **attack_log.csv**: Detailed chronological log of all events during simulations (automatically created on first run)
- **simulation_report.csv**: Summary statistics and metrics exported from the application
- **DOSRL logo.png**: Official project logo used in the application interface and documentation
- **Project_info.html**: Comprehensive project documentation with team information and technical details
- **README.md**: This file containing setup instructions, usage guides, and technical information

## Performance Metrics

- Max Concurrent Attacks: 200+ RPS (system dependent)
- ML Prediction Latency: <1s real-time scoring
- Blacklist Capacity: 1000+ active entries
- Log Throughput: 10K+ events/hour

## Troubleshooting

| Issue                | Solution                               |
| -------------------- | -------------------------------------- |
| Port 5000 busy       | netstat -ano \| findstr :5000 (Windows) |
| ML disabled          | pip install scikit-learn numpy         |
| No system stats      | pip install psutil                     |
| CSV permission error | Run as administrator                   |

## Contribution Guidelines

1. Fork repository
2. Create feature branch (git checkout -b feature/DoS-visualization)
3. Commit changes (git commit -m 'Add visualization enhancements')
4. Push to branch (git push origin feature/DoS-visualization)
5. Open Pull Request

Focus Areas: ML improvements, new attack vectors, UI enhancements