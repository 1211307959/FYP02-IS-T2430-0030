"use client"

import React, { useState, useEffect } from "react"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Button } from "@/components/ui/button"
import { ArrowUpRight, BarChart4, CircleAlert, DollarSign, Package, ShoppingBasket, TrendingDown, TrendingUp, Users } from "lucide-react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { getDashboardData } from "@/lib/api"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { BarChart, LineChart, CartesianGrid, XAxis, YAxis, Legend, Bar, Line, ResponsiveContainer, Tooltip, Cell } from "recharts"

export const dynamic = 'force-dynamic'; // Force dynamic rendering to prevent stale data

// Recommendation database with multiple potential actions for different insight types and severity levels
const recommendationDatabase = {
  revenueTrend: {
    // Revenue decline recommendations by severity
    decline: {
      critical: [
        {
          title: "Emergency Revenue Recovery Plan",
          description: "Implement immediate cost-cutting measures alongside targeted promotions for high-margin products. Convene an emergency team to identify and address revenue leakage.",
          actions: ["Freeze non-essential spending", "Launch high-margin product promotions", "Review pricing strategy"]
        },
        {
          title: "Rapid Market Response",
          description: "Analyze which products and customer segments are driving the decline and launch immediate recovery initiatives. Consider temporary incentives to boost short-term revenue.",
          actions: ["Segment analysis", "Customer outreach", "Flash promotions", "Emergency pricing review"]
        }
      ],
      high: [
        {
          title: "Revenue Stabilization Strategy",
          description: "Focus on retaining existing customers while identifying the root causes of decline. Implement targeted marketing to counteract the downward trend.",
          actions: ["Customer retention program", "Competitor analysis", "Targeted marketing campaign"]
        },
        {
          title: "Sales Process Optimization",
          description: "Review and strengthen your sales process to address conversion inefficiencies. Consider reorganizing sales territories or adjusting commission structures.",
          actions: ["Sales process audit", "Training refresh", "Commission restructure"]
        }
      ],
      medium: [
        {
          title: "Revenue Diversification",
          description: "Explore additional revenue streams to reduce dependency on declining segments. Consider expanding into adjacent markets or product categories.",
          actions: ["Market expansion analysis", "Product line extension", "Cross-selling campaign"]
        },
        {
          title: "Targeted Growth Initiatives",
          description: "Identify pockets of potential growth and allocate additional resources to these areas while monitoring declining segments.",
          actions: ["Growth segment analysis", "Resource reallocation", "Performance monitoring"]
        }
      ],
      low: [
        {
          title: "Preventative Monitoring",
          description: "Implement closer monitoring of sales metrics to catch early warning signs of further decline. Review pricing strategy for potential adjustments.",
          actions: ["Enhanced reporting", "Leading indicator monitoring", "Pricing review"]
        },
        {
          title: "Efficiency Optimization",
          description: "Focus on improving operational efficiency to maintain margins even with slightly reduced revenue. Consider small-scale process improvements.",
          actions: ["Process optimization", "Cost efficiency review", "Small-scale automation"]
        }
      ]
    },
    // Revenue growth recommendations by severity (urgency)
    growth: {
      high: [
        {
          title: "Growth Acceleration Plan",
          description: "Capitalize on strong momentum by scaling successful strategies and investing in growth infrastructure. Consider expanding production capacity.",
          actions: ["Scale successful campaigns", "Capacity planning", "Growth infrastructure investment"]
        },
        {
          title: "Market Share Expansion",
          description: "Leverage your growth momentum to capture additional market share from competitors. Consider aggressive marketing and strategic pricing.",
          actions: ["Competitive displacement strategy", "Market share tracking", "Strategic pricing"]
        }
      ],
      medium: [
        {
          title: "Sustainable Growth Framework",
          description: "Establish systems to sustain growth by identifying key drivers and ensuring scalability. Focus on removing potential bottlenecks.",
          actions: ["Growth driver analysis", "Scalability assessment", "Bottleneck elimination"]
        },
        {
          title: "Customer Success Amplification",
          description: "Strengthen customer success initiatives to ensure retention while growing. Develop case studies from successful customers.",
          actions: ["Success story development", "Referral program", "Customer journey mapping"]
        }
      ],
      low: [
        {
          title: "Growth Monitoring Framework",
          description: "Implement metrics to track growth sustainability and identify early opportunities to increase momentum.",
          actions: ["Growth dashboard", "Leading indicator tracking", "Opportunity scanning"]
        },
        {
          title: "Incremental Improvement Plan",
          description: "Focus on small, continuous improvements to maintain steady growth. Consider A/B testing different approaches.",
          actions: ["A/B testing program", "Continuous improvement", "Small-win strategy"]
        }
      ]
    }
  },
  productMix: {
    critical: [
      {
        title: "Urgent Product Portfolio Restructuring",
        description: "Conduct an emergency review of your product portfolio to reallocate resources away from unprofitable products and toward high-margin offerings.",
        actions: ["Portfolio emergency review", "Resource reallocation", "High-margin focus"]
      },
      {
        title: "Radical Product Strategy Shift",
        description: "Consider discontinuing the lowest-performing products while rapidly scaling high-margin offerings with marketing and sales focus.",
        actions: ["Product discontinuation plan", "High-margin scaling", "Marketing resource shift"]
      }
    ],
    high: [
      {
        title: "Strategic Product Mix Optimization",
        description: "Implement a coordinated strategy to emphasize high-margin products in marketing, sales training, and inventory management.",
        actions: ["Sales incentive restructuring", "Marketing reallocation", "Inventory optimization"]
      },
      {
        title: "Margin Enhancement Program",
        description: "Launch initiatives to improve margins across all products, with targeted strategies for each product segment based on potential.",
        actions: ["Cost reduction analysis", "Price optimization", "Product enhancement"]
      }
    ],
    medium: [
      {
        title: "Balanced Portfolio Approach",
        description: "Gradually shift resources toward higher-margin products while maintaining a diverse product mix to address various customer segments.",
        actions: ["Gradual resource shift", "Portfolio balancing", "Segment-specific strategies"]
      },
      {
        title: "Product Performance Monitoring",
        description: "Implement detailed tracking of product performance metrics to inform future portfolio decisions and identify optimization opportunities.",
        actions: ["Performance dashboard", "Quarterly review process", "Optimization planning"]
      }
    ],
    low: [
      {
        title: "Product Mix Analysis",
        description: "Conduct a thorough analysis of your product mix to identify opportunities for future optimization and resource allocation.",
        actions: ["Mix analysis", "Performance baseline", "Future planning"]
      },
      {
        title: "Incremental Adjustment Strategy",
        description: "Make small, targeted adjustments to product pricing, promotion, and placement to gradually improve overall mix performance.",
        actions: ["Incremental price testing", "Promotion adjustment", "Placement optimization"]
      }
    ]
  },
  priceOptimization: {
    critical: [
      {
        title: "Emergency Pricing Overhaul",
        description: "Implement immediate price corrections for severely underpriced products. Consider a staged approach for high-volume items to minimize market disruption.",
        actions: ["Immediate price correction", "High-volume transition plan", "Communication strategy"]
      },
      {
        title: "Profit Rescue Strategy",
        description: "Launch a comprehensive pricing intervention focusing on the most critical products first. Consider bundling strategies to ease transition.",
        actions: ["Critical product identification", "Bundling strategy", "Value-based pricing"]
      }
    ],
    high: [
      {
        title: "Strategic Price Rebalancing",
        description: "Develop a structured plan to adjust prices across product categories with careful consideration of customer segments and competitive positioning.",
        actions: ["Segment impact analysis", "Competitive positioning", "Price architecture redesign"]
      },
      {
        title: "Value-Based Pricing Implementation",
        description: "Transition to a value-based pricing model for key products, focusing on communicating value to justify higher prices.",
        actions: ["Value proposition development", "Sales training", "Customer communication"]
      }
    ],
    medium: [
      {
        title: "Systematic Price Optimization",
        description: "Implement a data-driven approach to gradually optimize prices across your portfolio, focusing on products with the highest margin improvement potential.",
        actions: ["Price elasticity testing", "Gradual adjustment plan", "Performance tracking"]
      },
      {
        title: "Pricing Capability Enhancement",
        description: "Improve your organization's pricing capabilities through better tools, processes, and training to capture more value consistently.",
        actions: ["Pricing tool implementation", "Process improvement", "Team training"]
      }
    ],
    low: [
      {
        title: "Price Monitoring System",
        description: "Establish systematic monitoring of price performance and competitive positioning to identify future optimization opportunities.",
        actions: ["Monitoring framework", "Competitive tracking", "Regular review process"]
      },
      {
        title: "Experimental Price Testing",
        description: "Implement small-scale price tests for selected products to gather data for future optimization decisions.",
        actions: ["Test design", "Data collection", "Analysis framework"]
      }
    ]
  },
  locationRetention: {
    critical: [
      {
        title: "Key Location Rescue Program",
        description: "Launch an immediate intervention for at-risk key locations, including executive involvement, service level enhancements, and strategic concessions if necessary.",
        actions: ["Executive sponsorship", "Service level enhancement", "Strategic investment"]
      },
      {
        title: "Location Concentration Crisis Plan",
        description: "Immediately address extreme location concentration risk through enhanced relationship management and accelerated market expansion efforts.",
        actions: ["Daily engagement protocol", "Risk mitigation planning", "Diversification acceleration"]
      }
    ],
    high: [
      {
        title: "Strategic Location Management Program",
        description: "Implement a formalized strategic location management program for key regions with regular business reviews, success planning, and executive sponsorship.",
        actions: ["Location planning process", "Business review cadence", "Success metrics tracking"]
      },
      {
        title: "Location Health Monitoring System",
        description: "Develop an early warning system to identify at-risk locations before problems arise, with clear intervention protocols based on risk level.",
        actions: ["Health score implementation", "Intervention playbooks", "Proactive outreach"]
      }
    ],
    medium: [
      {
        title: "Location Success Framework",
        description: "Create a structured location success program focused on delivering measurable value and building deeper relationships with key regional markets.",
        actions: ["Success planning", "Value realization tracking", "Relationship mapping"]
      },
      {
        title: "Balanced Growth Strategy",
        description: "Maintain focus on key locations while implementing targeted expansion efforts to gradually reduce concentration risk.",
        actions: ["Key location management", "Targeted expansion", "Balance monitoring"]
      }
    ],
    low: [
      {
        title: "Regional Strengthening Initiative",
        description: "Enhance performance in key locations through regular engagement, feedback collection, and small value-adds.",
        actions: ["Engagement calendar", "Feedback mechanism", "Value-add identification"]
      },
      {
        title: "Location Portfolio Analysis",
        description: "Regularly analyze your location portfolio to identify concentration risks and market enhancement opportunities.",
        actions: ["Portfolio analysis", "Risk assessment", "Opportunity identification"]
      }
    ]
  },
  locationDiversification: {
    critical: [
      {
        title: "Rapid Market Expansion Campaign",
        description: "Launch an aggressive market expansion initiative targeting new regional segments to quickly reduce dependency on dominant locations.",
        actions: ["Region targeting", "Marketing investment", "Sales incentives"]
      },
      {
        title: "Risk Mitigation Task Force",
        description: "Create a dedicated team focused on rapidly reducing location concentration risk through both expansion and existing location development.",
        actions: ["Dedicated resources", "Weekly progress tracking", "Executive oversight"]
      }
    ],
    high: [
      {
        title: "Market Expansion Strategy",
        description: "Develop and implement a structured approach to enter new markets or regions with high potential for growth.",
        actions: ["Market assessment", "Entry strategy", "Resource allocation"]
      },
      {
        title: "Diversification Incentive Program",
        description: "Implement specific incentives for sales and marketing teams focused on growth in underrepresented regions.",
        actions: ["Incentive design", "Target setting", "Performance tracking"]
      }
    ],
    medium: [
      {
        title: "Balanced Growth Framework",
        description: "Create a framework to ensure new business development is properly balanced across regional segments to gradually reduce concentration.",
        actions: ["Growth planning", "Region targeting", "Balance metrics"]
      },
      {
        title: "Ideal Market Profile Expansion",
        description: "Broaden your ideal market profile to include adjacent regions, with marketing and sales enablement to support expansion.",
        actions: ["Profile development", "Marketing adaptation", "Sales enablement"]
      }
    ],
    low: [
      {
        title: "Location Mix Monitoring",
        description: "Implement regular monitoring of location concentration metrics to track diversification progress and identify emerging risks.",
        actions: ["Metric definition", "Regular reporting", "Trend analysis"]
      },
      {
        title: "Opportunity Scanning Process",
        description: "Establish a process to regularly identify and evaluate opportunities to expand into new regional segments.",
        actions: ["Scanning framework", "Evaluation criteria", "Reporting cadence"]
      }
    ]
  },
  inventoryOptimization: {
    critical: [
      {
        title: "Inventory Reduction Emergency Plan",
        description: "Implement immediate measures to reduce excess inventory, including potential clearance sales, bundle offers, and channel partner arrangements.",
        actions: ["Clearance strategy", "Bundle creation", "Channel partner outreach"]
      },
      {
        title: "Cash Flow Recovery Initiative",
        description: "Focus on converting slow-moving inventory to cash through aggressive promotions, while implementing strict controls on new inventory purchases.",
        actions: ["Promotion design", "Purchasing freeze", "Cash flow tracking"]
      }
    ],
    high: [
      {
        title: "Inventory Management Overhaul",
        description: "Redesign inventory management processes with enhanced forecasting, order quantities, and monitoring to prevent future issues.",
        actions: ["Process redesign", "Forecasting improvement", "Monitoring enhancement"]
      },
      {
        title: "SKU Rationalization Program",
        description: "Systematically evaluate all slow-moving products for potential discontinuation, repositioning, or bundling opportunities.",
        actions: ["Product evaluation", "Discontinuation plan", "Transition strategy"]
      }
    ],
    medium: [
      {
        title: "Balanced Inventory Strategy",
        description: "Implement a more balanced approach to inventory management with category-specific stocking strategies based on turnover and profitability.",
        actions: ["Category strategy", "Stocking rules", "Performance tracking"]
      },
      {
        title: "Slow-Mover Marketing Plan",
        description: "Develop targeted marketing initiatives for slow-moving products to increase visibility and accelerate sales velocity.",
        actions: ["Product highlighting", "Promotional calendar", "Channel strategy"]
      }
    ],
    low: [
      {
        title: "Inventory Health Monitoring",
        description: "Implement regular monitoring of inventory health metrics to identify potential issues before they become significant problems.",
        actions: ["Metric definition", "Monitoring system", "Review process"]
      },
      {
        title: "Continuous Improvement Process",
        description: "Establish a process for regularly reviewing and making small adjustments to inventory management practices.",
        actions: ["Review cadence", "Improvement framework", "Success metrics"]
      }
    ]
  },
  seasonalStrategy: {
    high: [
      {
        title: "Comprehensive Seasonal Planning",
        description: "Develop a detailed seasonal business plan addressing inventory, staffing, marketing, and cash flow considerations for both peak and off-peak periods.",
        actions: ["Season-specific planning", "Resource allocation", "Marketing calendar"]
      },
      {
        title: "Off-Season Revenue Development",
        description: "Create strategies specifically designed to boost revenue during traditionally slow periods through new offerings, promotions, or market expansion.",
        actions: ["Off-season products", "Promotion strategy", "Market targeting"]
      }
    ],
    medium: [
      {
        title: "Seasonal Capacity Optimization",
        description: "Implement flexible capacity management to efficiently handle seasonal fluctuations while maintaining customer satisfaction and controlling costs.",
        actions: ["Capacity planning", "Flexible resources", "Cost management"]
      },
      {
        title: "Balanced Product Portfolio",
        description: "Develop product and service offerings with complementary seasonality to create more consistent demand throughout the year.",
        actions: ["Portfolio analysis", "Complementary development", "Launch timing"]
      }
    ],
    low: [
      {
        title: "Seasonal Performance Tracking",
        description: "Implement enhanced tracking of seasonal performance metrics to build historical data for improved future planning.",
        actions: ["Metric definition", "Data collection", "Year-over-year analysis"]
      },
      {
        title: "Seasonal Adjustment Process",
        description: "Establish a process for making regular adjustments to plans based on seasonal performance and changing market conditions.",
        actions: ["Review cadence", "Adjustment framework", "Performance metrics"]
      }
    ]
  }
};

