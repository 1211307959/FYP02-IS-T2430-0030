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
import { ArrowUpRight, BarChart4, CircleAlert, DollarSign, Package, ShoppingBasket, TrendingDown, TrendingUp, Users, RefreshCw } from "lucide-react"
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
function getRecommendation(insightType: string, severity: string, data: Record<string, any> = {}) {
  // Default to medium if severity is not specified
  const severityLevel = severity || 'medium';
  
  // Get recommendations for this insight type and severity
  let recommendations = [];
  
  // Handle special cases for trend-based insights
  if (insightType === 'revenueTrend') {
    const trendDirection = data.isDecline ? 'decline' : 'growth';
    recommendations = (recommendationDatabase.revenueTrend as any)[trendDirection]?.[severityLevel] || [];
  } else {
    // For other insight types
    recommendations = (recommendationDatabase as any)[insightType]?.[severityLevel] || [];
  }
  
  // If no recommendations found for this severity, try to fall back to medium
  if (recommendations.length === 0 && severityLevel !== 'medium') {
    recommendations = (recommendationDatabase as any)[insightType]?.['medium'] || [];
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
function mapPriorityToSeverity(priority: number) {
  if (priority >= 5) return 'critical';
  if (priority >= 4) return 'high';
  if (priority >= 3) return 'medium';
  return 'low';
}

// Get color for different severity levels
function getBadgeColor(severity: string) {
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
const getContextualRecommendation = (insightType: string, data: Record<string, any>, metrics: Record<string, any>) => {
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
      
      // Calculate absolute change for recent months
      const totalAbsoluteChange = last3Months[2].revenue - last3Months[0].revenue;
      const totalRelativeChange = totalAbsoluteChange / last3Months[0].revenue;
      
      // Check for declining trend
      const isDeclineTrend = declineRate1 < 0 && declineRate2 < 0;
      if (isDeclineTrend) {
        const avgDeclineRate = (Math.abs(declineRate1) + Math.abs(declineRate2)) / 2;
        const totalDecline = (last3Months[2].revenue - last3Months[0].revenue) / last3Months[0].revenue;
        
        // Calculate urgency based on the magnitude of decline
        // This ensures that the same insight type can have different priorities based on data
        let severity = "medium";
        if (Math.abs(totalDecline) > 0.2) {
          severity = "critical";
        } else if (Math.abs(totalDecline) > 0.1) {
          severity = "high";
        }
        
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
          category: "Revenue",
          timeframe: "immediate",
          severity: severity
        });
      }
      
      // Check for growth trend
      const isGrowthTrend = declineRate1 > 0 && declineRate2 > 0;
      if (isGrowthTrend) {
        const avgGrowthRate = (declineRate1 + declineRate2) / 2;
        const totalGrowth = (last3Months[2].revenue - last3Months[0].revenue) / last3Months[0].revenue;
        
        // Calculate urgency based on growth rate - higher growth gets higher priority
        // This ensures that the same insight type can have different priorities based on data
        let severity = "medium";
        if (totalGrowth > 0.3) {
          severity = "high";
        } else if (totalGrowth > 0.15) {
          severity = "medium";
        } else {
          severity = "low";
        }
        
        // Prepare metrics for priority calculation
        const metrics = {
          urgency: totalGrowth > 0.3 ? 4 : totalGrowth > 0.15 ? 3 : 2,
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
          category: "Revenue",
          timeframe: "short-term",
          severity: severity
        });
      }
      
      // Check for pricing opportunities based on data
      const hasRevenueData = Boolean(data.revenue_data && data.revenue_data.length);
      const hasProductData = Boolean(data.top_products_data && data.top_products_data.length);
      
      // Only suggest pricing insights if we have enough data to make it meaningful
      if (hasRevenueData && hasProductData && Math.abs(totalRelativeChange) > 0.1) {
        // Determine if pricing could be a factor (if we have revenue changes but quantities haven't changed as much)
        const hasPricingOpportunity = true; // This would normally check quantity vs revenue changes
        
        if (hasPricingOpportunity) {
          // Calculate severity based on the potential impact
          const pricingImpact = Math.abs(totalRelativeChange) * 100;
          let severity = "medium";
          if (pricingImpact > 25) {
            severity = "high";
          } else if (pricingImpact > 15) {
            severity = "medium";
          } else {
            severity = "low";
          }
          
          // Prepare metrics for priority calculation
          const metrics = {
            urgency: pricingImpact > 25 ? 4 : pricingImpact > 15 ? 3 : 2,
            impact: pricingImpact > 25 ? 5 : pricingImpact > 15 ? 4 : 3,
            scope: 4 // Company-wide opportunity
          };
          
          // Pricing data for recommendation
          const pricingData = {
            title: "Optimize Pricing Strategy",
            impact: pricingImpact,
            metrics: {
              potentialImpact: pricingImpact.toFixed(1) + "%",
              revenueChange: totalRelativeChange > 0 ? "+" + (totalRelativeChange * 100).toFixed(1) + "%" : (totalRelativeChange * 100).toFixed(1) + "%"
            }
          };
          
          const recommendation = getContextualRecommendation('priceOptimization', pricingData, metrics);
          
          insights.push({
            ...recommendation,
            icon: <DollarSign className="h-5 w-5 text-emerald-500" />,
            category: "Pricing",
            timeframe: "medium-term",
            severity: severity
          });
        }
    }
  }
}

  // 2. Product Mix Insights
  if (data.top_products_data && data.top_products_data.length >= 3) {
    const profitMargins = data.top_products_data.map((p: any) => ({
      id: p.id,
      name: p.name || p.product,
      margin: p.margin || (p.profit && p.revenue ? (p.profit / p.revenue) * 100 : 0),
      revenue: p.revenue || 0,
      profit: p.profit || 0
    }));
    
    type ProductMargin = {
      id: any;
      name: string;
      margin: number;
      revenue: number;
      profit: number;
    };
    
    // Find high and low margin products
    const highMarginProducts = profitMargins
      .filter((p: ProductMargin) => p.margin > 30)
      .sort((a: ProductMargin, b: ProductMargin) => b.margin - a.margin)
      .slice(0, 3);
    
    const lowMarginProducts = profitMargins
      .filter((p: ProductMargin) => p.margin < 15 && p.margin > 0)
      .sort((a: ProductMargin, b: ProductMargin) => a.margin - b.margin)
      .slice(0, 2);
    
    // Only proceed if we found at least some high or low margin products
    if (highMarginProducts.length > 0 || lowMarginProducts.length > 0) {
    // Calculate metrics for priority
      const highMarginRevenue = highMarginProducts.reduce((sum: number, p: any) => sum + p.revenue, 0);
      const lowMarginRevenue = lowMarginProducts.reduce((sum: number, p: any) => sum + p.revenue, 0);
      const totalRevenue = profitMargins.reduce((sum: number, p: any) => sum + p.revenue, 0);
    
    // Calculate impact based on revenue proportion
    const impactScore = Math.ceil(((highMarginRevenue + lowMarginRevenue) / totalRevenue) * 5);
    
      // Calculate urgency based on margin spread - the wider the spread, the more important to address
    const marginSpread = profitMargins.length > 1 ? 
        Math.max(...profitMargins.map((p: any) => p.margin)) - Math.min(...profitMargins.map((p: any) => p.margin)) : 0;
      
      // Determine severity based on data-driven metrics
      let severity = "medium";
      if (marginSpread > 50) {
        severity = "critical";
      } else if (marginSpread > 30) {
        severity = "high";
      } else if (marginSpread > 20) {
        severity = "medium";
      } else {
        severity = "low";
      }
      
    const urgencyScore = marginSpread > 50 ? 5 : marginSpread > 30 ? 4 : marginSpread > 20 ? 3 : 2;
    
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
        category: "Product",
        timeframe: marginSpread > 40 ? "short-term" : "medium-term",
        severity: severity
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
    
    // Determine severity based on concentration ratio
    let severity = "medium";
    if (concentrationRatio > 0.8) {
      severity = "critical";
    } else if (concentrationRatio > 0.6) {
      severity = "high";
    } else if (concentrationRatio > 0.4) {
      severity = "medium";
    } else {
      severity = "low";
    }
    
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
      category: "Regional",
      timeframe: concentrationRatio > 0.8 ? "short-term" : "medium-term",
      severity: severity
    });

    // Add location diversification insight if top location has much higher revenue
    if (topLocations.length >= 2) {
      const top1Revenue = topLocations[0].revenue;
      const top1Percent = top1Revenue / totalRevenue;
      const percentDifference = ((topLocations[0].revenue - topLocations[1].revenue) / topLocations[1].revenue) * 100;
      
      // Only suggest diversification if there's a significant concentration
      if (top1Percent > 0.25 || percentDifference > 50) {
        // Determine severity based on concentration
        let divSeverity = "medium";
        if (top1Percent > 0.5) {
          divSeverity = "high";
        } else if (top1Percent > 0.3) {
          divSeverity = "medium";
        } else {
          divSeverity = "low";
        }
        
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
          category: "Regional",
          timeframe: top1Percent > 0.5 ? "short-term" : "long-term",
          severity: divSeverity
        });
      }
    }
  }
  
  // 4. Seasonal Strategy
  if (data.revenue_data && data.revenue_data.length > 6) {
    // Parse month format from data (could be "MM/YYYY" or just "Month")
    const monthFormat = data.revenue_data[0].month.includes('/') ? 'mm/yyyy' : 'month';
    
    // Extract month names only
    const revenueByMonth = data.revenue_data.map((item: any) => {
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
    const monthlyAvg: Record<string, { total: number; count: number }> = {};
    revenueByMonth.forEach((item: any) => {
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
      
      // Determine severity based on seasonality strength
      let severity = "medium";
      if (seasonalityStrength > 2.5) {
        severity = "high";
      } else if (seasonalityStrength > 1.5) {
        severity = "medium";
      } else {
        severity = "low";
      }
      
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
        timeframe: seasonalityStrength > 2 ? "short-term" : "medium-term",
        severity: severity
      });
    }
  }
  
  return insights;
}

