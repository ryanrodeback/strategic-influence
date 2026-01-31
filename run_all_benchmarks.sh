#!/bin/bash
# Run all AI benchmarks and create comprehensive report

echo "Strategic Influence AI Benchmarking Suite"
echo "=========================================="
echo ""

echo "1. Quick Tournament (15 matches)"
echo "   Estimated time: 50 seconds"
echo ""
python run_tournament.py

echo ""
echo ""
echo "2. Extended Tournament (30 matches)"
echo "   Estimated time: 100 seconds"
echo ""
python extended_tournament.py

echo ""
echo ""
echo "=========================================="
echo "Benchmark Complete!"
echo "=========================================="
echo ""
echo "Review results and recommendations in:"
echo "  - AI_IMPROVEMENTS_SUMMARY.md"
echo "  - FINAL_AI_REPORT.md"
echo ""
echo "Recommended configuration:"
echo "  Agent: OptimizedMinimax(d=1)"
echo "  File: src/strategic_influence/agents/optimized_minimax_agent.py"
