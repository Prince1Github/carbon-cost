#!/usr/bin/env python3
"""
Carbon-Cost Simulation Script

This script simulates multiple GitHub Action runs to generate sample data
for testing the dashboard and demonstrating CO2 emission trends.
"""

import requests
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Configuration
BACKEND_URL = "http://localhost:5000/record"
REPOS = ["frontend-app", "backend-api", "mobile-app", "data-pipeline", "ml-service"]
MACHINE_TYPES = ["ubuntu-latest", "windows-latest", "macos-latest"]
BADGE_COLORS = ["Green", "Yellow", "Red"]

def generate_emission_data(repo: str, run_id: int) -> Dict[str, Any]:
    """
    Generate realistic emission data for a simulated CI/CD run
    
    Args:
        repo: Repository name
        run_id: Unique run identifier
        
    Returns:
        Dictionary containing emission data
    """
    # Simulate different job durations (30 seconds to 15 minutes)
    duration = random.randint(30, 900)
    
    # Randomly select machine type
    machine_type = random.choice(MACHINE_TYPES)
    
    # Calculate CO2 based on duration and machine type
    co2_factors = {
        "ubuntu-latest": 0.0002,
        "windows-latest": 0.0003,
        "macos-latest": 0.00025,
    }
    co2 = duration * co2_factors[machine_type]
    
    # Determine badge based on CO2
    if co2 < 0.5:
        badge = "Green"
    elif co2 < 1.5:
        badge = "Yellow"
    else:
        badge = "Red"
    
    # Generate timestamp (spread over the last 7 days)
    days_ago = random.randint(0, 7)
    hours_ago = random.randint(0, 24)
    minutes_ago = random.randint(0, 60)
    
    timestamp = datetime.now() - timedelta(
        days=days_ago, 
        hours=hours_ago, 
        minutes=minutes_ago
    )
    
    return {
        "repo": repo,
        "owner": "carbon-cost-team",
        "run_id": str(run_id),
        "co2": round(co2, 3),
        "duration": duration,
        "machine_type": machine_type,
        "badge": badge,
        "timestamp": timestamp.isoformat()
    }

def send_emission_data(data: Dict[str, Any]) -> bool:
    """
    Send emission data to the backend API
    
    Args:
        data: Emission data dictionary
        
    Returns:
        True if successful, False otherwise
    """
    try:
        response = requests.post(BACKEND_URL, json=data)
        if response.status_code == 201:
            print(f"✅ Recorded: {data['repo']} - {data['co2']}kg CO2 ({data['badge']})")
            return True
        else:
            print(f"❌ Failed: {data['repo']} - Status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {data['repo']} - {e}")
        return False

def simulate_runs(num_runs: int = 20, delay: float = 0.5) -> None:
    """
    Simulate multiple CI/CD runs
    
    Args:
        num_runs: Number of runs to simulate
        delay: Delay between runs in seconds
    """
    print(f"🚀 Starting simulation of {num_runs} CI/CD runs...")
    print(f"📊 Backend URL: {BACKEND_URL}")
    print("-" * 50)
    
    successful_runs = 0
    
    for i in range(1, num_runs + 1):
        repo = random.choice(REPOS)
        data = generate_emission_data(repo, i)
        
        if send_emission_data(data):
            successful_runs += 1
        
        # Add delay between requests
        if i < num_runs:
            time.sleep(delay)
    
    print("-" * 50)
    print(f"✅ Simulation complete!")
    print(f"📈 Successfully recorded {successful_runs}/{num_runs} runs")
    print(f"🌐 Check your dashboard at: http://localhost:8501")

def main():
    """Main function to run the simulation"""
    print("🌱 Carbon-Cost Data Simulation")
    print("=" * 40)
    
    # Check if backend is running
    try:
        response = requests.get("http://localhost:5000/stats")
        if response.status_code == 200:
            print("✅ Backend is running")
        else:
            print("❌ Backend is not responding properly")
            return
    except requests.exceptions.RequestException:
        print("❌ Backend is not running. Please start the Flask server first.")
        print("   Run: cd backend && python app.py")
        return
    
    # Get user input
    try:
        num_runs = int(input("Enter number of runs to simulate (default: 20): ") or "20")
        delay = float(input("Enter delay between runs in seconds (default: 0.5): ") or "0.5")
    except ValueError:
        print("Invalid input, using defaults")
        num_runs = 20
        delay = 0.5
    
    # Run simulation
    simulate_runs(num_runs, delay)

if __name__ == "__main__":
    main() 