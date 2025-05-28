"use client"

export const dynamic = 'force-dynamic'; // Force page to be dynamically rendered, no caching

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import { BarChart, LineChart, CartesianGrid, XAxis, YAxis, Legend, Bar, Line, ResponsiveContainer, Tooltip, Cell } from "recharts"
import { ArrowUpRight, DollarSign, ShoppingCart, TrendingUp, AlertCircle, FileText, RefreshCw, ListFilter, X, CalendarIcon, Filter } from "lucide-react"
import { checkApiHealth, getDashboardData, getDataFiles, selectDataFile, reloadDataFiles } from "@/lib/api"
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { useToast } from "@/components/ui/use-toast"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { useRouter } from "next/navigation"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { 
  Popover,
  PopoverContent,
  PopoverTrigger 
} from "@/components/ui/popover"
import { Calendar } from "@/components/ui/calendar"
import { format } from "date-fns"
import { Input } from "@/components/ui/input"

// Data File Indicator Component
const DataFileIndicator = ({ onReload }: { onReload: () => void }) => {
  const { toast } = useToast()
  const [dataFiles, setDataFiles] = useState<string[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState("")

  useEffect(() => {
    fetchDataFiles()
  }, [])

  const fetchDataFiles = async () => {
    try {
      const data = await getDataFiles()
      setDataFiles(data.files || [])
    } catch (err) {
      setError("Failed to load data files")
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
        description: `Using combined data from ${dataFiles.length} files.`,
      })
      onReload()
    } catch (err) {
      setError("Failed to reload data files")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="mb-6 flex items-center space-x-4">
      <div className="flex items-center">
        <FileText className="h-5 w-5 mr-2 text-muted-foreground" />
        <span className="text-sm font-medium">Data source:</span>
      </div>
      <Badge variant="outline" className="font-mono">
        Using combined data from {dataFiles.length} file{dataFiles.length !== 1 ? 's' : ''}
      </Badge>
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

interface Product {
  id: number;
  name: string;
  rank?: string;
  profit: number;
  revenue: number;
}

export default function DashboardPage() {
  // Add the router for refresh capability
  const router = useRouter();
  // State for API status
  const [apiStatus, setApiStatus] = useState("loading")
  // State for loading indicators
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState("")
  
  // State for dashboard data
  const [revenueData, setRevenueData] = useState<any[]>([])
  const [productRevenueData, setProductRevenueData] = useState<any[]>([])
  const [locationRevenueData, setLocationRevenueData] = useState<any[]>([])
  const [topProductsData, setTopProductsData] = useState<Product[]>([])
  const [allProductsData, setAllProductsData] = useState<Product[]>([])
  const [showAllProductsModal, setShowAllProductsModal] = useState(false)
  const [totalPredictedRevenue, setTotalPredictedRevenue] = useState(0)
  const [totalSales, setTotalSales] = useState(0)
  const [averageRevenuePerSale, setAverageRevenuePerSale] = useState(0)
  const [showProfit, setShowProfit] = useState(false)
  const [showFilters, setShowFilters] = useState(false)
  const [dateRange, setDateRange] = useState<{from: Date | undefined, to: Date | undefined}>({
    from: undefined,
    to: undefined
  })
  const [productFilter, setProductFilter] = useState("all")
  const [locationFilter, setLocationFilter] = useState("all")
  const [filteredRevenueData, setFilteredRevenueData] = useState<any[]>([])

  const NUM_TOP_PRODUCTS = 10; // Show top 10 products
  
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
    fetchDashboardData();
    checkApi();
    
    // Listen for data file changes from other parts of the app
    const handleDataFileChanged = (event: Event) => {
      console.log("Data file changed event received");
      // Force refresh data when file changes
      handleDataFileChange();
    };
    
    // Add event listener for data file changes
    window.addEventListener('dataFileChanged', handleDataFileChanged);
    
    // Clean up event listener when component unmounts
    return () => {
      window.removeEventListener('dataFileChanged', handleDataFileChanged);
    };
  }, [])

  // Handle data file change
  const handleDataFileChange = () => {
    // Force a full refresh of the router to clear any client-side caching
    router.refresh();
    fetchDashboardData();
  }

  // Add function to trigger manual refresh
  const handleRefresh = () => {
    router.refresh();
    fetchDashboardData();
  }
  
  // Define a function to process product data
  const processProductData = (data: any) => {
    if (!data?.top_products_data || !Array.isArray(data.top_products_data)) {
      console.warn("Missing or invalid product data");
      return { topProducts: [], allProducts: [] };
    }

    // Get all products and sort by profit
    const allProducts = [...data.top_products_data];
    const sortedAllProducts = [...allProducts].sort((a, b) => b.profit - a.profit);
    
    // Get top 10 products by profit
    const top10Products = sortedAllProducts.slice(0, NUM_TOP_PRODUCTS);
    
    console.log(`Displaying ${top10Products.length} top products out of ${sortedAllProducts.length} total products`);
    
    return { 
      topProducts: top10Products,
      allProducts: sortedAllProducts
    };
  };
  
  // Add a function to apply filters
  const applyFilters = () => {
    let filtered = [...revenueData];
    
    // Apply date range filter if dates are selected
    if (dateRange.from && dateRange.to) {
      const fromDate = new Date(dateRange.from);
      const toDate = new Date(dateRange.to);
      
      filtered = filtered.filter(item => {
        // Assuming month format is like "Jan 2023"
        if (!item.month) return true;
        
        const parts = item.month.split(' ');
        if (parts.length !== 2) return true;
        
        const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
        const monthIndex = monthNames.indexOf(parts[0]);
        if (monthIndex === -1) return true;
        
        const year = parseInt(parts[1]);
        const itemDate = new Date(year, monthIndex, 1);
        
        return itemDate >= fromDate && itemDate <= toDate;
      });
    }
    
    // Apply product filter if specified
    if (productFilter && productFilter !== "all") {
      // This would require product-specific revenue data
      // For now, we'll just log that this filter was applied
      console.log("Product filter applied:", productFilter);
    }
    
    // Apply location filter if specified
    if (locationFilter && locationFilter !== "all") {
      // This would require location-specific revenue data
      // For now, we'll just log that this filter was applied
      console.log("Location filter applied:", locationFilter);
    }
    
    setFilteredRevenueData(filtered);
  };
  
  // Call applyFilters whenever filter values change
  useEffect(() => {
    applyFilters();
  }, [revenueData, dateRange, productFilter, locationFilter]);
  
  const fetchDashboardData = async () => {
    setIsLoading(true);
    setError("");
    
    try {
      // Add cache busting parameter
      const timestamp = new Date().getTime();
      const data = await getDashboardData(`?_=${timestamp}`);
      
      console.log("Dashboard data received:", data);
      
      // Process product data
      const { topProducts, allProducts } = processProductData(data);
      
      // Store processed data
      setTopProductsData(topProducts);
      setAllProductsData(allProducts);
      
      // Check if profit data exists in the response
      const hasProfitData = data.revenue_data && 
                           data.revenue_data.length > 0 && 
                           'profit' in data.revenue_data[0];
                           
      console.log("Has profit data:", hasProfitData);
      
      // If profit data is missing, add it as a calculated field (40% of revenue)
      interface RevenueDataItem {
        month: string;
        revenue: number;
        profit?: number;
      }
      
      const enhancedRevenueData = data.revenue_data?.map((item: RevenueDataItem) => ({
        ...item,
        profit: item.profit || Math.round(item.revenue * 0.4)
      })) || [];
      
      setRevenueData(enhancedRevenueData);
      setFilteredRevenueData(enhancedRevenueData); // Initialize filtered data
      setProductRevenueData(data.product_revenue_data || []);
      
      // Update to use location_revenue_data instead of customer_revenue_data
      setLocationRevenueData(data.location_revenue_data || []);
      
      // Log the location data for debugging
      console.log("Location data:", data.location_revenue_data);
      
      setTotalPredictedRevenue(data.total_revenue || 0);
      setTotalSales(data.total_sales || 0);
      setAverageRevenuePerSale(data.avg_revenue_per_sale || 0);
    } catch (err) {
      console.error("Error fetching dashboard data:", err);
      setError("Failed to load dashboard data. Please try again later.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container py-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <Button 
          variant="outline" 
          onClick={handleRefresh} 
          disabled={isLoading}
          className="flex items-center gap-2"
        >
          <RefreshCw className="h-4 w-4" />
          Refresh Data
        </Button>
      </div>

      <DataFileIndicator onReload={handleDataFileChange} />
      
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
          <TabsTrigger value="locations">Revenue by Location</TabsTrigger>
          <TabsTrigger value="profitable">Profitable Products</TabsTrigger>
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
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setShowFilters(!showFilters)}
                    className="flex items-center gap-1"
                  >
                    <Filter className="h-4 w-4" />
                    {showFilters ? "Hide Filters" : "Show Filters"}
                  </Button>
                  <Switch 
                    id="show-profit" 
                    checked={showProfit}
                    onCheckedChange={setShowProfit}
                    className="data-[state=checked]:bg-green-500"
                  />
                  <Label htmlFor="show-profit">Show Profit</Label>
                </div>
              </div>
              
              {showFilters && (
                <div className="mt-4 p-4 border rounded-md bg-muted/20">
                  <div className="text-sm font-medium mb-2">Filter Options</div>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <Label htmlFor="date-range" className="text-xs">Date Range</Label>
                      <div className="flex space-x-2 mt-1">
                        <Popover>
                          <PopoverTrigger asChild>
                            <Button
                              id="date-from"
                              variant="outline"
                              size="sm"
                              className="w-full justify-start text-left font-normal"
                            >
                              <CalendarIcon className="mr-2 h-4 w-4" />
                              {dateRange.from ? (
                                format(dateRange.from, "MMM yyyy")
                              ) : (
                                <span>Start date</span>
                              )}
                            </Button>
                          </PopoverTrigger>
                          <PopoverContent className="w-auto p-0" align="start">
                            <Calendar
                              mode="single"
                              selected={dateRange.from}
                              onSelect={(date) => 
                                setDateRange({ ...dateRange, from: date })
                              }
                              initialFocus
                            />
                          </PopoverContent>
                        </Popover>
                        
                        <Popover>
                          <PopoverTrigger asChild>
                            <Button
                              id="date-to"
                              variant="outline"
                              size="sm"
                              className="w-full justify-start text-left font-normal"
                            >
                              <CalendarIcon className="mr-2 h-4 w-4" />
                              {dateRange.to ? (
                                format(dateRange.to, "MMM yyyy")
                              ) : (
                                <span>End date</span>
                              )}
                            </Button>
                          </PopoverTrigger>
                          <PopoverContent className="w-auto p-0" align="start">
                            <Calendar
                              mode="single"
                              selected={dateRange.to}
                              onSelect={(date) => 
                                setDateRange({ ...dateRange, to: date })
                              }
                              initialFocus
                            />
                          </PopoverContent>
                        </Popover>
                      </div>
                    </div>
                    
                    <div>
                      <Label htmlFor="product-filter" className="text-xs">Product</Label>
                      <Select 
                        value={productFilter} 
                        onValueChange={setProductFilter}
                      >
                        <SelectTrigger id="product-filter" className="mt-1">
                          <SelectValue placeholder="All Products" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="all">All Products</SelectItem>
                          {allProductsData.slice(0, 10).map(product => (
                            <SelectItem key={product.id} value={product.name}>
                              {product.name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    
                    <div>
                      <Label htmlFor="location-filter" className="text-xs">Location</Label>
                      <Select 
                        value={locationFilter} 
                        onValueChange={setLocationFilter}
                      >
                        <SelectTrigger id="location-filter" className="mt-1">
                          <SelectValue placeholder="All Locations" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="all">All Locations</SelectItem>
                          {locationRevenueData.map(location => (
                            <SelectItem key={location.name} value={location.name}>
                              {location.name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  
                  <div className="flex justify-end mt-4">
                    <Button 
                      size="sm" 
                      variant="secondary"
                      className="mr-2"
                      onClick={() => {
                        setDateRange({ from: undefined, to: undefined });
                        setProductFilter("all");
                        setLocationFilter("all");
                      }}
                    >
                      Reset
                    </Button>
                    <Button 
                      size="sm"
                      onClick={applyFilters}
                    >
                      Apply Filters
                    </Button>
                  </div>
                </div>
              )}
            </CardHeader>
            <CardContent className="h-[600px]">
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
                    data={filteredRevenueData}
                    margin={{
                      top: 20,
                      right: 30,
                      left: 20,
                      bottom: 20,
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
                      stroke="blue"
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
              <div className="mt-2 flex items-center gap-4 text-xs">
                <div className="flex items-center gap-1.5">
                  <div className="h-3 w-3 rounded-sm" style={{ backgroundColor: "hsl(var(--chart-2))" }}></div>
                  <div className="h-3 w-3 rounded-sm ml-1" style={{ backgroundColor: "hsl(var(--chart-3))" }}></div>
                  <span>Revenue (alternating)</span>
                </div>
              </div>
            </CardHeader>
            <CardContent className="h-[600px]">
              <ChartContainer
                config={{
                  revenue: {
                    label: "Revenue",
                    color: "hsl(var(--chart-2))",
                  },
                  profit: {
                    label: "Profit",
                    color: "hsl(var(--chart-4))",
                  }
                }}
              >
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={productRevenueData}
                    margin={{
                      top: 20,
                      right: 30,
                      left: 20,
                      bottom: 20,
                    }}
                    barCategoryGap={4}
                    barGap={2}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis tickFormatter={(value) => `$${value.toLocaleString()}`} />
                    <ChartTooltip
                      content={<ChartTooltipContent formatter={(value) => `$${Number(value).toLocaleString()}`} />}
                    />
                    <Legend />
                    <Bar 
                      dataKey="revenue" 
                      name="Revenue"
                      barSize={20}
                      radius={[4, 4, 0, 0]}
                    >
                      {productRevenueData.map((entry, index) => (
                        <Cell 
                          key={`${entry.name}-${index}`}
                          fill={index % 2 === 0 ? "hsl(var(--chart-2))" : "hsl(var(--chart-3))"}
                        />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </ChartContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="locations">
          <Card>
            <CardHeader>
              <CardTitle>Revenue by Location</CardTitle>
              <CardDescription>Distribution of revenue across different locations</CardDescription>
              <div className="mt-2 flex items-center gap-4 text-xs">
                <div className="flex items-center gap-1.5">
                  <div className="h-3 w-3 rounded-sm" style={{ backgroundColor: "orange" }}></div>
                  <span>Revenue by Location</span>
                </div>
              </div>
            </CardHeader>
            <CardContent className="h-[600px]">
              <ChartContainer
                config={{
                  revenue: {
                    label: "Revenue",
                    color: "orange",
                  }
                }}
              >
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={locationRevenueData}
                    margin={{
                      top: 20,
                      right: 30,
                      left: 20,
                      bottom: 20,
                    }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis tickFormatter={(value) => `$${value.toLocaleString()}`} />
                    <ChartTooltip
                      content={<ChartTooltipContent formatter={(value) => `$${Number(value).toLocaleString()}`} />}
                    />
                    <Legend />
                    <Bar 
                      dataKey="revenue" 
                      name="Revenue"
                      barSize={25}
                      radius={[4, 4, 0, 0]}
                      fill="orange"
                    >
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </ChartContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="profitable">
          <Card>
            <CardHeader>
              <CardTitle>Profitable Products</CardTitle>
              <CardDescription>Top profitable products</CardDescription>
              <div className="flex justify-between mt-2">
                <div className="flex items-center gap-1.5 text-xs">
                  <div className="h-3 w-3 rounded-sm" style={{ backgroundColor: "green" }}></div>
                  <span>Profit</span>
                </div>
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={() => setShowAllProductsModal(true)}
                  className="text-xs"
                >
                  View All Products
                </Button>
              </div>
            </CardHeader>
            <CardContent className="h-[600px]">
              <ChartContainer
                config={{
                  profit: {
                    label: "Profit",
                    color: "green",
                  }
                }}
              >
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={topProductsData}
                    margin={{
                      top: 20,
                      right: 30,
                      left: 20,
                      bottom: 20,
                    }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis tickFormatter={(value) => `$${value.toLocaleString()}`} />
                    <ChartTooltip
                      content={<ChartTooltipContent formatter={(value) => `$${Number(value).toLocaleString()}`} />}
                    />
                    <Legend />
                    <Bar 
                      dataKey="profit" 
                      name="Profit"
                      barSize={25}
                      radius={[4, 4, 0, 0]}
                      fill="green"
                    >
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </ChartContainer>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
        </>
      )}
      
      {/* Add back the All Products Modal */}
      <Dialog open={showAllProductsModal} onOpenChange={setShowAllProductsModal}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>All Products</DialogTitle>
            <DialogDescription>Complete list of products ordered by profit</DialogDescription>
          </DialogHeader>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Rank</TableHead>
                <TableHead>Product</TableHead>
                <TableHead className="text-right">Revenue</TableHead>
                <TableHead className="text-right">Profit</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {allProductsData.map((product, index) => (
                <TableRow key={product.id || index}>
                  <TableCell>{index + 1}</TableCell>
                  <TableCell>{product.name}</TableCell>
                  <TableCell className="text-right">${product.revenue?.toLocaleString() || 0}</TableCell>
                  <TableCell className="text-right">${product.profit?.toLocaleString() || 0}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </DialogContent>
      </Dialog>
    </div>
  )
}