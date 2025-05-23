"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  CircleAlert, 
  TrendingDown, 
  TrendingUp, 
  Zap, 
  AlertCircle,
  BarChart4, 
  ShoppingBasket, 
  DollarSign,
  Users,
  Package
} from "lucide-react"
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert"
import { getDashboardData } from "@/lib/api"

export const dynamic = 'force-dynamic'; // Force dynamic rendering to prevent stale data

// Enhanced insight generation functions
function generateProfitInsights(productData: any[]) {
  if (!productData || productData.length === 0) return []
  
  // Check for data validity
  if (!productData.every(p => p.name && typeof p.profit === 'number')) {
    console.warn("Some product data is missing name or profit properties:", productData);
    return [];
  }
  
  const insights = [];
  
  // Ensure no overlap between top and bottom products
  // First, separate products by their rank
  const topRanked = productData.filter(p => p.rank === 'top' || !p.rank);
  const bottomRanked = productData.filter(p => p.rank === 'bottom');
  
  // Sort by profit (highest to lowest for top, lowest to highest for bottom)
  const topProducts = [...topRanked].sort((a, b) => b.profit - a.profit);
  const bottomProducts = [...bottomRanked].sort((a, b) => a.profit - b.profit);
  
  // Log for debugging
  console.log("Top product candidates:", topProducts.slice(0, 5).map(p => `${p.name} (ID: ${p.id}): $${p.profit}`).join(', '));
  console.log("Bottom product candidates:", bottomProducts.slice(0, 5).map(p => `${p.name} (ID: ${p.id}): $${p.profit}`).join(', '));
  
  // Check for product ID overlaps between top and bottom lists
  const topProductIds = new Set(topProducts.slice(0, 5).map(p => p.id));
  const bottomProductIds = new Set(bottomProducts.slice(0, 5).map(p => p.id));
  
  // Find any overlapping IDs
  const overlappingIds = Array.from(topProductIds).filter(id => bottomProductIds.has(id));
  console.log("Overlapping product IDs:", overlappingIds);
  
  // If we have overlaps, remove them from the bottom list
  if (overlappingIds.length > 0) {
    console.log("Removing overlapping products from bottom candidates");
    const filteredBottomProducts = bottomProducts.filter(p => !topProductIds.has(p.id));
    // Replace the bottom products list with the filtered one
    bottomProducts.splice(0, bottomProducts.length, ...filteredBottomProducts);
  }
  
  // Get true top product from sorted list
  if (topProducts.length > 0) {
    const topProduct = topProducts[0];
    insights.push({
      title: "Top Profit Generator",
      description: `${topProduct.name} is your highest profit generator with $${topProduct.profit.toLocaleString()} in profits.`,
      icon: <TrendingUp className="h-5 w-5 text-green-500" />,
      type: "success"
    });
  }
  
  // Only add insight for bottom product if the array has any left after deduplication
  if (bottomProducts.length > 0) {
    const lowestProfit = bottomProducts[0];
    // Double check it's not in the top products
    if (!topProductIds.has(lowestProfit.id)) {
      insights.push({
        title: "Profit Improvement Opportunity",
        description: `${lowestProfit.name} has the lowest profit. Consider adjusting pricing or costs.`,
        icon: <TrendingDown className="h-5 w-5 text-amber-500" />,
        type: "warning"
      });
    } else {
      console.warn(`Skipping bottom product insight for ${lowestProfit.name} as it appears in top products (should not happen after deduplication)`);
    }
  }
  
  // Add overall profit margin insight if we have more than one product
  if (productData.length > 1) {
    const totalProfit = productData.reduce((sum, item) => sum + item.profit, 0)
    const avgProfit = totalProfit / productData.length
    
    const profitVariance = productData.some(p => p.profit < avgProfit * 0.5)
    
    if (profitVariance) {
      insights.push({
        title: "Profit Variance Alert",
        description: "There's significant variance in product profitability. Consider standardizing pricing strategies.",
        icon: <AlertCircle className="h-5 w-5 text-amber-500" />,
        type: "warning"
      })
    }
  }
  
  return insights
}

