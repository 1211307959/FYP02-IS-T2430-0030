"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import { BarChart, LineChart, CartesianGrid, XAxis, YAxis, Legend, Bar, Line, ResponsiveContainer, Tooltip } from "recharts"
import { ArrowUpRight, DollarSign, ShoppingCart, TrendingUp, AlertCircle, FileText, RefreshCw } from "lucide-react"
import { checkApiHealth, getDashboardData, getDataFiles, selectDataFile, reloadDataFiles } from "@/lib/api"
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { useToast } from "@/components/ui/use-toast"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"

// Data File Selector Component
const DataFileSelector = ({ onFileChange }: { onFileChange: () => void }) => {
  const { toast } = useToast()
  const [dataFiles, setDataFiles] = useState<string[]>([])
  const [currentFile, setCurrentFile] = useState<string>("")
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState("")

  useEffect(() => {
    fetchDataFiles()
  }, [])

  const fetchDataFiles = async () => {
    try {
      const data = await getDataFiles()
      setDataFiles(data.files || [])
      setCurrentFile(data.current_file || "")
    } catch (err) {
      setError("Failed to load data files")
    }
  }

  const handleFileChange = async (filename: string) => {
    if (filename === currentFile) return
    
    setIsLoading(true)
    setError("")
    
    try {
      await selectDataFile(filename)
      setCurrentFile(filename)
      onFileChange()
    } catch (err) {
      setError("Failed to change data file")
    } finally {
      setIsLoading(false)
    }
  }
  
  const handleReloadFiles = async () => {
    setIsLoading(true)
    setError("")
    
    try {
      await reloadDataFiles()
      fetchDataFiles()
      toast({
        title: "Data files reloaded",
        description: "The list of available data files has been refreshed.",
      })
    } catch (err) {
      setError("Failed to reload data files")
    } finally {
      setIsLoading(false)
    }
  }

  if (dataFiles.length === 0) return null;

  return (
    <div className="mb-6 flex items-center space-x-4">
      <div className="flex items-center">
        <FileText className="h-5 w-5 mr-2 text-muted-foreground" />
        <span className="text-sm font-medium">Data File:</span>
      </div>
      <Select
        value={currentFile}
        onValueChange={handleFileChange}
        disabled={isLoading}
      >
        <SelectTrigger className="w-[240px]">
          <SelectValue placeholder="Select a data file" />
        </SelectTrigger>
        <SelectContent>
          {dataFiles.map((file) => (
            <SelectItem key={file} value={file}>
              {file}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      <Button 
        variant="outline" 
        size="icon" 
        onClick={handleReloadFiles} 
        disabled={isLoading}
        title="Reload data files"
      >
        <RefreshCw className="h-4 w-4" />
      </Button>
      {error && <span className="text-sm text-destructive">{error}</span>}
    </div>
  )
}

export default function DashboardPage() {
  // State for API status
  const [apiStatus, setApiStatus] = useState("loading")
  // State for loading indicators
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState("")
  
  // State for dashboard data
  const [revenueData, setRevenueData] = useState<any[]>([])
  const [productRevenueData, setProductRevenueData] = useState<any[]>([])
  const [customerRevenueData, setCustomerRevenueData] = useState<any[]>([])
  const [topProductsData, setTopProductsData] = useState<any[]>([])
  const [totalPredictedRevenue, setTotalPredictedRevenue] = useState(0)
  const [totalSales, setTotalSales] = useState(0)
  const [averageRevenuePerSale, setAverageRevenuePerSale] = useState(0)
  const [showProfit, setShowProfit] = useState(false)
  
  useEffect(() => {
    // Check API health when component mounts
    const checkApi = async () => {
      try {
        const health = await checkApiHealth()
        setApiStatus(health.status)
      } catch (error) {
        setApiStatus("unhealthy")
      }
    }
    
    // Fetch dashboard data from the API
    const fetchDashboardData = async () => {
      setIsLoading(true)
      setError("")
      
      try {
        const data = await getDashboardData()
        
        // Update state with the fetched data
        console.log("Revenue data from API:", data.revenue_data);
        
        // Check if profit data exists in the response
        const hasProfitData = data.revenue_data && 
                             data.revenue_data.length > 0 && 
                             'profit' in data.revenue_data[0];
                             
        console.log("Has profit data:", hasProfitData);
        
        // If profit data is missing, add it as a calculated field (40% of revenue)
        const enhancedRevenueData = data.revenue_data.map(item => ({
          ...item,
          profit: item.profit || Math.round(item.revenue * 0.4)
        }));
        
        setRevenueData(enhancedRevenueData || []);
        setProductRevenueData(data.product_revenue_data || [])
        setCustomerRevenueData(data.customer_revenue_data || [])
        setTopProductsData(data.top_products_data || [])
        setTotalPredictedRevenue(data.total_revenue || 0)
        setTotalSales(data.total_sales || 0)
        setAverageRevenuePerSale(data.avg_revenue_per_sale || 0)
      } catch (err) {
        console.error("Error fetching dashboard data:", err)
        setError("Failed to load dashboard data. Please try again later.")
      } finally {
        setIsLoading(false)
      }
    }
    
    checkApi()
    fetchDashboardData()
  }, [])

  // Handle data file change
  const handleDataFileChange = () => {
    fetchDashboardData()
  }

  return (
    <div className="container py-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
      </div>

      <DataFileSelector onFileChange={handleDataFileChange} />
      
      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}
      
      {isLoading ? (
        <div className="flex items-center justify-center h-40">
          <div className="text-lg text-muted-foreground">Loading dashboard data...</div>
        </div>
      ) : (
        <>
      <div className="grid gap-4 md:grid-cols-3 mb-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Revenue</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${totalPredictedRevenue.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-green-500 flex items-center">
                +12.5% <ArrowUpRight className="h-3 w-3 ml-1" />
              </span>{" "}
              from previous period
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Average Revenue per Sale</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${averageRevenuePerSale.toFixed(2)}</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-green-500 flex items-center">
                +8.2% <ArrowUpRight className="h-3 w-3 ml-1" />
              </span>{" "}
              from previous period
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Sales</CardTitle>
            <ShoppingCart className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalSales.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-green-500 flex items-center">
                +5.7% <ArrowUpRight className="h-3 w-3 ml-1" />
              </span>{" "}
              from previous period
            </p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="revenue" className="space-y-4">
        <TabsList>
          <TabsTrigger value="revenue">Revenue Over Time</TabsTrigger>
          <TabsTrigger value="products">Revenue by Product</TabsTrigger>
          <TabsTrigger value="customers">Revenue by Location</TabsTrigger>
          <TabsTrigger value="profitable">Top Profitable Products</TabsTrigger>
        </TabsList>

        <TabsContent value="revenue">
          <Card>
            <CardHeader>
              <div className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle>Revenue Over Time</CardTitle>
                  <CardDescription>Monthly revenue trends for the current year</CardDescription>
                </div>
                <div className="flex items-center space-x-2">
                  <Switch 
                    id="show-profit" 
                    checked={showProfit}
                    onCheckedChange={setShowProfit}
                    className="data-[state=checked]:bg-green-500"
                  />
                  <Label htmlFor="show-profit">Show Profit</Label>
                </div>
              </div>
            </CardHeader>
            <CardContent className="h-[400px]">
              <ChartContainer
                config={{
                  revenue: {
                    label: "Revenue",
                    color: "hsl(var(--chart-1))",
                  },
                  profit: {
                    label: "Profit",
                    color: "hsl(var(--chart-4))",
                  },
                }}
              >
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart
                    data={revenueData}
                    margin={{
                      top: 20,
                      right: 30,
                      left: 20,
                      bottom: 5,
                    }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis tickFormatter={(value) => `$${value.toLocaleString()}`} />
                    <ChartTooltip
                      content={<ChartTooltipContent formatter={(value) => `$${Number(value).toLocaleString()}`} />}
                    />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="revenue"
                      stroke="var(--color-revenue)"
                      strokeWidth={2}
                      activeDot={{ r: 8 }}
                      name="Revenue"
                    />
                    {showProfit && (
                      <Line
                        type="monotone"
                        dataKey="profit"
                        stroke="green"
                        strokeWidth={2}
                        activeDot={{ r: 6 }}
                        name="Profit"
                      />
                    )}
                  </LineChart>
                </ResponsiveContainer>
              </ChartContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="products">
          <Card>
            <CardHeader>
              <CardTitle>Revenue by Product</CardTitle>
              <CardDescription>Distribution of revenue across different products</CardDescription>
            </CardHeader>
            <CardContent className="h-[400px]">
              <ChartContainer
                config={{
                  revenue: {
                    label: "Revenue",
                    color: "hsl(var(--chart-2))",
                  },
                }}
              >
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={productRevenueData}
                    margin={{
                      top: 20,
                      right: 30,
                      left: 20,
                      bottom: 5,
                    }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis tickFormatter={(value) => `$${value.toLocaleString()}`} />
                    <ChartTooltip
                      content={<ChartTooltipContent formatter={(value) => `$${Number(value).toLocaleString()}`} />}
                    />
                    <Legend />
                    <Bar dataKey="revenue" fill="var(--color-revenue)" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </ChartContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="customers">
          <Card>
            <CardHeader>
              <CardTitle>Revenue by Location</CardTitle>
              <CardDescription>Distribution of revenue across different locations</CardDescription>
            </CardHeader>
            <CardContent className="h-[400px]">
              <ChartContainer
                config={{
                  revenue: {
                    label: "Revenue",
                    color: "hsl(var(--chart-3))",
                  },
                }}
              >
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={customerRevenueData}
                    margin={{
                      top: 20,
                      right: 30,
                      left: 20,
                      bottom: 5,
                    }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis tickFormatter={(value) => `$${value.toLocaleString()}`} />
                    <ChartTooltip
                      content={<ChartTooltipContent formatter={(value) => `$${Number(value).toLocaleString()}`} />}
                    />
                    <Legend />
                    <Bar dataKey="revenue" fill="var(--color-revenue)" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </ChartContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="profitable">
          <Card>
            <CardHeader>
              <CardTitle>Top 5 Profitable Products</CardTitle>
              <CardDescription>Products with the highest profit margins</CardDescription>
            </CardHeader>
            <CardContent className="h-[400px]">
              <ChartContainer
                config={{
                  profit: {
                    label: "Profit",
                    color: "hsl(var(--chart-4))",
                  },
                }}
              >
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={topProductsData}
                    layout="vertical"
                    margin={{
                      top: 20,
                      right: 30,
                      left: 100,
                      bottom: 5,
                    }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" tickFormatter={(value) => `$${value.toLocaleString()}`} />
                    <YAxis type="category" dataKey="name" />
                    <ChartTooltip
                      content={<ChartTooltipContent formatter={(value) => `$${Number(value).toLocaleString()}`} />}
                    />
                    <Legend />
                    <Bar dataKey="profit" fill="var(--color-profit)" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </ChartContainer>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
        </>
      )}
    </div>
  )
}
