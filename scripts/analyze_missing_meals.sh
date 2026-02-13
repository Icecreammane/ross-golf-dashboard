#!/bin/bash

# Feb 8 Super Bowl - found subs at 2:17pm and party snacks at 8:14pm
echo "=== FEB 8 (SUPER BOWL) MEALS ==="
echo "2:17 PM - 2 Italian subs from deli (1,400 cal, 65g P)"
echo "8:14 PM - Party snacks: cookie, jalapeño poppers, chips+dip, pretzels (940 cal, 22g P)"
echo ""

# Let me check Feb 1, 5, and 7 food photos
echo "=== Checking Feb 1 photos ==="
ls -lah ~/.clawdbot/media/inbound/*.jpg | grep "Feb  1"

echo""
echo "=== Checking Feb 5 photos ==="
ls -lah ~/.clawdbot/media/inbound/*.jpg | grep "Feb  5"

echo ""
echo "=== Checking Feb 7 photos ==="
ls -lah ~/.clawdbot/media/inbound/*.jpg | grep "Feb  7"