// Helper function to select a recommendation based on insight type and severity
function getRecommendation(insightType, severity, data = {}) {
  // Default to medium if severity is not specified
  const severityLevel = severity || 'medium';
  
  // Get recommendations for this insight type and severity
  let recommendations = [];
  
  // Handle special cases for trend-based insights
  if (insightType === 'revenueTrend') {
    const trendDirection = data.isDecline ? 'decline' : 'growth';
    recommendations = recommendationDatabase.revenueTrend[trendDirection]?.[severityLevel] || [];
  } else {
    // For other insight types
    recommendations = recommendationDatabase[insightType]?.[severityLevel] || [];
  }
  
  // If no recommendations found for this severity, try to fall back to medium
  if (recommendations.length === 0 && severityLevel !== 'medium') {
    recommendations = recommendationDatabase[insightType]?.['medium'] || [];
  }
  
  // If still no recommendations, return a generic one
  if (recommendations.length === 0) {
    return {
      title: "Review and Optimize",
      description: "Analyze current performance and identify opportunities for improvement.",
      actions: ["Performance analysis", "Opportunity identification", "Action planning"]
    };
  }
  
  // Select a recommendation - could be random or based on data characteristics
  // For simplicity, we'll use the first one, but in a real system you might 
  // have more complex selection logic
  const selectedIndex = data.recommendationIndex || 0;
  return recommendations[selectedIndex % recommendations.length];
}