function generateRevenueInsights(customerData: any[], revenueData: any[]) {
  if (!customerData || customerData.length === 0) return []
  
  // Find top revenue customers
  const sortedByRevenue = [...customerData].sort((a, b) => b.revenue - a.revenue)
  const topCustomer = sortedByRevenue[0]
  const secondCustomer = sortedByRevenue.length > 1 ? sortedByRevenue[1] : null
  
  const insights = [
    {
      title: "Key Account Alert",
      description: `${topCustomer.name} is your top revenue source, generating $${topCustomer.revenue.toLocaleString()}.`,
      icon: <Zap className="h-5 w-5 text-blue-500" />,
      type: "info"
    }
  ]
  
  // Add concentration risk insight if we have a second customer
  if (secondCustomer) {
    const percentDifference = ((topCustomer.revenue - secondCustomer.revenue) / secondCustomer.revenue) * 100
    
    if (percentDifference > 50) {
      insights.push({
        title: "Revenue Concentration Risk",
        description: `Your top customer generates ${percentDifference.toFixed(1)}% more revenue than your second-highest customer, creating dependency risk.`,
        icon: <CircleAlert className="h-5 w-5 text-amber-500" />,
        type: "warning"
      })
    }
  }
  
  // Analyze revenue trends if we have revenue data
  if (revenueData && revenueData.length > 1) {
    // Check if last month's revenue is better or worse than previous month
    const monthOrder = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    const sortedRevenue = [...revenueData].sort((a, b) => monthOrder.indexOf(a.month) - monthOrder.indexOf(b.month))
    
    const lastMonth = sortedRevenue[sortedRevenue.length - 1]
    const previousMonth = sortedRevenue[sortedRevenue.length - 2]
    
    if (lastMonth && previousMonth) {
      const change = ((lastMonth.revenue - previousMonth.revenue) / previousMonth.revenue) * 100
      
      if (change > 0) {
        insights.push({
          title: "Positive Revenue Trend",
          description: `Revenue increased by ${change.toFixed(1)}% from ${previousMonth.month} to ${lastMonth.month}.`,
          icon: <BarChart4 className="h-5 w-5 text-green-500" />,
          type: "success"
        })
      } else if (change < 0) {
        insights.push({
          title: "Revenue Decline",
          description: `Revenue decreased by ${Math.abs(change).toFixed(1)}% from ${previousMonth.month} to ${lastMonth.month}.`,
          icon: <TrendingDown className="h-5 w-5 text-red-500" />,
          type: "destructive"
        })
      }
    }
  }
  
  return insights
}

function generateProductInsights(productData: any[]) {
  if (!productData || productData.length === 0) return []

  // Check for data validity
  if (!productData.every(p => p.name && typeof p.revenue === 'number')) {
    console.warn("Some product data is missing name or revenue properties:", productData);
    return [];
  }

  const insights = [];
  
  // Find top revenue product using sorting
  const sortedByRevenue = [...productData]
    .filter(p => p && p.revenue !== undefined && p.name)
    .sort((a, b) => b.revenue - a.revenue);
    
  // Safety check
  if (sortedByRevenue.length === 0) return [];
  
  const topProduct = sortedByRevenue[0];
  
  // Add top product insight
  insights.push({
    title: "Top Selling Product",
    description: `${topProduct.name} is your best-selling product generating $${topProduct.revenue.toLocaleString()} in revenue.`,
    icon: <ShoppingBasket className="h-5 w-5 text-green-500" />,
    type: "success"
  });
  
  // Find the product with lowest revenue that's different from the top
  const bottomProducts = sortedByRevenue
    .filter(p => p.id !== topProduct.id)
    .slice(-1);
    
  // Only add bottom product insight if we found one and it's significantly underperforming
  if (bottomProducts.length > 0) {
    const bottomProduct = bottomProducts[0];
    if (bottomProduct.revenue < topProduct.revenue * 0.2) {
      insights.push({
        title: "Underperforming Product",
        description: `${bottomProduct.name} is generating significantly less revenue than your top products. Consider promotion or replacement.`,
        icon: <TrendingDown className="h-5 w-5 text-amber-500" />,
        type: "warning"
      });
    }
  }
  
  return insights
}

