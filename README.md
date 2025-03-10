# WorldQuant BRAIN Development Toolkit

This toolkit provides a comprehensive workflow for developing, simulating, and submitting alpha expressions to the WorldQuant BRAIN platform.

## Overview

The toolkit consists of four main components:

1. **Creator** - Generates alpha expressions based on fundamental data
2. **Simulator** - Performs backtesting for the generated alpha expressions
3. **Checker** - Validates and submits successful alpha expressions
4. **Monitor** - Ensures continuous operation of the simulation process

## Prerequisites

1. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create a `credentials.json` file in the project directory:
   ```json
   {
     "username": "your_username",
     "password": "your_password"
   }
   ```

## Components

### 1. Alpha Creator

This component generates alpha expressions based on fundamental data.

**Key Features:**
- Authentication with WorldQuant BRAIN API
- Extraction of supported fields from specified datasets
- Generation of alpha expressions
- Output to CSV for simulation

**Usage:**
```bash
python alpha_creator.py
```

**Output:** `alphas_pending_simulated.csv`

### 2. Alpha Simulator

This component handles the backtesting of the generated alpha expressions.

**Key Features:**
- Concurrent simulation of multiple alpha expressions
- Dynamic task queue management
- Logging of simulation status and progress
- Error handling with automatic retries

**Usage:**
```bash
python alpha_simulator.py
```

**Input:** `pending_simulated_list.csv`  
**Output:** `simulated_list.csv`

### 3. Alpha Checker

This component validates successful alpha expressions and manages their submission.

**Key Features:**
- Filtering of alphas based on performance metrics (Fitness, Sharpe, Turnover)
- Submission status checking
- Identification of successful submissions

**Usage:**
```bash
python checker.py
```

### 4. Monitoring System

A bash script that ensures the continuous operation of the simulator.

**Key Features:**
- Monitors the `simulation.log` file
- Restarts the simulator if no updates are detected for 10 minutes
- Logs monitoring activities

**Usage:**
```bash
# Make the script executable
chmod +x monitor.sh

# Run as a background process
nohup ./monitor.sh >> monitor.log 2>&1 &

# View logs in real-time
tail -f monitor.log

# Stop the monitoring process
pkill -f monitor.sh
```

## Complete Workflow

1. Generate alpha expressions:
   ```bash
   python alpha_creator.py
   ```

2. Start the simulation process with monitoring:
   ```bash
   chmod +x monitor.sh
   nohup ./monitor.sh >> monitor.log 2>&1 &
   ```

3. Check submission status:
   ```bash
   python checker.py
   ```