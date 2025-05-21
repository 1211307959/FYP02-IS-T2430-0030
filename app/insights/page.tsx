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
  DollarSign 
} from "lucide-react"
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert"
import { getDashboardData } from "@/lib/api"

// Enhanced insight generation functions
function generateProfitInsights(productData: any[]) {
  if (!productData || productData.length === 0) return []
  
  // Find products with highest and lowest profit margins
  const sortedByProfit = [...productData].sort((a, b) => b.profit - a.profit)
  const highestProfit = sortedByProfit[0]
  const lowestProfit = sortedByProfit[sortedByProfit.length - 1]
  
  const insights = [
    {
      title: "Top Profit Generator",
      description: `${highestProfit.name} is your highest profit generator with $${highestProfit.profit.toLocaleString()} in profits.`,
      icon: <TrendingUp className="h-5 w-5 text-green-500" />,
      type: "success"
    },
    {
      title: "Profit Improvement Opportunity",
      description: `${lowestProfit.name} has the lowest profit. Consider adjusting pricing or costs.`,
      icon: <TrendingDown className="h-5 w-5 text-amber-500" />,
      type: "warning"
    }
  ]
  
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

  // Find best performing and worst performing products
  const sortedByRevenue = [...productData].sort((a, b) => b.revenue - a.revenue)
  const topProduct = sortedByRevenue[0]
  const bottomProduct = sortedByRevenue[sortedByRevenue.length - 1]
  
  const insights = [
    {
      title: "Top Selling Product",
      description: `${topProduct.name} is your best-selling product generating $${topProduct.revenue.toLocaleString()} in revenue.`,
      icon: <ShoppingBasket className="h-5 w-5 text-green-500" />,
      type: "success"
    }
  ]
  
  // Add recommendation for underperforming product
  if (bottomProduct.revenue < topProduct.revenue * 0.2) {
    insights.push({
      title: "Underperforming Product",
      description: `${bottomProduct.name} is generating significantly less revenue than your top products. Consider promotion or replacement.`,
      icon: <TrendingDown className="h-5 w-5 text-amber-500" />,
      type: "warning"
    })
  }
  
  return insights
}

function generateActionableInsights(data: any) {
  const insights = [
    {
      title: "Optimize Product Mix",
      description: "Focus on promoting high-margin products while reevaluating low-margin offerings.",
      icon: <ShoppingBasket className="h-5 w-5 text-blue-500" />,
      type: "info"
    },
    {
      title: "Customer Diversification",
      description: "Reduce dependency risk by expanding your customer base beyond current top accounts.",
      icon: <CircleAlert className="h-5 w-5 text-blue-500" />,
      type: "info"
    }
  ]
  
  // Add seasonal recommendations if we have revenue data
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
    
    if (maxRevenueMonth.month !== minRevenueMonth.month) {
      insights.push({
        title: "Seasonal Strategy",
        description: `Plan inventory and promotions around your peak month (${maxRevenueMonth.month}) and develop strategies to boost sales during slower months like ${minRevenueMonth.month}.`,
        icon: <BarChart4 className="h-5 w-5 text-purple-500" />,
        type: "info"
      })
    }
  }
  
  return insights
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
        <h1 className="text-3xl font-bold tracking-tight">AI Insights</h1>
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
                  <CardTitle className="text-lg">{insight.title}</CardTitle>
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