// Map insight types to severity levels
function mapPriorityToSeverity(priority) {
  if (priority >= 5) return 'critical';
  if (priority >= 4) return 'high';
  if (priority >= 3) return 'medium';
  return 'low';
}

// Get color for different severity levels
function getBadgeColor(severity) {
  switch (severity) {
    case 'critical': return 'bg-red-100 text-red-800';
    case 'high': return 'bg-amber-100 text-amber-800';
    case 'medium': return 'bg-blue-100 text-blue-800';
    case 'low': return 'bg-green-100 text-green-800';
    default: return 'bg-gray-100 text-gray-800';
  }
}

// Helper function to calculate priority based on business metrics
const calculatePriority = (metrics: {
  urgency?: number,  // 1-5: how time-sensitive (5 = immediate)
  impact?: number,   // 1-5: financial impact (5 = highest)
  scope?: number,    // 1-5: how widespread (5 = company-wide)
  trend?: number     // -5 to 5: trend direction and strength (negative = declining)
}) => {
  // Extract metrics with defaults
  const { 
    urgency = 3, 
    impact = 3, 
    scope = 3, 
    trend = 0 
  } = metrics
  
  // Calculate weighted priority score (0-5 scale)
  const priorityScore = (
    (urgency * 0.4) + 
    (impact * 0.3) + 
    (scope * 0.2) + 
    (Math.abs(trend) * 0.1 * (trend < 0 ? 1.2 : 0.8))  // Negative trends get higher priority
  )
  
  // Round to the nearest decimal
  return Math.round(priorityScore * 10) / 10
}

// Helper function to choose the most appropriate recommendation from our database
const getContextualRecommendation = (insightType, data, metrics) => {
  // Calculate overall priority from metrics
  const priority = calculatePriority(metrics);
  
  // Determine severity level based on priority
  let severityLevel = 'medium';
  if (priority >= 5) {
    severityLevel = 'critical';
  } else if (priority >= 4) {
    severityLevel = 'high';
  } else if (priority >= 3) {
    severityLevel = 'medium';
  } else {
    severityLevel = 'low';
  }
  
  // Special case for revenue trend (needs to know if it's growth or decline)
  if (insightType === 'revenueTrend') {
    const isDecline = metrics.trend < 0;
    const recommendationData = {
      isDecline,
      declineRate: data.declineRate,
      totalDecline: data.totalDecline,
      months: data.months,
      // Use data attributes to create variation in recommendations
      recommendationIndex: Math.floor(Math.abs(metrics.trend * 10)) % 2
    };
    
    // Get the recommendation
    const recommendation = getRecommendation('revenueTrend', severityLevel, recommendationData);
    
    return {
      title: isDecline ? "Reverse Revenue Decline" : "Capitalize on Growth Momentum",
      recommendation: recommendation.title,
      description: recommendation.description,
      actions: recommendation.actions,
      priority: priority,
      type: isDecline ? (priority >= 4 ? "destructive" : "warning") : "success",
      metrics: data.metrics || {}
    };
  }
  
  // For other insight types
  const recommendationData = {
    ...data,
    recommendationIndex: Math.floor(priority * 10) % 2 // Use priority to create variation
  };
  
  // Get the recommendation
  const recommendation = getRecommendation(insightType, severityLevel, recommendationData);
  
  return {
    title: data.title || recommendation.title,
    recommendation: recommendation.title,
    description: recommendation.description,
    actions: recommendation.actions,
    priority: priority,
    type: priority >= 4 ? "warning" : (priority >= 3 ? "info" : "default"),
    metrics: data.metrics || {}
  };
}

