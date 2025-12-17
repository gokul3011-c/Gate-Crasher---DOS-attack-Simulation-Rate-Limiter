<div align="center">
  <img src="GATE%20&%20CRASHER.png" alt="GATE & CRASHER Logo" width="150" height="150" style="border-radius: 50%; object-fit: cover;">
</div>

# GATE & CRASHER - DoS Simulator & Rate Limiter

A comprehensive cybersecurity simulation tool designed for educational purposes to demonstrate Denial-of-Service (DoS) attacks and rate limiting defenses.

## Purpose

This application simulates DoS attacks against a local web server while demonstrating effective rate limiting and auto-blacklisting defense mechanisms. It's designed for cybersecurity education, allowing users to understand:

- How DoS attacks work and their impact on servers
- How rate limiting can protect against abusive traffic
- How auto-blacklisting defends against persistent attackers
- The importance of system resource monitoring during attacks

## Features

- **Security Mechanisms**:
  - **Rate Limiting**: Limits requests to 5 per 10-second window
  - **Auto-Blacklisting**: Blocks IPs after 3 rate limit violations for 60 seconds
  - **Defense Chain Visualization**: Real-time visualization of firewall → rate limiter → application flow

- **Monitoring & Analytics**:
  - **System Resource Monitoring**: Real-time CPU and RAM usage tracking
  - **Live Statistics**: Counts of requests sent, successful responses (200), and blocked requests (429)
  - **Detailed Logging**: Comprehensive Excel logging of all attack events
  - **Request Log**: Real-time display of all HTTP responses

- **Controls**:
  - **Server Control**: Start/Stop the Flask web server
  - **Attack Control**: Start/Stop simulated DoS attacks
  - **Refresh**: Reset statistics while preserving log data
  - **View Logs**: Open detailed Excel logs for analysis

## Getting Started

- **Prerequisites**:

  - **Python 3.6+**
  - **Required Python packages**:
    ```bash
    pip install flask requests psutil pandas openpyxl pillow
    ```

- **Installation**:

  1. **Clone or download this repository**
  2. **Install required packages**: `pip install flask requests psutil pandas openpyxl pillow`
  3. **Run the application**: `python dos_simulator.py`

- **Usage**:

  1. **Start the Application** - Launch `dos_simulator.py`
  2. **Start the Server** - Click "Start Server" in the Server Control panel
  3. **Initiate Attack** - Click "Start Attack" in the Attacker Control panel
  4. **Monitor Effects** - Observe system resources, live statistics, and request logs
  5. **Analyze Results** - Click "View Log Details" to examine Excel logs

## How It Works

- **DoS Attack Simulation**:

  - **Sends continuous HTTP GET requests** - Targets the local server
  - **Exceeds rate limits** - Goes beyond 5 requests per 10 seconds
  - **Triggers defenses** - Activates rate limiting (429 responses) and auto-blacklisting (403 responses)

- **Defense Mechanisms**:
  1. **Rate Limiter**: Implements sliding window algorithm to limit requests
  2. **Auto-Blacklist**: Blocks IPs after 3 rate limit violations for 60 seconds
  3. **System Monitoring**: Tracks CPU/RAM usage to show attack impact

- **Data Logging**:

  - **All events logged** - Saved to `attack_log.xlsx`
  - **Comprehensive details** - Includes timestamps, event types, details, and durations
  - **Persistent storage** - Data remains across application sessions

## File Structure

- **dos_simulator.py** - Main application
- **attack_log.xlsx** - Attack data logs
- **GATE & CRASHER.png** - Header image
- **DOSRL logo.png** - Logo image
- **Project_info.html** - Project documentation
- **README.md** - This file

## Technical Architecture

- **Components**:

  - **Flask Server** - Handles incoming requests with rate limiting
  - **Tkinter GUI** - Provides user interface for controls and monitoring
  - **Attack Simulator** - Generates HTTP requests to simulate DoS
  - **System Monitor** - Tracks CPU and RAM usage via psutil
  - **Data Logger** - Records events to Excel via pandas

- **Rate Limiting Algorithm**:

  Implements a sliding window approach:

  1. **Maintains request queue** - Keeps track of request timestamps
  2. **Removes expired requests** - Clears requests outside the 10-second window
  3. **Blocks excess requests** - Prevents requests when count reaches 5 within window
  4. **Tracks violations** - Counts violations for blacklisting

- **Auto-Blacklisting**:

  1. **Counts violations** - Tracks rate limit violations per IP
  2. **Applies blacklist** - Blocks IP for 60 seconds after 3 violations
  3. **Manages expiration** - Automatically removes expired blacklist entries

## UI Layout

- **Header**:

  - **Application branding** - Custom header image

- **Control Panels**:

  - **Server Control** - Manage server status and view blacklist status
  - **Attacker Control** - Control attack simulation and view attacker status

- **Monitoring Sections**:

  - **System Resource Monitoring** - CPU and RAM usage indicators
  - **Live Statistics** - Request counts and refresh button
  - **Defense Chain** - Visual representation of security layers

- **Main Content**:

  - **Request Log** - Real-time display of HTTP responses
  - **View Log Details** - Button to open Excel logs

## Educational Value

- **Learning Outcomes**:

  - **Understand DoS mechanics** - Learn how attacks work and impact servers
  - **Learn rate limiting** - Master implementation techniques for traffic control
  - **Explore auto-blacklisting** - Study strategies for blocking persistent attackers
  - **Analyze resource consumption** - Examine system impact during attacks
  - **Study defense-in-depth** - Investigate layered security approaches

- **Safe Usage Guidelines**:

  - **Educational use only** - For learning and research purposes
  - **Controlled environments** - Use only in safe test environments
  - **No production systems** - Never use against live production systems
  - **Respect policies** - Follow all network usage policies

## Contributing

This is an educational tool. Contributions are welcome for:

- **Bug fixes** - Resolve issues and improve stability
- **Feature enhancements** - Add new capabilities and functionality
- **Documentation improvements** - Enhance guides and explanations
- **UI/UX refinements** - Improve user interface and experience

## License

This project is for educational purposes. See individual libraries for their respective licenses.

## Acknowledgments

- Built with Python, Flask, Tkinter, and various open-source libraries
- Designed for cybersecurity education and research
- Thanks to all contributors and the open-source community

## Troubleshooting

- **Common Issues**:
  - **Missing Dependencies**: Install all required packages
  - **Port Conflicts**: Ensure port 5000 is available
  - **Excel File Issues**: Close Excel when viewing logs
  - **GUI Display Problems**: Check Python/Tkinter installation

- **Support**:

  For issues or questions, please check the code comments or create an issue in the repository.