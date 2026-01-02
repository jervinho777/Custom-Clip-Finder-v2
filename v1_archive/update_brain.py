#!/usr/bin/env python3
"""
Auto-update brain with new performance data

Run this:
- After exporting new clips
- When new viral clips added to training data
- Periodically (weekly) to incorporate latest learnings
"""

import asyncio
from viral_pattern_analyzer import ViralPatternAnalyzer

async def update_brain():
    """Update brain with latest data"""
    
    print(f"\n{'='*70}")
    print(f"🔄 AUTO-UPDATE: VIRAL PRINCIPLES BRAIN")
    print(f"{'='*70}")
    
    analyzer = ViralPatternAnalyzer()
    
    # Re-analyze everything with latest data
    principles = await analyzer.analyze_all()
    
    print(f"\n✅ Brain updated!")
    print(f"   Version: {principles.get('version', 'unknown')}")
    print(f"   Updated: {principles.get('updated_at', 'unknown')}")
    print(f"   Next composition will use latest learnings!")
    
    return principles

if __name__ == '__main__':
    asyncio.run(update_brain())