// Function to generate actionable insights from dashboard data
function generateActionableInsights(data: any) {
  if (!data) return [];
  
  const insights = [];
  
  // 1. Revenue trend insights
  if (data.revenue_data && data.revenue_data.length > 3) {
    const monthOrder = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"];
    
    // Parse month format from data (could be "MM/YYYY" or just "Month")
    const monthFormat = data.revenue_data[0].month.includes('/') ? 'mm/yyyy' : 'month';
    
    // Sort data by month (handling different formats)
    let revenueByMonth = [...data.revenue_data];
    if (monthFormat === 'mm/yyyy') {
      revenueByMonth.sort((a, b) => {
        const [aMonth, aYear] = a.month.split('/');
        const [bMonth, bYear] = b.month.split('/');
        if (aYear !== bYear) return parseInt(aYear) - parseInt(bYear);
        return parseInt(aMonth) - parseInt(bMonth);
      });
    } else {
      revenueByMonth.sort((a, b) => monthOrder.indexOf(a.month) - monthOrder.indexOf(b.month));
    }
    
    // Get last 3 months to check for trends
    const last3Months = revenueByMonth.slice(-3);
    if (last3Months.length === 3) {
      // Calculate rates
      const declineRate1 = (last3Months[1].revenue - last3Months[0].revenue) / last3Months[0].revenue;
      const declineRate2 = (last3Months[2].revenue - last3Months[1].revenue) / last3Months[1].revenue;
      
      // Check for declining trend
      const isDeclineTrend = declineRate1 < 0 && declineRate2 < 0;
      if (isDeclineTrend) {
        const avgDeclineRate = (Math.abs(declineRate1) + Math.abs(declineRate2)) / 2;
        const totalDecline = (last3Months[2].revenue - last3Months[0].revenue) / last3Months[0].revenue;
        
        // Prepare metrics for priority calculation
        const metrics = {
          urgency: Math.abs(totalDecline) > 0.2 ? 5 : Math.abs(totalDecline) > 0.1 ? 4 : 3,
          impact: Math.abs(totalDecline) > 0.3 ? 5 : Math.abs(totalDecline) > 0.2 ? 4 : 3,
          scope: 5, // Company-wide issue
          trend: -Math.min(5, Math.ceil(Math.abs(totalDecline) * 10)) // Negative trend scaled by decline rate
        };
        
        // Get contextual recommendation
        const revenueData = {
          declineRate: avgDeclineRate,
          totalDecline: totalDecline,
          months: last3Months.map(m => m.month),
          metrics: {
            declineRate: Math.abs(totalDecline * 100).toFixed(1) + "%",
            monthlyAvgDecline: (avgDeclineRate * 100).toFixed(1) + "%"
          }
        };
        
        const recommendation = getContextualRecommendation('revenueTrend', revenueData, metrics);
        
        insights.push({
          ...recommendation,
          icon: <TrendingDown className="h-5 w-5 text-amber-500" />,
          category: "Revenue Growth",
          timeframe: "immediate"
        });
      }
      
      // Check for growth trend
      const isGrowthTrend = declineRate1 > 0 && declineRate2 > 0;
      if (isGrowthTrend) {
        const avgGrowthRate = (declineRate1 + declineRate2) / 2;
        const totalGrowth = (last3Months[2].revenue - last3Months[0].revenue) / last3Months[0].revenue;
        
        // Prepare metrics for priority calculation
        const metrics = {
          urgency: 3, // Moderate urgency to capitalize on growth
          impact: totalGrowth > 0.3 ? 5 : totalGrowth > 0.2 ? 4 : 3,
          scope: 4, // Company-wide opportunity
          trend: Math.min(3, Math.ceil(totalGrowth * 10)) // Positive trend
        };
        
        // Get contextual recommendation
        const revenueData = {
          declineRate: -avgGrowthRate, // Negative to indicate growth
          totalDecline: -totalGrowth,  // Negative to indicate growth
          months: last3Months.map(m => m.month),
          metrics: {
            growthRate: (totalGrowth * 100).toFixed(1) + "%",
            monthlyAvgGrowth: (avgGrowthRate * 100).toFixed(1) + "%"
          }
        };
        
        const recommendation = getContextualRecommendation('revenueTrend', revenueData, metrics);
        
        insights.push({
          ...recommendation,
          icon: <TrendingUp className="h-5 w-5 text-green-500" />,
          category: "Revenue Growth",
          timeframe: "short-term"
        });
      }
    }
  }
  
  // 2. Product Mix Insights
  if (data.top_products_data && data.top_products_data.length > 0) {
    const profitMargins = data.top_products_data.map((p: any) => ({
      id: p.id,
      name: p.name || p.product,
      margin: p.margin || (p.profit && p.revenue ? (p.profit / p.revenue) * 100 : 0),
      revenue: p.revenue || 0,
      profit: p.profit || 0
    }));
    
    // Find high and low margin products
    const highMarginProducts = profitMargins
      .filter((p: any) => p.margin > 30)
      .sort((a: any, b: any) => b.margin - a.margin)
      .slice(0, 3);
    
    const lowMarginProducts = profitMargins
      .filter((p: any) => p.margin < 15 && p.margin > 0)
      .sort((a: any, b: any) => a.margin - b.margin)
      .slice(0, 2);
    
    // Calculate metrics for priority
    const highMarginRevenue = highMarginProducts.reduce((sum, p) => sum + p.revenue, 0);
    const lowMarginRevenue = lowMarginProducts.reduce((sum, p) => sum + p.revenue, 0);
    const totalRevenue = profitMargins.reduce((sum, p) => sum + p.revenue, 0);
    
    // Calculate impact based on revenue proportion
    const impactScore = Math.ceil(((highMarginRevenue + lowMarginRevenue) / totalRevenue) * 5);
    
    // Calculate urgency based on margin spread
    const marginSpread = profitMargins.length > 1 ? 
      Math.max(...profitMargins.map(p => p.margin)) - Math.min(...profitMargins.map(p => p.margin)) : 0;
    const urgencyScore = marginSpread > 50 ? 5 : marginSpread > 30 ? 4 : marginSpread > 20 ? 3 : 2;
    
    if (highMarginProducts.length > 0 || lowMarginProducts.length > 0) {
      // Prepare metrics for priority calculation
      const metrics = {
        urgency: urgencyScore,
        impact: impactScore,
        scope: highMarginProducts.length + lowMarginProducts.length > 4 ? 4 : 3
      };
      
      // Product data for recommendation
      const productData = {
        title: "Optimize Product Mix",
        highMarginProducts: highMarginProducts.map(p => p.name),
        lowMarginProducts: lowMarginProducts.map(p => p.name),
        marginSpread: marginSpread,
        metrics: {
          marginSpread: marginSpread.toFixed(1) + "%",
          revenueImpact: ((highMarginRevenue + lowMarginRevenue) / totalRevenue * 100).toFixed(1) + "%"
        }
      };
      
      const recommendation = getContextualRecommendation('productMix', productData, metrics);
      
      insights.push({
        ...recommendation,
        icon: <ShoppingBasket className="h-5 w-5 text-blue-500" />,
        category: "Product Management",
        timeframe: marginSpread > 40 ? "short-term" : "medium-term"
      });
    }
  }
  
  // 3. Location Insights
  if (data.location_revenue_data && data.location_revenue_data.length > 2) {
    const topLocations = [...data.location_revenue_data]
      .sort((a, b) => b.revenue - a.revenue);
    
    const top3Locations = topLocations.slice(0, 3);
    const top3Revenue = top3Locations.reduce((sum, c) => sum + c.revenue, 0);
    const totalRevenue = topLocations.reduce((sum, c) => sum + c.revenue, 0);
    const concentrationRatio = top3Revenue / totalRevenue;
    
    // Prepare metrics for priority calculation
    const metrics = {
      urgency: concentrationRatio > 0.8 ? 5 : concentrationRatio > 0.6 ? 4 : 3,
      impact: 5, // Location retention is always high impact
      scope: 3
    };
    
    // Location data for recommendation
    const locationData = {
      title: "Focus on Key Locations",
      locations: top3Locations.map(c => c.name),
      concentrationRatio: concentrationRatio,
      metrics: {
        topLocationRevenue: (concentrationRatio * 100).toFixed(1) + "%",
        locationCount: top3Locations.length
      }
    };
    
    const recommendation = getContextualRecommendation('locationRetention', locationData, metrics);
    
    insights.push({
      ...recommendation,
      icon: <Users className="h-5 w-5 text-blue-500" />,
      category: "Regional Strategy",
      timeframe: concentrationRatio > 0.8 ? "short-term" : "medium-term"
    });

    // Add location diversification insight if top location has much higher revenue
    if (topLocations.length >= 2) {
      const top1Revenue = topLocations[0].revenue;
      const top1Percent = top1Revenue / totalRevenue;
      const percentDifference = ((topLocations[0].revenue - topLocations[1].revenue) / topLocations[1].revenue) * 100;
      
      if (top1Percent > 0.25 || percentDifference > 50) {
        // Calculate priority
        const divMetrics = {
          urgency: top1Percent > 0.5 ? 5 : top1Percent > 0.3 ? 4 : 3,
          impact: Math.ceil(top1Percent * 5), // Higher impact for higher concentration
          scope: 3,
          trend: 0
        };
        
        // Get recommendation based on severity
        const divData = {
          topLocation: topLocations[0].name,
          concentration: top1Percent,
          metrics: {
            concentration: (top1Percent * 100).toFixed(1) + "%",
            difference: percentDifference.toFixed(1) + "%"
          },
          recommendationIndex: Math.floor(top1Percent * 10) % 2 // Use concentration to select different recommendations
        };
        
        const divRecommendation = getContextualRecommendation('locationDiversification', divData, divMetrics);
        
        insights.push({
          ...divRecommendation,
          icon: <CircleAlert className="h-5 w-5 text-blue-500" />,
          category: "Regional Strategy",
          timeframe: top1Percent > 0.5 ? "short-term" : "long-term"
        });
      }
    }
  }
  
  // 4. Seasonal Strategy
  if (data.revenue_data && data.revenue_data.length > 6) {
    // Parse month format from data (could be "MM/YYYY" or just "Month")
    const monthFormat = data.revenue_data[0].month.includes('/') ? 'mm/yyyy' : 'month';
    
    // Extract month names only
    const revenueByMonth = data.revenue_data.map(item => {
      let month = item.month;
      if (monthFormat === 'mm/yyyy') {
        month = item.month.split('/')[0];
      }
      return {
        ...item,
        shortMonth: month
      };
    });
    
    // Group by month (in case we have multiple years)
    const monthlyAvg = {};
    revenueByMonth.forEach(item => {
      if (!monthlyAvg[item.shortMonth]) {
        monthlyAvg[item.shortMonth] = { total: 0, count: 0 };
      }
      monthlyAvg[item.shortMonth].total += item.revenue;
      monthlyAvg[item.shortMonth].count += 1;
    });
    
    // Calculate averages
    const monthlyAvgArray = Object.keys(monthlyAvg).map(month => ({
      month,
      revenue: monthlyAvg[month].total / monthlyAvg[month].count
    }));
    
    // Find highest and lowest months
    const maxRevenueMonth = monthlyAvgArray.reduce((max, curr) => 
      curr.revenue > max.revenue ? curr : max, monthlyAvgArray[0]
    );
    
    const minRevenueMonth = monthlyAvgArray.reduce((min, curr) => 
      curr.revenue < min.revenue ? curr : min, monthlyAvgArray[0]
    );
    
    if (maxRevenueMonth && minRevenueMonth && maxRevenueMonth.month !== minRevenueMonth.month) {
      // Calculate seasonality strength
      const avgRevenue = monthlyAvgArray.reduce((sum, m) => sum + m.revenue, 0) / monthlyAvgArray.length;
      const peakVariance = maxRevenueMonth.revenue / avgRevenue;
      const troughVariance = avgRevenue / minRevenueMonth.revenue;
      const seasonalityStrength = (peakVariance + troughVariance) / 2;
      
      // Prepare metrics for priority calculation
      const metrics = {
        urgency: seasonalityStrength > 2 ? 4 : seasonalityStrength > 1.5 ? 3 : 2,
        impact: Math.min(5, Math.ceil(seasonalityStrength)),
        scope: 4 // Company-wide planning
      };
      
      // Seasonal data for recommendation
      const seasonalData = {
        title: "Seasonal Strategy",
        peakMonth: maxRevenueMonth.month,
        troughMonth: minRevenueMonth.month,
        seasonalityStrength: seasonalityStrength,
        metrics: {
          peakMonth: maxRevenueMonth.month,
          peakRevenue: "$" + maxRevenueMonth.revenue.toLocaleString(),
          troughMonth: minRevenueMonth.month,
          troughRevenue: "$" + minRevenueMonth.revenue.toLocaleString(),
          seasonalityStrength: seasonalityStrength.toFixed(1) + "x"
        }
      };
      
      const recommendation = getContextualRecommendation('seasonalStrategy', seasonalData, metrics);
      
      insights.push({
        ...recommendation,
        icon: <BarChart4 className="h-5 w-5 text-purple-500" />,
        category: "Planning",
        timeframe: seasonalityStrength > 2 ? "short-term" : "medium-term"
      });
    }
  }
  
  return insights;
}