function generateActionableInsights(data: any) {
  const insights = []
  
  // 1. Data-driven product mix recommendations
  if (data.top_products_data && data.top_products_data.length > 0) {
    const profitMargins = data.top_products_data.map((p: any) => ({
      name: p.name,
      margin: p.profit && p.revenue ? (p.profit / p.revenue) * 100 : 0
    }))
    
    const highMarginProducts = profitMargins
      .filter((p: {name: string, margin: number}) => p.margin > 30)
      .map((p: {name: string, margin: number}) => p.name)
      .slice(0, 3)
    
    const lowMarginProducts = profitMargins
      .filter((p: {name: string, margin: number}) => p.margin < 15 && p.margin > 0)
      .map((p: {name: string, margin: number}) => p.name)
      .slice(0, 2)
    
    if (highMarginProducts.length > 0) {
      insights.push({
        title: "Optimize Product Mix",
        description: `Focus on promoting high-margin products${highMarginProducts.length > 0 ? ' like ' + highMarginProducts.join(', ') : ''} while reevaluating low-margin offerings${lowMarginProducts.length > 0 ? ' such as ' + lowMarginProducts.join(', ') : ''}.`,
        icon: <ShoppingBasket className="h-5 w-5 text-blue-500" />,
        type: "info",
        category: "Product Management",
        timeframe: "medium-term",
        priority: 3
      })
    }
  } else {
    // Fallback if no product data
    insights.push({
      title: "Optimize Product Mix",
      description: "Focus on promoting high-margin products while reevaluating low-margin offerings.",
      icon: <ShoppingBasket className="h-5 w-5 text-blue-500" />,
      type: "info",
      category: "Product Management",
      timeframe: "medium-term",
      priority: 3
    })
  }
  
  // 2. Add price optimization insights
  if (data.product_revenue_data && data.product_revenue_data.length > 0) {
    const potentialProducts = data.product_revenue_data
      .filter((p: any) => p.quantity > 100 && p.profit && p.revenue && (p.profit/p.revenue < 0.25))
      .slice(0, 2)
      .map((p: any) => p.name)
    
    if (potentialProducts.length > 0) {
      insights.push({
        title: "Price Optimization Opportunity",
        description: `Consider testing higher prices for high-volume, low-margin products like ${potentialProducts.join(', ')}.`,
        icon: <DollarSign className="h-5 w-5 text-green-500" />,
        type: "success",
        category: "Pricing Strategy",
        timeframe: "short-term",
        priority: 5
      })
    }
  }
  
  // 3. Add customer retention recommendations
  if (data.customer_revenue_data && data.customer_revenue_data.length > 2) {
    const topCustomers = [...data.customer_revenue_data]
      .sort((a, b) => b.revenue - a.revenue)
      .slice(0, 3)
      .map(c => c.name)
      
    insights.push({
      title: "Focus on Customer Retention",
      description: `Develop retention strategies for key accounts like ${topCustomers.join(', ')} to secure long-term revenue.`,
      icon: <Users className="h-5 w-5 text-blue-500" />,
      type: "info",
      category: "Customer Relations",
      timeframe: "long-term",
      priority: 4
    })
    
    // Customer diversification (if top customer has much higher revenue)
    if (data.customer_revenue_data.length >= 2) {
      const sorted = [...data.customer_revenue_data].sort((a, b) => b.revenue - a.revenue)
      const percentDifference = ((sorted[0].revenue - sorted[1].revenue) / sorted[1].revenue) * 100
      
      if (percentDifference > 50) {
        insights.push({
          title: "Customer Diversification",
          description: `Reduce dependency risk by expanding your customer base beyond ${sorted[0].name}, which represents a significant revenue concentration.`,
          icon: <CircleAlert className="h-5 w-5 text-blue-500" />,
          type: "info",
          category: "Customer Relations",
          timeframe: "long-term",
          priority: 3
        })
      } else {
        insights.push({
          title: "Customer Diversification",
          description: "Reduce dependency risk by expanding your customer base beyond current top accounts.",
          icon: <CircleAlert className="h-5 w-5 text-blue-500" />,
          type: "info",
          category: "Customer Relations",
          timeframe: "long-term",
          priority: 2
        })
      }
    }
  } else {
    // Fallback if no customer data
    insights.push({
      title: "Customer Diversification",
      description: "Reduce dependency risk by expanding your customer base beyond current top accounts.",
      icon: <CircleAlert className="h-5 w-5 text-blue-500" />,
      type: "info",
      category: "Customer Relations",
      timeframe: "long-term",
      priority: 2
    })
  }
  
  // 4. Add trend-based recommendations
  if (data.revenue_data && data.revenue_data.length > 3) {
    const monthOrder = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    const revenueByMonth = [...data.revenue_data]
      .sort((a, b) => monthOrder.indexOf(a.month) - monthOrder.indexOf(b.month))
    
    // Check for declining trends
    const last3Months = revenueByMonth.slice(-3)
    if (last3Months.length === 3) {
      const isDeclineTrend = last3Months[2].revenue < last3Months[1].revenue && 
                          last3Months[1].revenue < last3Months[0].revenue
      
      if (isDeclineTrend) {
        insights.push({
          title: "Reverse Revenue Decline",
          description: `Revenue has declined for 3 consecutive months (${last3Months.map(m => m.month).join(', ')}). Consider promotional campaigns or new product introductions.`,
          icon: <TrendingUp className="h-5 w-5 text-amber-500" />,
          type: "warning",
          category: "Pricing Strategy",
          timeframe: "short-term",
          priority: 5
        })
      }
    }
  }
  
  // 5. Add inventory management recommendations
  if (data.product_revenue_data && data.product_revenue_data.length > 0) {
    const slowMovingProducts = data.product_revenue_data
      .filter((p: any) => p.quantity < 10 && p.revenue > 0)
      .slice(0, 2)
      .map((p: any) => p.name)
    
    if (slowMovingProducts.length > 0) {
      insights.push({
        title: "Inventory Optimization",
        description: `Consider reducing inventory for slow-moving products like ${slowMovingProducts.join(', ')} to improve cash flow.`,
        icon: <Package className="h-5 w-5 text-blue-500" />,
        type: "info",
        category: "Product Management",
        timeframe: "short-term",
        priority: 3
      })
    }
  }
  
  // 6. Add seasonal recommendations if we have revenue data
  if (data.revenue_data && data.revenue_data.length > 0) {
    const monthOrder = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    const revenueByMonth = [...data.revenue_data].sort((a, b) => 
      monthOrder.indexOf(a.month) - monthOrder.indexOf(b.month)
    )
    
    // Find highest revenue month
    const maxRevenueMonth = revenueByMonth.reduce((max, curr) => 
      curr.revenue > max.revenue ? curr : max, revenueByMonth[0]
    )
    
    // Find lowest revenue month
    const minRevenueMonth = revenueByMonth.reduce((min, curr) => 
      curr.revenue < min.revenue ? curr : min, revenueByMonth[0]
    )
    
    if (maxRevenueMonth && minRevenueMonth && maxRevenueMonth.month !== minRevenueMonth.month) {
      insights.push({
        title: "Seasonal Strategy",
        description: `Plan inventory and promotions around your peak month (${maxRevenueMonth.month}) and develop strategies to boost sales during slower months like ${minRevenueMonth.month}.`,
        icon: <BarChart4 className="h-5 w-5 text-purple-500" />,
        type: "info",
        category: "Planning",
        timeframe: "long-term",
        priority: 4
      })
    }
  }
  
  // 7. Sort insights by priority
  return insights.sort((a, b) => b.priority - a.priority)
}

