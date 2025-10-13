#!/bin/bash
# SAGE AI Deployment Script
echo "Starting SAGE AI on port 8540..."
cd sage_ai
nohup python3 sage4_interface_fixed.py > sage.log 2>&1 &
echo "✅ SAGE AI started. Check logs at sage.log"