export default function InsightsPage() {
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState("")
  const [productInsights, setProductInsights] = useState<any[]>([])
  const [customerInsights, setCustomerInsights] = useState<any[]>([])
  const [actionableInsights, setActionableInsights] = useState<any[]>([])
  const [insightMetrics, setInsightMetrics] = useState({ critical: 0, high: 0, medium: 0, low: 0 })
  const [mostUrgentInsight, setMostUrgentInsight] = useState<any>(null)
  const [selectedInsight, setSelectedInsight] = useState<any>(null)
  const [showInsightDetails, setShowInsightDetails] = useState(false)
  
  useEffect(() => {
    const fetchInsights = async () => {
      setIsLoading(true)
      try {
        const data = await getDashboardData()
        
        // Generate insights from data
        const insights = generateActionableInsights(data)
        setActionableInsights(insights)
        
        // Calculate metrics
        const critical = insights.filter(i => mapPriorityToSeverity(i.priority) === 'critical').length
        const high = insights.filter(i => mapPriorityToSeverity(i.priority) === 'high').length
        const medium = insights.filter(i => mapPriorityToSeverity(i.priority) === 'medium').length
        const low = insights.filter(i => mapPriorityToSeverity(i.priority) === 'low').length
        
        setInsightMetrics({
          critical,
          high,
          medium,
          low
        })
        
        // Find most urgent insight (highest priority)
        if (insights.length > 0) {
          const mostUrgent = [...insights].sort((a, b) => b.priority - a.priority)[0]
          setMostUrgentInsight(mostUrgent)
        }
      } catch (e) {
        console.error("Error fetching dashboard data:", e)
        setError("Failed to fetch insights. Please try again later.")
      } finally {
        setIsLoading(false)
      }
    }
    
    fetchInsights()
    
    // Listen for data file changes from other parts of the app
    const handleDataFileChanged = (event: Event) => {
      console.log("Data file changed event received in insights page");
      // Reload insights when data file changes
      fetchInsights();
    };
    
    // Add event listener for data file changes
    window.addEventListener('dataFileChanged', handleDataFileChanged);
    
    // Clean up event listener when component unmounts
    return () => {
      window.removeEventListener('dataFileChanged', handleDataFileChanged);
    };
  }, [])

  // Helper function to get color based on severity/type
  const getSeverityColor = (insight) => {
    if (insight.severityLevel === 'critical' || insight.type === 'destructive') {
      return 'bg-red-50 border-red-200'
    } else if (insight.severityLevel === 'high' || insight.type === 'warning') {
      return 'bg-amber-50 border-amber-200'
    } else if (insight.severityLevel === 'medium' || insight.type === 'success') {
      return 'bg-green-50 border-green-200'
    } else {
      return 'bg-blue-50 border-blue-200'
    }
  }

  // Render an insight card with appropriate styling
  const renderInsightCard = (insight, index, isFeatured = false) => {
    return (
      <Card 
        key={index} 
        className={`${getSeverityColor(insight)} ${isFeatured ? 'border-2' : ''}`}
      >
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <div className="flex items-center gap-2">
            {insight.icon}
            <div>
              <CardTitle className="text-lg flex items-center gap-2">
                {insight.recommendation || insight.title}
                {insight.priority && !isFeatured && (
                  <span className={`text-xs px-2 py-0.5 rounded-full ${getBadgeColor(mapPriorityToSeverity(insight.priority))}`}>
                    {mapPriorityToSeverity(insight.priority)}
                  </span>
                )}
              </CardTitle>
              {insight.category && (
                <div className="flex items-center mt-1 text-xs text-muted-foreground">
                  <span className="mr-3">{insight.category}</span>
                  {insight.timeframe && (
                    <span className="px-1.5 py-0.5 bg-muted rounded-full">{insight.timeframe}</span>
                  )}
                </div>
              )}
            </div>
          </div>
          {isFeatured && insight.priority && (
            <span className={`text-xs px-3 py-1 rounded-full font-medium ${getBadgeColor(mapPriorityToSeverity(insight.priority))}`}>
              {mapPriorityToSeverity(insight.priority) === 'critical' ? 'URGENT' : mapPriorityToSeverity(insight.priority).toUpperCase()}
            </span>
          )}
        </CardHeader>
        <CardContent>
          <CardDescription className="text-base">{insight.description}</CardDescription>
          
          {/* Display metrics in a more structured format */}
          {insight.metrics && Object.keys(insight.metrics).length > 0 && (
            <div className="mt-3 grid grid-cols-2 gap-2">
              {Object.entries(insight.metrics).map(([key, value]) => (
                <div key={key} className="flex flex-col">
                  <span className="text-xs text-muted-foreground capitalize">{key.replace(/([A-Z])/g, ' $1').replace(/_/g, ' ').toLowerCase()}</span>
                  <span className="font-medium">{value}</span>
                </div>
              ))}
            </div>
          )}
          
          {/* Display recommended actions if available */}
          {insight.actions && insight.actions.length > 0 && (
            <div className="mt-4 pt-4 border-t border-border">
              <h4 className="text-sm font-medium mb-2">Recommended Actions:</h4>
              <ul className="text-sm space-y-2">
                {insight.actions.slice(0, 2).map((action, i) => (
                  <li key={i} className="flex items-start">
                    <div className="h-5 w-5 mr-2 flex items-center justify-center flex-shrink-0">
                      <div className="h-1.5 w-1.5 rounded-full bg-primary"></div>
                    </div>
                    <span>{action}</span>
                  </li>
                ))}
                {insight.actions.length > 2 && (
                  <li className="text-xs text-muted-foreground pl-7">
                    +{insight.actions.length - 2} more actions
                  </li>
                )}
              </ul>
            </div>
          )}
          
          <div className="mt-4 flex justify-end space-x-2">
            <Button 
              size="sm" 
              variant="outline"
              onClick={() => {
                setSelectedInsight(insight);
                setShowInsightDetails(true);
              }}
            >
              View Details
            </Button>
            {insight.source === 'action' && (
              <Button size="sm" variant="default">
                Take Action
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    )
  }

  // Add a function to generate more detailed analysis text based on insight type
  const getDetailedAnalysis = (insight) => {
    if (!insight) return '';
    
    const severityLevel = mapPriorityToSeverity(insight.priority);
    
    let analysis = '';
    
    // Generate detailed analysis based on insight category
    if (insight.category === "Regional Strategy") {
      const locationText = insight.locations ? insight.locations.join(", ") : "your top locations";
      if (insight.concentrationRatio > 0.7) {
        analysis = `Your business shows a significant concentration risk with ${insight.metrics?.topLocationRevenue || '60%+'} of revenue coming from just ${insight.metrics?.locationCount || 'a few'} locations. This creates vulnerability if market conditions change in these regions. The recommendation focuses on maintaining these key revenue sources while strategically expanding your geographic footprint.`;
      } else if (insight.concentrationRatio > 0.5) {
        analysis = `Your business has a moderate concentration with ${insight.metrics?.topLocationRevenue || '50-60%'} of revenue from ${insight.metrics?.locationCount || 'a few'} locations. While not critical, this suggests an opportunity to expand your geographic reach while maintaining strong relationships with ${locationText}.`;
      } else {
        analysis = `Your business has a relatively balanced geographic distribution with ${insight.metrics?.topLocationRevenue || 'less than 50%'} of revenue from your top locations. The recommendation focuses on optimizing your regional strategy to maintain this balance while maximizing growth.`;
      }
    } else if (insight.category === "Revenue Growth") {
      if (insight.type === "destructive" || insight.type === "warning") {
        analysis = `Your revenue has declined by ${insight.metrics?.declineRate || 'a significant amount'} over the analyzed period. This consistent downward trend requires ${severityLevel === 'critical' ? 'immediate intervention' : 'attention'} to identify and address the root causes. The recommendation focuses on stopping the decline and rebuilding momentum.`;
      } else {
        analysis = `Your business is experiencing positive growth momentum with a ${insight.metrics?.growthRate || 'significant'} increase in revenue. The recommendation focuses on strategies to capitalize on and sustain this growth trajectory.`;
      }
    } else if (insight.category === "Product Management") {
      analysis = `Your product portfolio shows a profit margin spread of ${insight.metrics?.marginSpread || 'significant variation'}, indicating opportunities for optimization. Your highest margin products (${insight.highMarginProducts?.join(", ") || 'top performers'}) significantly outperform your lowest margin products (${insight.lowMarginProducts?.join(", ") || 'underperformers'}). The recommendation focuses on strategically rebalancing your product mix.`;
    } else if (insight.category === "Planning") {
      analysis = `Your business shows seasonal patterns with peak performance in ${insight.metrics?.peakMonth || 'certain periods'} and lower performance in ${insight.metrics?.troughMonth || 'other periods'}. The seasonality strength is ${insight.metrics?.seasonalityStrength || 'notable'}, requiring strategic planning to maximize opportunities and minimize downtime.`;
    } else {
      analysis = `This ${severityLevel} priority insight identifies an important opportunity for your business. The recommended actions provide a structured approach to address this opportunity.`;
    }
    
    return analysis;
  }

  // Add a function to generate example KPIs for the insight
  const getInsightKPIs = (insight) => {
    if (!insight) return [];
    
    // Generate KPIs based on insight category
    if (insight.category === "Regional Strategy") {
      return [
        { name: "Location Revenue Concentration", current: insight.metrics?.topLocationRevenue || "60.3%", target: "Below 50%" },
        { name: "Geographic Expansion Rate", current: "0 new regions/quarter", target: "1-2 new regions/quarter" },
        { name: "Secondary Location Growth", current: "3% YoY", target: "10% YoY" }
      ];
    } else if (insight.category === "Revenue Growth") {
      if (insight.type === "destructive" || insight.type === "warning") {
        return [
          { name: "Revenue Trend", current: `-${insight.metrics?.declineRate || "5%"} (declining)`, target: "Positive growth" },
          { name: "Customer Retention Rate", current: "82%", target: "90%+" },
          { name: "Sales Conversion Rate", current: "18%", target: "25%" }
        ];
      } else {
        return [
          { name: "Revenue Growth Rate", current: `+${insight.metrics?.growthRate || "12%"}`, target: "Sustain >10%" },
          { name: "Market Share", current: "14%", target: "20%" },
          { name: "Customer Acquisition Cost", current: "$850", target: "Maintain or reduce" }
        ];
      }
    } else if (insight.category === "Product Management") {
      return [
        { name: "Portfolio Profit Margin Spread", current: insight.metrics?.marginSpread || "25%", target: "Below 15%" },
        { name: "High-Margin Product Revenue", current: "30% of total", target: "50% of total" },
        { name: "Low-Margin Product Profitability", current: "5% margin", target: "15% margin or discontinue" }
      ];
    } else if (insight.category === "Planning") {
      return [
        { name: "Seasonal Revenue Variation", current: insight.metrics?.seasonalityStrength || "2.5x", target: "Below 2x" },
        { name: "Off-Season Capacity Utilization", current: "60%", target: "80%" },
        { name: "Peak Season Fulfillment Rate", current: "92%", target: "98%" }
      ];
    } else {
      return [
        { name: "Implementation Rate", current: "0%", target: "100%" },
        { name: "Time to Value", current: "N/A", target: "90 days" }
      ];
    }
  }

  // Add a function to generate detailed implementation steps
  const getDetailedImplementationSteps = (insight) => {
    if (!insight || !insight.actions) return [];
    
    // Map each action to a more detailed step
    return insight.actions.map((action, index) => {
      // Generate a more detailed description based on the action
      let details = '';
      
      // These are examples - in a real application, you might have predefined detailed steps
      if (action.toLowerCase().includes('expansion')) {
        details = 'Conduct market research to identify 3-5 high-potential regions, develop region-specific marketing plans, and allocate resources for targeted expansion.';
      } else if (action.toLowerCase().includes('monitoring')) {
        details = 'Implement weekly KPI tracking dashboards, establish alert thresholds, and assign ownership for regular review and response protocols.';
      } else if (action.toLowerCase().includes('analysis') || action.toLowerCase().includes('audit')) {
        details = 'Gather relevant data from the past 12 months, conduct thorough analysis using standardized frameworks, and document findings with specific opportunities.';
      } else if (action.toLowerCase().includes('strategy')) {
        details = 'Form a cross-functional team, conduct SWOT analysis, identify key strategic initiatives, and develop a phased implementation plan with clear metrics.';
      } else if (action.toLowerCase().includes('pricing')) {
        details = 'Analyze price elasticity by segment, benchmark against competitors, model impact of various pricing scenarios, and develop a controlled rollout plan.';
      } else {
        details = 'Establish clear ownership, timeline, and success metrics. Identify required resources and potential challenges. Create a specific implementation plan with milestones.';
      }
      
      return {
        step: index + 1,
        action,
        details,
        timeframe: index === 0 ? 'Immediate (1-2 weeks)' : index === 1 ? 'Short-term (1-3 months)' : 'Medium-term (3-6 months)'
      };
    });
  }

  return (
    <div className="container mx-auto py-8">
      <h1 className="text-3xl font-bold mb-2">Business Insights</h1>
      <p className="text-muted-foreground mb-6">Data-driven recommendations to improve your business performance</p>

      {isLoading ? (
        <div className="space-y-4">
          <Skeleton className="h-[200px] w-full rounded-lg" />
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <Skeleton className="h-[300px] w-full rounded-lg" />
            <Skeleton className="h-[300px] w-full rounded-lg" />
            <Skeleton className="h-[300px] w-full rounded-lg" />
          </div>
        </div>
      ) : error ? (
        <Alert variant="destructive">
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>
            {error}
          </AlertDescription>
        </Alert>
      ) : (
        <>
          {/* Most Urgent Insight Section */}
          {mostUrgentInsight && (
            <div className="mb-8">
              <h2 className="text-xl font-semibold mb-4 flex items-center">
                <span className="h-2 w-2 rounded-full bg-red-500 mr-2"></span>
                Most Urgent Action
              </h2>
              {renderInsightCard(mostUrgentInsight, 'urgent', true)}
              <div className="mt-4 flex justify-end">
                <Button variant="default" className="gap-2">
                  Create Action Plan <ArrowUpRight size={16} />
                </Button>
              </div>
            </div>
          )}

          {/* Priority Indicators */}
          <div className="mb-6">
            <h2 className="text-xl font-semibold mb-3">Priority Indicators</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <Card className="p-4">
                <div className="flex items-center gap-2">
                  <div className="h-3 w-3 rounded-full bg-red-500"></div>
                  <h3 className="font-medium">Critical</h3>
                </div>
                <p className="text-3xl font-bold mt-2">{insightMetrics.critical}</p>
                <p className="text-xs text-muted-foreground mt-1">Require immediate attention</p>
              </Card>
              <Card className="p-4">
                <div className="flex items-center gap-2">
                  <div className="h-3 w-3 rounded-full bg-amber-500"></div>
                  <h3 className="font-medium">High</h3>
                </div>
                <p className="text-3xl font-bold mt-2">{insightMetrics.high}</p>
                <p className="text-xs text-muted-foreground mt-1">Important to address soon</p>
              </Card>
              <Card className="p-4">
                <div className="flex items-center gap-2">
                  <div className="h-3 w-3 rounded-full bg-blue-500"></div>
                  <h3 className="font-medium">Medium</h3>
                </div>
                <p className="text-3xl font-bold mt-2">{insightMetrics.medium}</p>
                <p className="text-xs text-muted-foreground mt-1">Plan to address these</p>
              </Card>
              <Card className="p-4">
                <div className="flex items-center gap-2">
                  <div className="h-3 w-3 rounded-full bg-green-500"></div>
                  <h3 className="font-medium">Low</h3>
                </div>
                <p className="text-3xl font-bold mt-2">{insightMetrics.low}</p>
                <p className="text-xs text-muted-foreground mt-1">Monitor periodically</p>
              </Card>
            </div>
          </div>

          {/* Category Tabs - Sort actionableInsights by priority within each category */}
          <Tabs defaultValue="all" className="mt-8">
            <TabsList className="mb-4">
              <TabsTrigger value="all">All Insights</TabsTrigger>
              <TabsTrigger value="revenue">Revenue</TabsTrigger>
              <TabsTrigger value="products">Products</TabsTrigger>
              <TabsTrigger value="locations">Locations</TabsTrigger>
              <TabsTrigger value="operations">Operations</TabsTrigger>
            </TabsList>
            
            <TabsContent value="all" className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {actionableInsights.map((insight, index) => renderInsightCard(insight, index))}
            </TabsContent>
            
            <TabsContent value="revenue" className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {actionableInsights
                .filter(insight => insight.category === "Revenue Growth" || insight.category === "Pricing Strategy")
                .sort((a, b) => b.priority - a.priority)
                .map((insight, index) => renderInsightCard(insight, index))}
            </TabsContent>
            
            <TabsContent value="products" className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {actionableInsights
                .filter(insight => insight.category === "Product Management" || insight.category === "Inventory Management")
                .sort((a, b) => b.priority - a.priority)
                .map((insight, index) => renderInsightCard(insight, index))}
            </TabsContent>
            
            <TabsContent value="locations" className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {actionableInsights
                .filter(insight => insight.category === "Regional Strategy")
                .sort((a, b) => b.priority - a.priority)
                .map((insight, index) => renderInsightCard(insight, index))}
            </TabsContent>
            
            <TabsContent value="operations" className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {actionableInsights
                .filter(insight => insight.category === "Planning" || insight.category === "Operations")
                .sort((a, b) => b.priority - a.priority)
                .map((insight, index) => renderInsightCard(insight, index))}
            </TabsContent>
          </Tabs>
        </>
      )}

      <Dialog open={showInsightDetails} onOpenChange={setShowInsightDetails}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          {selectedInsight && (
            <>
              <DialogHeader>
                <div className="flex items-center gap-2">
                  {selectedInsight.icon}
                  <DialogTitle className="text-xl">{selectedInsight.recommendation || selectedInsight.title}</DialogTitle>
                </div>
                <div className="flex items-center mt-1 gap-2">
                  <span className={`px-2 py-0.5 rounded-full text-xs ${getBadgeColor(mapPriorityToSeverity(selectedInsight.priority))}`}>
                    {mapPriorityToSeverity(selectedInsight.priority)}
                  </span>
                  <DialogDescription className="mt-0">{selectedInsight.category} • {selectedInsight.timeframe}</DialogDescription>
                </div>
              </DialogHeader>
              
              <div className="py-4 space-y-6">
                {/* Summary section */}
                <div>
                  <h3 className="text-lg font-semibold mb-2">Summary</h3>
                  <p>{selectedInsight.description}</p>
                </div>
                
                {/* Detailed Analysis section */}
                <div>
                  <h3 className="text-lg font-semibold mb-2">Detailed Analysis</h3>
                  <p className="text-muted-foreground">{getDetailedAnalysis(selectedInsight)}</p>
                </div>
                
                {/* Key Metrics section */}
                {selectedInsight.metrics && Object.keys(selectedInsight.metrics).length > 0 && (
                  <div>
                    <h3 className="text-lg font-semibold mb-2">Key Metrics</h3>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                      {Object.entries(selectedInsight.metrics).map(([key, value]) => (
                        <div key={key} className="bg-muted p-3 rounded-lg">
                          <div className="text-xs text-muted-foreground capitalize">{key.replace(/([A-Z])/g, ' $1').replace(/_/g, ' ').toLowerCase()}</div>
                          <div className="text-lg font-semibold">{value}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                {/* KPI Targets section */}
                <div>
                  <h3 className="text-lg font-semibold mb-2">KPI Targets</h3>
                  <div className="border rounded-lg overflow-hidden">
                    <table className="min-w-full divide-y">
                      <thead className="bg-muted">
                        <tr>
                          <th className="px-4 py-2 text-left text-xs font-medium text-muted-foreground">KPI</th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-muted-foreground">Current</th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-muted-foreground">Target</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y">
                        {getInsightKPIs(selectedInsight).map((kpi, index) => (
                          <tr key={index} className={index % 2 === 0 ? 'bg-background' : 'bg-muted/30'}>
                            <td className="px-4 py-2 text-sm">{kpi.name}</td>
                            <td className="px-4 py-2 text-sm">{kpi.current}</td>
                            <td className="px-4 py-2 text-sm">{kpi.target}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
                
                {/* Implementation Plan section */}
                <div>
                  <h3 className="text-lg font-semibold mb-2">Implementation Plan</h3>
                  <div className="space-y-4">
                    {getDetailedImplementationSteps(selectedInsight).map((step) => (
                      <div key={step.step} className="border-l-2 border-primary pl-4 ml-2">
                        <div className="flex justify-between items-center">
                          <h4 className="font-medium">Step {step.step}: {step.action}</h4>
                          <span className="text-xs bg-muted px-2 py-1 rounded-full">{step.timeframe}</span>
                        </div>
                        <p className="text-sm text-muted-foreground mt-1">{step.details}</p>
                      </div>
                    ))}
                  </div>
                </div>
                
                {/* Expected Outcome section */}
                <div>
                  <h3 className="text-lg font-semibold mb-2">Expected Outcome</h3>
                  <p className="text-muted-foreground">
                    {selectedInsight.category === "Regional Strategy" 
                      ? "Implementing this recommendation will reduce geographic concentration risk, create more balanced revenue streams across regions, and build resilience against localized market fluctuations. Expect more sustainable growth and reduced vulnerability to regional economic changes."
                      : selectedInsight.category === "Revenue Growth" && (selectedInsight.type === "destructive" || selectedInsight.type === "warning")
                      ? "These interventions aim to halt the revenue decline within 60 days and restore positive growth within 90-120 days. Long-term benefits include more stable revenue patterns and improved business resilience."
                      : selectedInsight.category === "Revenue Growth"
                      ? "These actions will help capitalize on current momentum, accelerating growth by an estimated 15-20% above baseline projections while building sustainable processes for long-term expansion."
                      : selectedInsight.category === "Product Management"
                      ? "Rebalancing your product mix should improve overall portfolio profitability by 3-5 percentage points while reducing reliance on underperforming products. Expect more consistent margin performance across product lines."
                      : selectedInsight.category === "Planning"
                      ? "These seasonal strategies should reduce revenue variability by 15-20%, improve off-season utilization, and enhance operational efficiency during peak periods, resulting in more consistent cash flow and resource utilization."
                      : "Successful implementation will address the identified opportunities and help optimize business performance in this area. Expected benefits include improved efficiency, enhanced competitive position, and stronger financial outcomes."
                    }
                  </p>
                </div>
              </div>
              
              <DialogFooter className="flex justify-between items-center">
                <div className="text-xs text-muted-foreground">
                  Priority score: {selectedInsight.priority}/5 • Generated based on your business data
                </div>
                <Button onClick={() => setShowInsightDetails(false)}>Close</Button>
              </DialogFooter>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}