// Updated to use dynamic backend data
function getDetailedAnalysis(insight: any): string {
  if (!insight) return '';
  
  // Use the detailed_analysis from backend if available
  if (insight.detailed_analysis) {
    return insight.detailed_analysis;
  }
  
  // Fallback to default
  return `This insight is based on analysis of your business data, revealing an opportunity that warrants attention.`;
}

// Function to strip markdown formatting
function stripMarkdown(text: string): string {
  if (!text) return '';
  return text
    .replace(/\*\*/g, '') // Remove ** bold formatting
    .replace(/\*/g, '')   // Remove * italic formatting
    .replace(/#{1,6}\s/g, '') // Remove # headers
    .replace(/`/g, '')    // Remove ` code formatting
    .trim();
}

// Updated to use dynamic backend data
function getInsightKPIs(insight: any) {
  if (!insight) return [];
  
  // Use the kpi_targets from backend if available
  if (insight.kpi_targets && Array.isArray(insight.kpi_targets)) {
    return insight.kpi_targets
      .filter((kpi: any) => kpi.metric && kpi.current && kpi.target) // Filter out invalid KPIs
      .map((kpi: any) => ({
        name: kpi.metric || "KPI", // Use 'metric' not 'kpi'
        current: kpi.current || "N/A",
        target: kpi.target || "N/A"
      }));
  }
  
  // Fallback to default KPIs
  return [
    { name: "Performance Improvement", current: "Baseline", target: "15-25% increase" },
    { name: "Implementation Progress", current: "0%", target: "100% within timeline" },
    { name: "ROI Achievement", current: "0%", target: "≥ 200% within 12 months" }
  ];
}

// Updated to use dynamic backend data
function getDetailedImplementationSteps(insight: any) {
  if (!insight) return [];
  
  // Use the implementation_plan from backend if available
  if (insight.implementation_plan && Array.isArray(insight.implementation_plan)) {
    return insight.implementation_plan.map((step: any, index: number) => ({
      step: step.step || `Step ${index + 1}`,
      action: step.step || "Implementation Step",
      details: step.description || "Execute this implementation step",
      timeframe: step.timeline || "TBD"
    }));
  }
  
  // Fallback to default implementation steps
  return [
    { 
      step: "Step 1", 
      action: "Analyze Current Data", 
      details: "Review the metrics associated with this insight to understand the current situation.", 
      timeframe: "Immediate (1 week)" 
    },
    { 
      step: "Step 2", 
      action: "Identify Improvement Opportunities", 
      details: "Based on the data analysis, identify specific areas where improvements can be made.", 
      timeframe: "Short-term (2 weeks)" 
    },
    { 
      step: "Step 3", 
      action: "Develop Action Plan", 
      details: "Create a targeted plan to address the identified opportunities with clear ownership and timeline.", 
      timeframe: "Short-term (3-4 weeks)" 
    },
    { 
      step: "Step 4", 
      action: "Implement and Monitor", 
      details: "Execute the action plan and establish metrics to track progress and impact.", 
      timeframe: "Ongoing" 
    }
  ];
}

// Updated to use dynamic backend data
function getExpectedOutcome(insight: any): string {
  if (!insight) return '';
  
  // Use the expected_outcome from backend if available
  if (insight.expected_outcome) {
    return insight.expected_outcome;
  }
  
  // Fallback to default
  return "Successful implementation will address the identified opportunities and help optimize business performance in this area. Expected benefits include improved efficiency, enhanced competitive position, and stronger financial results.";
}

export default function InsightsPage() {
  const [insights, setInsights] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedInsight, setSelectedInsight] = useState<any>(null);
  const [showDetailDialog, setShowDetailDialog] = useState(false);
  const [activeTab, setActiveTab] = useState("all");
  
  // Get the most urgent insight for featuring
  const getFeaturedInsight = () => {
    if (insights.length === 0) return null;
    
    // First try to find a critical insight
    const criticalInsight = insights.find(i => i.severity === "critical");
    if (criticalInsight) return criticalInsight;
    
    // Then try to find a high priority insight
    const highInsight = insights.find(i => i.severity === "high");
    if (highInsight) return highInsight;
    
    // Otherwise use the first insight
    return insights[0];
  };
  
  useEffect(() => {
    const fetchInsights = async () => {
      setLoading(true);
      try {
        // Fetch insights directly from the backend
        const response = await fetch('/api/insights', {
          headers: {
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
          }
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data && data.status !== 'error') {
          // Use the insights directly from the backend, but enhance them with frontend logic
          const backendInsights = data.insights || [];
          
          // For now, use the backend insights directly
          // In future, we could combine with frontend-generated insights
          setInsights(backendInsights);
          
          console.log("Loaded insights:", backendInsights);
        } else {
          throw new Error(data?.error || 'Failed to fetch insights');
        }
        setError(null);
      } catch (err) {
        console.error("Error fetching insights:", err);
        setError("Failed to load insights. Please try again later.");
        setInsights([]);
      } finally {
        setLoading(false);
      }
    };
    
    fetchInsights();
    
    // Listen for data file changes from other parts of the app
    const handleDataFileChanged = (event: Event) => {
      console.log("Data file changed event received in insights");
      // Reload insights when file changes
      fetchInsights();
    };
    
    // Add event listener for data file changes
    window.addEventListener('dataFileChanged', handleDataFileChanged);
    
    // Clean up event listener when component unmounts
    return () => {
      window.removeEventListener('dataFileChanged', handleDataFileChanged);
    };
  }, []);

  // Determine severity color
  const getSeverityColor = (insight: any): string => {
    const severity = insight.severity || "medium";
    const colorMap: Record<string, string> = {
      critical: "bg-red-500",
      high: "bg-orange-500",
      medium: "bg-yellow-500",
      low: "bg-green-500"
    };
    return colorMap[severity as keyof typeof colorMap] || "bg-blue-500";
  };

  // Render an insight card
  const renderInsightCard = (insight: any, index: string | number, isFeatured = false) => {
    const severityColor = getSeverityColor(insight);
    const urgencyClass = insight.severity === "critical" ? 
      'bg-gradient-to-br from-red-50 to-red-100 border-red-200' : 
      insight.severity === "high" ? 
        'bg-gradient-to-br from-amber-50 to-amber-100 border-amber-200' : 
        isFeatured ? 'bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-200' : '';
    
    return (
      <Card 
        key={index} 
        className={`${isFeatured ? 'col-span-1 md:col-span-2 lg:col-span-3' : ''} h-full flex flex-col ${urgencyClass}`}
      >
        <CardHeader className="p-4 sm:p-6">
          <div className="flex items-start justify-between">
            <div className="flex flex-col space-y-2">
              <div className="flex items-center space-x-2">
                {insight.icon ? 
                  React.cloneElement(insight.icon, { className: "h-5 w-5 text-muted-foreground" }) :
                  <BarChart4 className="h-5 w-5 text-muted-foreground" />
                }
                <Badge 
                  variant="outline" 
                  className={`text-white ${severityColor} text-xs`}
                >
                  {insight.severity || "Medium"}
                </Badge>
              </div>
                    {insight.category && (
                <Badge variant="secondary" className="text-xs w-fit">
                  {insight.category}
                </Badge>
                        )}
                      </div>
                  </div>
          <CardTitle className="text-base sm:text-lg mt-2">{insight.title}</CardTitle>
          <CardDescription className="text-xs sm:text-sm line-clamp-2">
            {insight.description}
          </CardDescription>
        </CardHeader>
        <CardContent className="flex-grow p-4 sm:p-6 pt-0 sm:pt-0">
          <div className="space-y-2 text-sm">
            {insight.metrics && Array.isArray(insight.metrics) && insight.metrics.map((metric: any, i: number) => (
              <div key={i} className="flex flex-col space-y-1">
                <div className="flex justify-between text-xs">
                  <span>{metric.label}</span>
                  <span className="font-medium">{metric.value}</span>
          </div>
                {metric.progress !== undefined && (
                  <Progress value={metric.progress as number} className="h-1" />
                )}
                </div>
              ))}
            {insight.metrics && !Array.isArray(insight.metrics) && Object.entries(insight.metrics).map(([label, value]: [string, any], i: number) => (
              <div key={`${label}-${i}`} className="flex flex-col space-y-1">
                <div className="flex justify-between text-xs">
                  <span>{label}</span>
                  <span className="font-medium">{String(value)}</span>
            </div>
                    </div>
            ))}
            </div>
        </CardContent>
        <CardFooter className="border-t p-4 sm:p-6">
          <div className="w-full">
            <Button 
              variant="outline"
              className="w-full text-xs sm:text-sm h-8 sm:h-9"
              onClick={() => {
                setSelectedInsight(insight);
                setShowDetailDialog(true);
              }}
            >
              View Details & Recommendations
            </Button>
          </div>
        </CardFooter>
              </Card>
    );
  };

  return (
    <div className="container py-4 sm:py-6 md:py-8 px-2 sm:px-4 md:px-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-4 sm:mb-6">
        <div>
          <h1 className="text-2xl sm:text-3xl md:text-4xl font-bold mb-2 sm:mb-0">Business Insights</h1>
          {!loading && (
            <p className="text-sm text-muted-foreground">
              {insights.length} {insights.length === 1 ? 'data-driven insight' : 'data-driven insights'} available
            </p>
          )}
          </div>
        <Button 
          variant="outline" 
          disabled={loading} 
          onClick={() => window.location.reload()}
          className="self-start sm:self-auto text-xs sm:text-sm"
        >
          <RefreshCw className="mr-2 h-3 sm:h-4 w-3 sm:w-4" />
          Refresh Insights
        </Button>
        </div>

      {error && (
        <Alert variant="destructive" className="mb-4 sm:mb-6">
          <CircleAlert className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
          {[...Array(6)].map((_, i) => (
            <Card key={i} className="h-full">
              <CardHeader>
                <Skeleton className="h-6 w-1/3 mb-2" />
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-2/3 mt-2" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-20 w-full" />
              </CardContent>
              <CardFooter>
                <Skeleton className="h-9 w-full" />
              </CardFooter>
            </Card>
          ))}
        </div>
      ) : (
        <div className="space-y-6">
          {/* Featured Insight */}
          {insights.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
              {renderInsightCard(getFeaturedInsight(), 0, true)}
            </div>
          )}

          {/* All Insights */}
          <Tabs defaultValue="all" value={activeTab} onValueChange={setActiveTab}>
            <div className="flex justify-between items-center mb-2 sm:mb-4">
              <TabsList className="overflow-x-auto flex-nowrap whitespace-nowrap w-auto max-w-[calc(100vw-2rem)] sm:max-w-none">
                <TabsTrigger value="all" className="text-xs sm:text-sm">All Insights</TabsTrigger>
                <TabsTrigger value="critical" className="text-xs sm:text-sm">Critical</TabsTrigger>
                <TabsTrigger value="high" className="text-xs sm:text-sm">High</TabsTrigger>
                <TabsTrigger value="Revenue" className="text-xs sm:text-sm">Revenue</TabsTrigger>
                <TabsTrigger value="Product" className="text-xs sm:text-sm">Product</TabsTrigger>
                <TabsTrigger value="Regional" className="text-xs sm:text-sm">Regional</TabsTrigger>
                <TabsTrigger value="Planning" className="text-xs sm:text-sm">Planning</TabsTrigger>
                <TabsTrigger value="Pricing" className="text-xs sm:text-sm">Pricing</TabsTrigger>
              </TabsList>
                </div>
            
            <TabsContent value="all">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
                {insights.length > 0 ? (
                  insights.filter(insight => insight !== getFeaturedInsight()).map((insight, index) => renderInsightCard(insight, `all-${index}`))
                ) : (
                  <div className="col-span-full text-center py-10">
                    <p>No insights available. Try refreshing the data.</p>
                </div>
                )}
                </div>
            </TabsContent>

            <TabsContent value="critical">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
                {insights.filter(i => i.severity === "critical").length > 0 ? (
                  insights.filter(i => i.severity === "critical").map((insight, index) => renderInsightCard(insight, `critical-${index}`))
                ) : (
                  <div className="col-span-full text-center py-10">
                    <p>No critical insights found. That's good news!</p>
                </div>
                )}
            </div>
            </TabsContent>
            
            <TabsContent value="high">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
                {insights.filter(i => i.severity === "high").length > 0 ? (
                  insights.filter(i => i.severity === "high").map((insight, index) => renderInsightCard(insight, `high-${index}`))
                ) : (
                  <div className="col-span-full text-center py-10">
                    <p>No high priority insights found.</p>
          </div>
                )}
              </div>
            </TabsContent>
            
            <TabsContent value="Revenue">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
                {insights.filter(i => i.category === "Revenue").length > 0 ? (
                  insights.filter(i => i.category === "Revenue").map((insight, index) => renderInsightCard(insight, `revenue-${index}`))
                ) : (
                  <div className="col-span-full text-center py-10">
                    <p>No revenue insights available.</p>
                  </div>
                )}
              </div>
            </TabsContent>
            
            <TabsContent value="Product">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
                {insights.filter(i => i.category === "Product").length > 0 ? (
                  insights.filter(i => i.category === "Product").map((insight, index) => renderInsightCard(insight, `product-${index}`))
                ) : (
                  <div className="col-span-full text-center py-10">
                    <p>No product insights available.</p>
                  </div>
                )}
              </div>
            </TabsContent>
            
            <TabsContent value="Regional">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
                {insights.filter(i => i.category === "Regional").length > 0 ? (
                  insights.filter(i => i.category === "Regional").map((insight, index) => renderInsightCard(insight, `regional-${index}`))
                ) : (
                  <div className="col-span-full text-center py-10">
                    <p>No regional insights available.</p>
                  </div>
                )}
              </div>
            </TabsContent>
            
            <TabsContent value="Planning">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
                {insights.filter(i => i.category === "Planning").length > 0 ? (
                  insights.filter(i => i.category === "Planning").map((insight, index) => renderInsightCard(insight, `planning-${index}`))
                ) : (
                  <div className="col-span-full text-center py-10">
                    <p>No planning insights available.</p>
                  </div>
                )}
              </div>
            </TabsContent>
            
            <TabsContent value="Pricing">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
                {insights.filter(i => i.category === "Pricing").length > 0 ? (
                  insights.filter(i => i.category === "Pricing").map((insight, index) => renderInsightCard(insight, `pricing-${index}`))
                ) : (
                  <div className="col-span-full text-center py-10">
                    <p>No pricing insights available.</p>
                  </div>
                )}
              </div>
        </TabsContent>
      </Tabs>
        </div>
      )}

      {/* Insight Detail Dialog */}
      <Dialog open={showDetailDialog} onOpenChange={setShowDetailDialog}>
        <DialogContent className="w-[90vw] max-w-full sm:max-w-lg md:max-w-2xl lg:max-w-4xl max-h-[90vh] sm:max-h-[80vh] overflow-y-auto">
          {selectedInsight && (
            <>
              <DialogHeader>
                <div className="flex items-center space-x-2 mb-2">
                  <Badge 
                    variant="outline" 
                    className={`text-white ${getSeverityColor(selectedInsight)} text-xs`}
                  >
                    {selectedInsight.severity || "Medium"}
                  </Badge>
                  <span className="text-sm text-muted-foreground">
                    {selectedInsight.category} insight
                  </span>
                </div>
                <DialogTitle className="text-xl">{selectedInsight.title}</DialogTitle>
                <DialogDescription className="text-sm">
                  {selectedInsight.description}
                </DialogDescription>
              </DialogHeader>
              
              <div className="py-4 space-y-6">
                {/* Summary section */}
                <div>
                  <h3 className="text-lg font-semibold mb-2">Summary</h3>
                  <p>{stripMarkdown(selectedInsight.description)}</p>
                </div>
                
                {/* Detailed Analysis section */}
                <div>
                  <h3 className="text-lg font-semibold mb-2">Detailed Analysis</h3>
                  <p className="text-muted-foreground">{stripMarkdown(selectedInsight.detailed_analysis || getDetailedAnalysis(selectedInsight))}</p>
                </div>
                
                {/* Key Metrics section */}
                {selectedInsight.metrics && Object.keys(selectedInsight.metrics).length > 0 && (
                  <div>
                    <h3 className="text-lg font-semibold mb-2">Key Metrics</h3>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                      {Object.entries(selectedInsight.metrics).map(([key, value]: [string, any], i: number) => (
                        <div key={`${key}-${i}`} className="bg-muted p-3 rounded-lg">
                          <div className="text-xs text-muted-foreground capitalize">{key.replace(/([A-Z])/g, ' $1').replace(/_/g, ' ').toLowerCase()}</div>
                          <div className="text-lg font-semibold">{String(value)}</div>
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
                
                {/* Recommended Action section */}
                <div>
                  <h3 className="text-lg font-semibold mb-2">Recommended Action</h3>
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <p className="text-sm">
                      {stripMarkdown(selectedInsight.recommended_action || selectedInsight.action_plan || "Use data-driven approaches to address this opportunity.")}
                    </p>
                  </div>
                </div>
                
                {/* Business Impact section */}
                <div>
                  <h3 className="text-lg font-semibold mb-2">Business Impact</h3>
                  <p className="text-muted-foreground">
                    {stripMarkdown(selectedInsight.business_impact || selectedInsight.why_it_matters || getExpectedOutcome(selectedInsight))}
                  </p>
                </div>
                
                {/* Model Integration section */}
                {selectedInsight.model_integration && (
                  <div>
                    <h3 className="text-lg font-semibold mb-2">Next Steps</h3>
                    <p className="text-muted-foreground text-sm">
                      {stripMarkdown(selectedInsight.model_integration)}
                    </p>
                  </div>
                )}
              </div>
              
              <DialogFooter className="flex justify-between items-center">
                <div className="text-xs text-muted-foreground">
                  Priority score: {selectedInsight.priority_score ? Math.round(selectedInsight.priority_score) : selectedInsight.priority || 'N/A'} • Generated based on your business data
                </div>
                <Button onClick={() => setShowDetailDialog(false)}>Close</Button>
              </DialogFooter>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}
