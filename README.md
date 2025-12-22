<div align="center">
  <img src="DOSRL%20logo.png" alt="GATE & CRASHER Logo" width="250" height="250" style="border-radius: 50%; object-fit: cover; border: 3px solid #3498db; box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
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

```bash
# 1. Install dependencies
pip install flask requests psutil numpy scikit-learn

# 2. Launch application
python dos_simulator.py
```

### Usage Workflow
1. Start Server → localhost:5000 (rate limited endpoint)
2. Configure Parameters → Adjust limits/RPS/modes
3. Execute Attack → Monitor defense activation
4. Analyze Results → Generate CSV reports

## Technical Architecture

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
├── DOSRL logo.png         # Branding
├── Project_info.html      # Documentation
└── README.md              # This file
```

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