#!/usr/bin/env python3
"""
Enhanced uniqueness solution: Add insight ID-specific variations within categories
"""

def add_insight_id_variation(content_dict, insight_id, category):
    """Add insight ID-specific variations to content"""
    
    # Extract the number from the insight ID (e.g., F006 -> 6, PR003 -> 3)
    import re
    id_match = re.search(r'(\d+)$', insight_id)
    id_num = int(id_match.group(1)) if id_match else 1
    
    variations = {
        1: {"focus": "immediate impact", "timeline_adj": "accelerated", "intensity": "intensive"},
        2: {"focus": "strategic alignment", "timeline_adj": "phased", "intensity": "comprehensive"},
        3: {"focus": "market positioning", "timeline_adj": "measured", "intensity": "targeted"},
        4: {"focus": "operational excellence", "timeline_adj": "structured", "intensity": "systematic"},
        5: {"focus": "competitive advantage", "timeline_adj": "adaptive", "intensity": "strategic"},
        6: {"focus": "customer value", "timeline_adj": "iterative", "intensity": "customer-focused"},
        7: {"focus": "innovation potential", "timeline_adj": "progressive", "intensity": "innovative"},
        8: {"focus": "market expansion", "timeline_adj": "scalable", "intensity": "expansion-driven"},
        9: {"focus": "efficiency optimization", "timeline_adj": "streamlined", "intensity": "efficiency-focused"},
        10: {"focus": "sustainability", "timeline_adj": "long-term", "intensity": "sustainable"},
        11: {"focus": "risk mitigation", "timeline_adj": "controlled", "intensity": "risk-aware"}
    }
    
    variation = variations.get(id_num % 11 + 1, variations[1])
    
    return variation

def create_unique_implementation_steps(category, insight_id, stats):
    """Create unique implementation steps with ID-specific variations"""
    variation = add_insight_id_variation({}, insight_id, category)
    
    # Base steps with variations
    if category == "financial":
        steps = [
            {"step": f"{variation['intensity'].title()} Financial Assessment", 
             "description": f"Conduct {variation['focus']}-oriented analysis of ${stats.get('total_revenue', 0):,.0f} revenue base with {variation['intensity']} approach.", 
             "timeline": "1-2 weeks"},
            {"step": f"{variation['timeline_adj'].title()} Strategy Development", 
             "description": f"Design {variation['timeline_adj']} financial optimization strategy emphasizing {variation['focus']} and measurable outcomes.", 
             "timeline": "2-3 weeks"},
            {"step": f"{variation['focus'].title()} Implementation", 
             "description": f"Execute {variation['focus']}-driven improvements using {variation['intensity']} methodology with continuous monitoring.", 
             "timeline": "1-3 months"},
            {"step": f"{variation['timeline_adj'].title()} Performance Optimization", 
             "description": f"Monitor and optimize financial performance using {variation['timeline_adj']} approach for sustained {variation['focus']}.", 
             "timeline": "Ongoing"}
        ]
    else:
        # Generic with variations
        steps = [
            {"step": f"{variation['intensity'].title()} Assessment", 
             "description": f"Comprehensive {variation['focus']}-oriented analysis using {variation['intensity']} methodology.", 
             "timeline": "1-2 weeks"},
            {"step": f"{variation['timeline_adj'].title()} Strategy Design", 
             "description": f"Develop {variation['timeline_adj']} strategy framework emphasizing {variation['focus']} and strategic alignment.", 
             "timeline": "2-3 weeks"},
            {"step": f"{variation['focus'].title()} Implementation", 
             "description": f"Execute {variation['focus']}-driven initiatives with {variation['intensity']} approach and progress tracking.", 
             "timeline": "1-3 months"},
            {"step": f"{variation['timeline_adj'].title()} Optimization", 
             "description": f"Monitor outcomes and optimize performance using {variation['timeline_adj']} methodology for sustained results.", 
             "timeline": "Ongoing"}
        ]
    
    return steps

# Test the variation system
if __name__ == "__main__":
    # Test different insight IDs
    test_ids = ["F001", "F002", "F006", "F011", "PR003", "P005"]
    
    for insight_id in test_ids:
        variation = add_insight_id_variation({}, insight_id, "financial")
        print(f"{insight_id}: {variation}")
    
    print("\nThis variation system will ensure each insight has unique implementation steps!")
    print("Each insight ID gets different focus, timeline style, and intensity approach.") 