export default function InsightsPage() {
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState("")
  const [productInsights, setProductInsights] = useState<any[]>([])
  const [customerInsights, setCustomerInsights] = useState<any[]>([])
  const [actionableInsights, setActionableInsights] = useState<any[]>([])
  
  useEffect(() => {
    const fetchInsights = async () => {
      setIsLoading(true)
      setError("")
      
      try {
        // Get dashboard data to generate insights
        const data = await getDashboardData()
        
        // Generate insights from data
        setProductInsights([
          ...generateProfitInsights(data.top_products_data || []),
          ...generateProductInsights(data.product_revenue_data || [])
        ])
        
        setCustomerInsights(
          generateRevenueInsights(data.customer_revenue_data || [], data.revenue_data || [])
        )
        
        // Generate actionable business recommendations
        setActionableInsights(generateActionableInsights(data))
        
      } catch (err) {
        console.error("Error generating insights:", err)
        setError("Failed to generate insights. Please try again later.")
      } finally {
        setIsLoading(false)
      }
    }
    
    fetchInsights()
  }, [])

  return (
    <div className="container py-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold tracking-tight">Actionable Insights</h1>
      </div>

      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}
      
      {isLoading ? (
        <div className="flex items-center justify-center h-40">
          <div className="text-lg text-muted-foreground">Generating insights...</div>
        </div>
      ) : (
        <Tabs defaultValue="product" className="space-y-4">
        <TabsList>
            <TabsTrigger value="product">Product Insights</TabsTrigger>
            <TabsTrigger value="customer">Customer Insights</TabsTrigger>
            <TabsTrigger value="actions">Recommended Actions</TabsTrigger>
        </TabsList>

          <TabsContent value="product" className="space-y-4">
            {productInsights.length === 0 ? (
              <Card>
                <CardContent className="pt-6">
                  <p className="text-muted-foreground">No product insights available. Add more data to generate insights.</p>
                </CardContent>
              </Card>
            ) : (
              productInsights.map((insight, index) => (
                <Card key={index}>
                  <CardHeader className="flex flex-row items-center gap-2">
                    {insight.icon}
                    <CardTitle className="text-lg">{insight.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <CardDescription className="text-base">{insight.description}</CardDescription>
                  </CardContent>
                </Card>
              ))
            )}
        </TabsContent>

        <TabsContent value="customer" className="space-y-4">
            {customerInsights.length === 0 ? (
              <Card>
                <CardContent className="pt-6">
                  <p className="text-muted-foreground">No customer insights available. Add more data to generate insights.</p>
                </CardContent>
              </Card>
            ) : (
              customerInsights.map((insight, index) => (
                <Card key={index}>
                  <CardHeader className="flex flex-row items-center gap-2">
                    {insight.icon}
                    <CardTitle className="text-lg">{insight.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <CardDescription className="text-base">{insight.description}</CardDescription>
                  </CardContent>
                </Card>
              ))
            )}
        </TabsContent>

          <TabsContent value="actions" className="space-y-4">
            {actionableInsights.map((insight, index) => (
              <Card key={index}>
                <CardHeader className="flex flex-row items-center gap-2">
                  {insight.icon}
                  <div className="flex flex-col">
                    <CardTitle className="text-lg">{insight.title}</CardTitle>
                    {insight.category && (
                      <div className="flex items-center mt-1 text-xs text-muted-foreground">
                        <span className="mr-3">{insight.category}</span>
                        {insight.timeframe && (
                          <span className="px-1.5 py-0.5 bg-muted rounded-full">{insight.timeframe}</span>
                        )}
                      </div>
                    )}
                  </div>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-base">{insight.description}</CardDescription>
                </CardContent>
              </Card>
            ))}
        </TabsContent>
      </Tabs>
      )}
    </div>
  )
}
