#!/usr/bin/env python3
"""Trace execution to find where it hangs"""

import sys
import trace

# Create a Trace object
tracer = trace.Trace(trace=1, count=0)

# Run the multiphase processor with tracing
sys.argv = [
    'multiphase_processor_improved.py',
    'data/papers/computational_linguistics/sh_truncated.txt',
    'schemas/semantic_hypergraph/traced_output.yml'
]

# Change to the correct directory
import os
os.chdir('/home/brian/lit_review')

# Run with timeout
import signal

def timeout_handler(signum, frame):
    print("\n\nTIMEOUT - Last executed lines above show where it hung")
    sys.exit(1)

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(30)  # 30 second timeout

try:
    tracer.run('exec(open("src/schema_creation/multiphase_processor_improved.py").read())')
except SystemExit:
    pass