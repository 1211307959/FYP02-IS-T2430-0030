"use client"

import { useState, useEffect, useRef, useCallback } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Label } from "@/components/ui/label"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { FileText, Calendar, TrendingUp, LineChart, BarChart, RefreshCw, RotateCcw } from "lucide-react"
import { useToast } from "@/components/ui/use-toast"
import { Input } from "@/components/ui/input"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { 
  getProducts, 
  getProductData, 
  getLocations,
  fetchForecastSales,
  fetchProductTrend,
  fetchMultipleForecast,
  formatDate,
  getDefaultDateRange
} from "@/lib/api"
import {
  LineChart as RechartsLineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart as RechartsBarChart,
  Bar,
  Area,
  AreaChart as RechartsAreaChart
} from "recharts"

interface Product {
  id: string | number;
  name: string;
}

interface ProductData {
  id: string | number;
  averagePrice: number;
  averageCost: number;
}

interface Location {
  id: string;
  name: string;
}

interface ChartDataItem {
  date: string;
  weekday: string;
  revenue: number;
  quantity: number;
  profit: number;
  revenueLower?: number;
  revenueUpper?: number;
  quantityLower?: number;
  quantityUpper?: number;
  profitLower?: number;
  profitUpper?: number;
  seasonalTrend?: number;
  displayDate?: string; // Formatted date based on frequency
}

interface ForecastItem {
  date: string;
  weekday: string;
  revenue: any;
  quantity: any;
  profit: any;
}

interface ForecastResult {
  status: string;
  forecast: Array<ForecastItem>;
  summary: {
    total_revenue: number;
    total_quantity: number;
    total_profit: number;
    average_revenue_per_period: number;
    average_quantity_per_period: number;
    average_profit_per_period: number;
    total_periods: number;
  };
  note?: string;
}

interface TrendResult {
  status: string;
  price_variations: Array<{
    price_factor: number;
    unit_price: number;
    summary: {
      total_revenue: number;
      total_quantity: number;
      total_profit: number;
    };
  }>;
}

interface ProductForecast {
  product_id: string;
  location: string;
  forecast: ForecastItem[];
  summary: {
    total_revenue: number;
    total_quantity: number;
    total_profit: number;
    total_periods: number;
    average_revenue_per_period: number;
    average_quantity_per_period: number;
    average_profit_per_period: number;
  };
}

interface MultipleForecasts {
  status: string;
  forecasts: ProductForecast[];
  metadata: {
    start_date: string;
    end_date: string;
    frequency: string;
    products_count: number;
  };
  message?: string;
}

export default function SalesForecastingPage() {
  const { toast } = useToast()
  const [activeTab, setActiveTab] = useState("auto")
  const [products, setProducts] = useState<Product[]>([])
  const [productData, setProductData] = useState<ProductData[]>([])
  const [locations, setLocations] = useState<Location[]>([])
  const [loading, setLoading] = useState(false)
  const [forecastResult, setForecastResult] = useState<ForecastResult | null>(null)
  const [trendResult, setTrendResult] = useState<TrendResult | null>(null)
  const [isLoadingOptions, setIsLoadingOptions] = useState(true)
  const [productAverages, setProductAverages] = useState<Record<string, {price: number, cost: number}>>({})
  
  // Add refs to track API request status and prevent duplicate calls
  const mounted = useRef(false);
  const productDataLoadedRef = useRef(false);
  const requestInProgressRef = useRef(false);
  const lastRequestTimeRef = useRef(0);
  
  // Form state
  const [selectedProduct, setSelectedProduct] = useState<string>("")
  const [selectedLocation, setSelectedLocation] = useState<string>("")
  const { startDate, endDate } = getDefaultDateRange(365) // Default to one year
  const [forecastStartDate, setForecastStartDate] = useState<string>(startDate)
  const [forecastEndDate, setForecastEndDate] = useState<string>(endDate)
  const [frequency, setFrequency] = useState<"D" | "W" | "M">("M") // Default to Monthly for better visualization
  
  // Automatic forecast uses monthly frequency and one year to show meaningful variations
  const getAutomaticForecastSettings = () => {
    const { startDate: autoStart, endDate: autoEnd } = getDefaultDateRange(365) // One year
    return {
      startDate: autoStart,
      endDate: autoEnd,
      frequency: 'M' as const // Monthly frequency for automatic forecast
    }
  }
  const [metricView, setMetricView] = useState<"revenue" | "quantity" | "profit" | "all" | "none">("revenue")
  // Removed confidence intervals and seasonality trend toggles
  const [showRevenue, setShowRevenue] = useState<boolean>(true)
  const [showProfit, setShowProfit] = useState<boolean>(true)
  // Custom forecast metric toggles - allow multiple metrics simultaneously
  const [showCustomRevenue, setShowCustomRevenue] = useState<boolean>(true)
  const [showCustomProfit, setShowCustomProfit] = useState<boolean>(true)
  const [showCustomQuantity, setShowCustomQuantity] = useState<boolean>(true)
  const [allProductsForecast, setAllProductsForecast] = useState<ForecastResult | null>(null)
  
  // Load product price and cost data
  const loadProductData = async (): Promise<Record<string, { price: number, cost: number }>> => {
    try {
      // If we've already loaded product data and aren't explicitly reloading, return existing data
      if (productDataLoadedRef.current && Object.keys(productAverages).length > 0) {
        console.log("Using cached product data:", Object.keys(productAverages).length, "products");
        return productAverages;
      }
      
      console.log("Loading fresh product data...");
      const response = await getProductData();
      
      // Create a map from product IDs to their price and cost data
      const productMap: Record<string, {price: number, cost: number}> = {};
      
      if (response && response.products && Array.isArray(response.products)) {
        response.products.forEach((product: { productId: string | number, price: number, cost: number }) => {
          // Use the productId directly as the key (as a string)
          productMap[product.productId.toString()] = {
            price: Math.round(product.price * 100) / 100,
            cost: Math.round(product.cost * 100) / 100
          };
        });
        
        // Update the product averages state
        setProductAverages(productMap);
        
        // Convert to array format for the component state
        const productDataArray = Object.entries(productMap).map(([id, data]) => ({
          id,
          averagePrice: data.price,
          averageCost: data.cost
        }));
        
        setProductData(productDataArray);
        
        // Mark as loaded
        productDataLoadedRef.current = true;
        
        console.log(`Successfully loaded ${productDataArray.length} products with price data`);
        return productMap;
      } else {
        console.error("Invalid response format from getProductData:", response);
        throw new Error("Invalid product data response format");
      }
      
    } catch (err) {
      console.error("Error loading product data:", err);
      
      toast({
        variant: "destructive",
        title: "Error loading product data",
        description: "Failed to load product price and cost data.",
      });
      
      throw err; // Re-throw to allow caller to handle
    }
  };
  
  // Reload product data function
  const reloadProductData = async () => {
    // Reset the cache flag to force a reload
    productDataLoadedRef.current = false;
    
    await loadProductData();
    toast({
      title: "Data refreshed",
      description: "Product data has been refreshed",
    });
  };
  
  // Generate all products forecast with debouncing
  const generateAllProductsForecast = async () => {
    // Prevent concurrent requests
    if (requestInProgressRef.current) {
      console.log("Request already in progress, skipping duplicate call");
      throw new Error("Request already in progress");
    }
    
    // Debounce API calls
    const now = Date.now();
    if (now - lastRequestTimeRef.current < 2000) {
      console.log("Debouncing forecast request - too soon after last request");
      throw new Error("Request debounced - too soon after last request");
    }
    
    // Set flags to prevent duplicate calls
    requestInProgressRef.current = true;
    lastRequestTimeRef.current = now;
    
    try {
      if (products.length === 0 || locations.length === 0) {
        console.error("Products or locations not loaded:", { productsCount: products.length, locationsCount: locations.length });
        throw new Error("Products or locations not loaded yet");
      }

      if (!productAverages || Object.keys(productAverages).length === 0) {
        console.error("Product averages not loaded:", { productAveragesKeys: Object.keys(productAverages || {}).length });
        throw new Error("Product price data not loaded yet");
      }

      // Create a list of all products with their default location and price
      // Sort products by price to ensure we get diverse price ranges
      const productList = products
        .map(product => {
          const id = product.id.toString();
          const price = productAverages[id]?.price;
          const cost = productAverages[id]?.cost;
          
          // Skip products without price data from CSV
          if (!price || !cost) {
            console.warn(`Product ${id} missing price/cost data, skipping`);
            return null;
          }
          
          return {
            product_id: id,
            location: 'All',
            unit_price: price,
            unit_cost: cost,
            price_category: price < 3000 ? 'low' : price < 8000 ? 'medium' : 'high'
          };
        })
        .filter(product => product !== null) // Remove products without price data
        .sort((a, b) => a.unit_price - b.unit_price); // Sort by price for diversity
      
      console.log("Products with price diversity:", productList.map(p => 
        `Product ${p.product_id}: $${p.unit_price} (${p.price_category})`
      ));
      
      // Use all products for automatic forecast
      const productsToUse = productList.map(({ price_category, ...product }) => product);
      
      console.log("Sending automatic forecast request with products:", productsToUse.length, "products");
      
      // Use automatic forecast settings for better visualization
      const autoSettings = getAutomaticForecastSettings();
      console.log("Using automatic forecast settings:", autoSettings);
      const result = await fetchMultipleForecast(
        productsToUse,
        autoSettings.startDate,
        autoSettings.endDate,
        autoSettings.frequency
      );
      
      if (!result) {
        throw new Error("No result returned from forecast API");
      }
      
      console.log("Received forecast result:", result);
      console.log("Result metadata:", result.metadata);
      
      // Validate the result structure
      if (!result || typeof result !== 'object') {
        console.error("Invalid forecast result:", result);
        throw new Error("Invalid forecast result format");
      }
      
      // Check for error response
      if ('error' in result) {
        throw new Error(result.error);
      }
      
      // Handle both formats: direct success property or status property
      const isSuccess = result.success === true || result.status === "success";
      
      if (isSuccess) {
        console.log("Number of forecasts received:", result.forecasts ? result.forecasts.length : 0);
        
        // Use the aggregated forecast if available, otherwise sum individual forecasts
        let finalForecast;
        let totalRevenue = 0;
        let totalQuantity = 0;
        let totalProfit = 0;
        
        if (result.aggregated_forecast && Array.isArray(result.aggregated_forecast)) {
          // Use pre-aggregated data from backend
          console.log("Using pre-aggregated forecast data");
          finalForecast = result.aggregated_forecast;
          
          // Calculate totals from summary if available
          if (result.summary) {
            totalRevenue = result.summary.total_revenue || 0;
            totalQuantity = result.summary.total_quantity || 0;
            totalProfit = result.summary.total_profit || 0;
          } else {
            // Calculate from daily data
            totalRevenue = finalForecast.reduce((sum: number, item: any) => sum + (item.revenue || 0), 0);
            totalQuantity = finalForecast.reduce((sum: number, item: any) => sum + (item.quantity || 0), 0);
            totalProfit = finalForecast.reduce((sum: number, item: any) => sum + (item.profit || 0), 0);
          }
        } else if (result.forecasts && Array.isArray(result.forecasts)) {
          // Sum individual product forecasts manually
          console.log("Manually aggregating individual product forecasts");
          const dateMap = new Map();
          
          result.forecasts.forEach((productForecast: ProductForecast, index: number) => {
            console.log(`Processing product ${productForecast.product_id}: ${productForecast.summary?.total_revenue || 0} revenue`);
            
            if (productForecast.forecast && Array.isArray(productForecast.forecast)) {
              productForecast.forecast.forEach((dailyForecast: ForecastItem) => {
                const date = dailyForecast.date;
                
                if (!dateMap.has(date)) {
                  dateMap.set(date, {
                    date,
                    weekday: dailyForecast.weekday,
                    revenue: 0,
                    quantity: 0,
                    profit: 0
                  });
                }
                
                const entry = dateMap.get(date);
                
                // Extract values, handling both object and scalar formats
                const revenue = typeof dailyForecast.revenue === 'object' 
                  ? (dailyForecast.revenue?.prediction || 0) 
                  : (parseFloat(dailyForecast.revenue as any) || 0);
                  
                const quantity = typeof dailyForecast.quantity === 'object' 
                  ? (dailyForecast.quantity?.prediction || 0) 
                  : (parseFloat(dailyForecast.quantity as any) || 0);
                  
                const profit = typeof dailyForecast.profit === 'object' 
                  ? (dailyForecast.profit?.prediction || 0) 
                  : (parseFloat(dailyForecast.profit as any) || 0);
                
                entry.revenue += revenue;
                entry.quantity += quantity;
                entry.profit += profit;
              });
            }
            
            // Add to totals from summary if available
            if (productForecast.summary) {
              totalRevenue += productForecast.summary.total_revenue || 0;
              totalQuantity += productForecast.summary.total_quantity || 0;
              totalProfit += productForecast.summary.total_profit || 0;
            }
          });
          
          // Convert the date map to an array and sort by date
          finalForecast = Array.from(dateMap.values()).sort((a, b) => 
            new Date(a.date).getTime() - new Date(b.date).getTime()
          );
        } else {
          throw new Error("No valid forecast data received from API");
        }
        
        console.log("Aggregated totals:", { totalRevenue, totalQuantity, totalProfit });
        console.log("Final forecast periods:", finalForecast.length);
        
        // Create a summary
        const summary = {
          total_revenue: totalRevenue,
          total_quantity: totalQuantity,
          total_profit: totalProfit,
          total_periods: finalForecast.length,
          average_revenue_per_period: finalForecast.length ? totalRevenue / finalForecast.length : 0,
          average_quantity_per_period: finalForecast.length ? totalQuantity / finalForecast.length : 0,
          average_profit_per_period: finalForecast.length ? totalProfit / finalForecast.length : 0
        };
        
        // Create a unified forecast result
        const unifiedResult = {
          status: "success",
          forecast: finalForecast,
          summary,
          metadata: {
            products_count: result.forecasts ? result.forecasts.length : productsToUse.length,
            start_date: autoSettings.startDate,
            end_date: autoSettings.endDate,
            frequency: autoSettings.frequency,
            note: `Aggregated ML forecast across ${result.forecasts ? result.forecasts.length : productsToUse.length} products (SUM of all products)`
          }
        };
        
        console.log("Final unified result summary:", unifiedResult.summary);
        
        // Ensure we're providing properly structured data for the charts
        if (unifiedResult.forecast && Array.isArray(unifiedResult.forecast)) {
          unifiedResult.forecast = unifiedResult.forecast.map((item: any) => {
            // Ensure we have properly structured data for charting
            if (typeof item.quantity !== 'object') {
              item.quantity = {
                prediction: item.quantity,
                lower_bound: Math.max(0, item.quantity * 0.85),
                upper_bound: item.quantity * 1.15
              };
            }
            
            if (typeof item.revenue !== 'object') {
              item.revenue = {
                prediction: item.revenue,
                lower_bound: Math.max(0, item.revenue * 0.85),
                upper_bound: item.revenue * 1.15
              };
            }
            
            if (typeof item.profit !== 'object') {
              item.profit = {
                prediction: item.profit,
                lower_bound: Math.max(0, item.profit * 0.85),
                upper_bound: item.profit * 1.15
              };
            }
            
            return item;
          });
        }
        
        setAllProductsForecast(unifiedResult);
        return unifiedResult;
      } else {
        console.error("Forecast API returned error status:", result);
        throw new Error(result.message || result.error || "Failed to generate forecast for all products");
      }
    } catch (error) {
      console.error("Error generating all products forecast:", error);
      throw error; // Re-throw so the calling function can handle it
    } finally {
      requestInProgressRef.current = false;
    }
  };
  
  // Update the useEffect for initialization
  useEffect(() => {
    // Only run this effect on the initial mount
    const initialMount = { current: true };
    
    const loadInitialData = async () => {
      if (!initialMount.current) return;
      
      console.log("Starting loadInitialData...");
      
      try {
        setIsLoadingOptions(true);
        
        // Load product data first and wait for it to complete
        console.log("Loading product data...");
        const productAveragesData = await loadProductData();
        console.log("Product data loaded successfully:", Object.keys(productAveragesData).length, "products");
        
        // Load products and locations
        console.log("Getting products...");
        const productsData = await getProducts();
        let mappedProducts: Product[] = [];
        
        if (productsData && Array.isArray(productsData)) {
          mappedProducts = productsData.map((product: any) => ({
            id: product.id || product.toString(),
            name: product.name || `Product ${product}`
          }));
        }
        
        console.log("Getting locations data...");
        const locationsData = await getLocations();
        let mappedLocations: Location[] = [];
        
        if (locationsData && Array.isArray(locationsData)) {
          mappedLocations = locationsData.map((location: any) => ({
            id: typeof location === 'string' ? location : location.id,
            name: typeof location === 'string' ? location : location.name
          }));
        }
        
        // Set default values
        if (mappedProducts.length > 0 && mappedLocations.length > 0) {
          console.log("Setting default product and location from loaded data");
          
          const defaultLocation = mappedLocations[0].id;
          const defaultProduct = mappedProducts[0].id.toString();
          
          setSelectedProduct(defaultProduct);
          setSelectedLocation(defaultLocation);
        }
        
        // Update state variables
        setProducts(mappedProducts);
        setLocations(mappedLocations);
        setIsLoadingOptions(false);

        console.log("State updated - products:", mappedProducts.length, "locations:", mappedLocations.length);

        // Generate initial forecast if we have all required data
        if (mappedProducts.length > 0 && mappedLocations.length > 0 && Object.keys(productAveragesData).length > 0) {
          console.log("Generating initial forecast...");
          console.log("Products count:", mappedProducts.length);
          console.log("Locations count:", mappedLocations.length);
          console.log("Product averages count:", Object.keys(productAveragesData).length);
          
          try {
            // Use the loaded product averages data directly for forecast generation
            const productList = mappedProducts
              .map(product => {
                const id = product.id.toString();
                const price = productAveragesData[id]?.price;
                const cost = productAveragesData[id]?.cost;
                
                // Skip products without price data from CSV
                if (!price || !cost) {
                  console.warn(`Product ${id} missing price/cost data, skipping`);
                  return null;
                }
                
                return {
                  product_id: id,
                  location: 'All',
                  unit_price: price,
                  unit_cost: cost
                };
              })
              .filter(product => product !== null);
              
            if (productList.length === 0) {
              throw new Error("No products with valid price data found");
            }
            
            console.log("Starting forecast generation with", productList.length, "products");
            setLoading(true);
            
            const result = await fetchMultipleForecast(
              productList,
              forecastStartDate,
              forecastEndDate,
              frequency
            );
            
            if (result && (result.success === true || result.status === "success")) {
              // Process the forecast result
              let finalForecast;
              let totalRevenue = 0;
              let totalQuantity = 0;
              let totalProfit = 0;
              
              if (result.aggregated_forecast && Array.isArray(result.aggregated_forecast)) {
                finalForecast = result.aggregated_forecast;
                if (result.summary) {
                  totalRevenue = result.summary.total_revenue || 0;
                  totalQuantity = result.summary.total_quantity || 0;
                  totalProfit = result.summary.total_profit || 0;
                }
              } else if (result.forecasts && Array.isArray(result.forecasts)) {
                // Aggregate individual forecasts
                const dateMap = new Map();
                result.forecasts.forEach((productForecast: ProductForecast) => {
                  if (productForecast.forecast && Array.isArray(productForecast.forecast)) {
                    productForecast.forecast.forEach((dailyForecast: ForecastItem) => {
                      const date = dailyForecast.date;
                      
                      if (!dateMap.has(date)) {
                        dateMap.set(date, {
                          date,
                          weekday: dailyForecast.weekday,
                          revenue: 0,
                          quantity: 0,
                          profit: 0
                        });
                      }
                      
                      const entry = dateMap.get(date);
                      const revenue = typeof dailyForecast.revenue === 'object' 
                        ? (dailyForecast.revenue?.prediction || 0) 
                        : (parseFloat(dailyForecast.revenue as any) || 0);
                      const quantity = typeof dailyForecast.quantity === 'object' 
                        ? (dailyForecast.quantity?.prediction || 0) 
                        : (parseFloat(dailyForecast.quantity as any) || 0);
                      const profit = typeof dailyForecast.profit === 'object' 
                        ? (dailyForecast.profit?.prediction || 0) 
                        : (parseFloat(dailyForecast.profit as any) || 0);
                      
                      entry.revenue += revenue;
                      entry.quantity += quantity;
                      entry.profit += profit;
                    });
                  }
                  
                  if (productForecast.summary) {
                    totalRevenue += productForecast.summary.total_revenue || 0;
                    totalQuantity += productForecast.summary.total_quantity || 0;
                    totalProfit += productForecast.summary.total_profit || 0;
                  }
                });
                
                finalForecast = Array.from(dateMap.values()).sort((a, b) => 
                  new Date(a.date).getTime() - new Date(b.date).getTime()
                );
              }
              
              if (finalForecast) {
                const summary = {
                  total_revenue: totalRevenue,
                  total_quantity: totalQuantity,
                  total_profit: totalProfit,
                  total_periods: finalForecast.length,
                  average_revenue_per_period: finalForecast.length ? totalRevenue / finalForecast.length : 0,
                  average_quantity_per_period: finalForecast.length ? totalQuantity / finalForecast.length : 0,
                  average_profit_per_period: finalForecast.length ? totalProfit / finalForecast.length : 0
                };
                
                const unifiedResult = {
                  status: "success",
                  forecast: finalForecast,
                  summary,
                  note: `Forecast for all ${productList.length} products aggregated by All Locations`
                };
                
                setAllProductsForecast(unifiedResult as ForecastResult);
                console.log("Initial forecast generated successfully");
              }
            } else {
              throw new Error(result?.error || "Failed to generate forecast");
            }
          } catch (error) {
            console.error("Initial forecast generation failed:", error);
            toast({
              title: "Forecast Error",
              description: "Failed to generate initial forecast. Please try using the refresh button.",
              variant: "destructive",
            });
          } finally {
            setLoading(false);
          }
        } else {
          console.log("Cannot generate initial forecast - missing data:", {
            products: mappedProducts.length,
            locations: mappedLocations.length,
            productAverages: Object.keys(productAveragesData).length
          });
        }
        
        // Mark that we've completed the initial load
        initialMount.current = false;
      } catch (error) {
        console.error("Error loading initial data:", error);
        setIsLoadingOptions(false);
        setLoading(false);
        initialMount.current = false;
        
        // Show error message to user
        toast({
          title: "Error loading data",
          description: "Could not load initial data. Please try refreshing the page.",
          variant: "destructive",
        });
      }
    };

    loadInitialData();
    
    // Event listener for data file changes
    const handleDataFileChanged = () => {
      console.log("Data file changed event received in sales forecasting");
      
      // Prevent infinite loops - only handle file changes if not currently loading
      if (requestInProgressRef.current || isLoadingOptions) {
        console.log("Ignoring data file change - already loading");
        return;
      }
      
      // Clear API data cache
      import("@/lib/api").then(api => {
        if (typeof api.clearDataCache === 'function') {
          api.clearDataCache();
        }
      });
      
      productDataLoadedRef.current = false;
      
      // Reset forecast state
      setForecastResult(null);
      setAllProductsForecast(null);
      
      // Re-initialize ONLY if not already initialized
      if (!initialMount.current) {
        initialMount.current = true;
        loadInitialData();
      }
    };
    
    // Add event listener
    window.addEventListener('dataFileChanged', handleDataFileChanged);
    
    // Cleanup
    return () => {
      window.removeEventListener('dataFileChanged', handleDataFileChanged);
      initialMount.current = false;
    };
  }, []); // Empty dependency array - this effect runs ONCE only

  // Handle product selection change with debouncing
  const handleProductChange = (value: string) => {
    if (value !== selectedProduct) {
    setSelectedProduct(value);
    }
  };
  
  // Handle location selection change with debouncing
  const handleLocationChange = (value: string) => {
    if (value !== selectedLocation) {
    setSelectedLocation(value);
    }
  };

  // Date change handlers with validation
  const handleStartDateChange = (value: string) => {
    console.log("Start date changed to:", value);
    setForecastStartDate(value);
  };

  const handleEndDateChange = (value: string) => {
    console.log("End date changed to:", value);
    setForecastEndDate(value);
  };

  // Handle auto forecast generation with useCallback to avoid dependency issues
  const handleGenerateAutoForecast = useCallback(async () => {
    // Prevent concurrent requests
    if (requestInProgressRef.current) {
      console.log("Auto forecast request already in progress, skipping");
      return;
    }
    
    // Debounce API calls
    const now = Date.now();
    if (now - lastRequestTimeRef.current < 2000) {
      console.log("Debouncing auto forecast - too soon after last request");
      return;
    }
    
    if (!selectedProduct || !selectedLocation) {
      toast({
        title: "Missing information",
        description: "Please select a product and location",
        variant: "destructive",
      });
      return;
    }

    requestInProgressRef.current = true;
    lastRequestTimeRef.current = now;
    setLoading(true);
    
    try {
      // Get the average price and cost for the product from productAverages
      const productPrice = productAverages[selectedProduct]?.price || 0;
      const productCost = productAverages[selectedProduct]?.cost || 0;

      if (productPrice <= 0) {
        throw new Error("Product price information not found or invalid");
      }

      // Make sure we have valid dates
      const today = new Date();
      const oneYearLater = new Date(today);
      oneYearLater.setDate(today.getDate() + 365);
      
      const startDate = forecastStartDate || formatDate(today);
      const endDate = forecastEndDate || formatDate(oneYearLater);

      // Call the forecast API
      const result = await fetchForecastSales(
        selectedProduct,
        selectedLocation,
        productPrice,
        productCost,
        startDate,
        endDate,
        frequency,
        true
      );

      if (!result) {
        throw new Error("No result returned from forecast API");
      }

      if (result.status === "success") {
        // Add any missing properties to ensure the UI doesn't break
        if (result.forecast && Array.isArray(result.forecast)) {
          result.forecast = result.forecast.map((item: ForecastItem) => {
            // Ensure we have properly structured data
            if (typeof item.quantity !== 'object') {
              item.quantity = {
                prediction: item.quantity,
                lower_bound: Math.max(0, item.quantity * 0.85),
                upper_bound: item.quantity * 1.15
              };
            }
            
            if (typeof item.revenue !== 'object') {
              item.revenue = {
                prediction: item.revenue,
                lower_bound: Math.max(0, item.revenue * 0.85),
                upper_bound: item.revenue * 1.15
              };
            }
            
            if (typeof item.profit !== 'object') {
              item.profit = {
                prediction: item.profit,
                lower_bound: Math.max(0, item.profit * 0.85),
                upper_bound: item.profit * 1.15
              };
            }
            
            return item;
          });
        }
        
        setForecastResult(result);
      } else {
        throw new Error(result.message || "Forecast API returned an error");
      }
    } catch (error) {
      console.error("Error generating forecast:", error);
      toast({
        title: "Forecast error",
        description: typeof error === 'object' && error !== null && 'message' in error ? (error as Error).message : "Failed to generate forecast",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
      requestInProgressRef.current = false;
    }
  }, [selectedProduct, selectedLocation, productAverages, forecastStartDate, forecastEndDate, frequency, toast]);

  // REMOVED: Auto-generate forecast useEffect that was causing infinite loops
  // The initial forecast is generated in loadInitialData(), no need for auto-refresh on selection changes

  // Make sure we have valid date ranges always
  useEffect(() => {
    // Only validate if we have valid date strings
    if (!forecastStartDate || !forecastEndDate) {
      return;
    }
    
    // Validate date ranges and fix if needed
    try {
      const startDate = new Date(forecastStartDate);
      const endDate = new Date(forecastEndDate);
      
      // Check if dates are valid
      if (isNaN(startDate.getTime()) || isNaN(endDate.getTime())) {
        console.log("Invalid date detected, resetting to defaults");
        const { startDate: defaultStart, endDate: defaultEnd } = getDefaultDateRange(365);
        setForecastStartDate(defaultStart);
        setForecastEndDate(defaultEnd);
        return;
      }
      
      // Make sure end date is after start date (with minimum 1 day difference)
      if (endDate <= startDate) {
        console.log("End date is not after start date, adjusting...");
        const newEndDate = new Date(startDate);
        newEndDate.setDate(startDate.getDate() + 365); // One year default
        setForecastEndDate(formatDate(newEndDate));
      }
    } catch (e) {
      console.log("Date validation error, resetting to defaults:", e);
      // Reset to default if dates are invalid
      const { startDate, endDate } = getDefaultDateRange(365); // One year default
      setForecastStartDate(startDate);
      setForecastEndDate(endDate);
    }
  }, [forecastStartDate, forecastEndDate]);

  // Calculate seasonal trends from forecast data
  const calculateSeasonalTrend = (forecastData: ForecastItem[]): number[] => {
    if (!forecastData || !forecastData.length) return [];
    
    // Extract days of week
    const weekdayFactors: Record<string, number> = {
      'Monday': 0.95,
      'Tuesday': 0.9,
      'Wednesday': 1.0,
      'Thursday': 1.05,
      'Friday': 1.15,
      'Saturday': 1.25,
      'Sunday': 1.1
    };
    
    // Calculate moving average
    const window = 3;
    const quantities = forecastData.map((item: ForecastItem) => 
      typeof item.quantity === 'object' ? item.quantity.prediction : item.quantity
    );
    
    const movingAvg: number[] = [];
    for (let i = 0; i < quantities.length; i++) {
      let sum = 0;
      let count = 0;
      for (let j = Math.max(0, i - window); j <= Math.min(quantities.length - 1, i + window); j++) {
        sum += quantities[j];
        count++;
      }
      movingAvg.push(sum / count);
    }
    
    // Apply weekday factors to create seasonal trend
    return forecastData.map((item: ForecastItem, i: number) => {
      const weekday = item.weekday;
      const factor = weekdayFactors[weekday] || 1.0;
      return movingAvg[i] * factor;
    });
  };

  const handleGenerateCustomForecast = useCallback(async () => {
    // Prevent concurrent requests
    if (requestInProgressRef.current) {
      console.log("Custom forecast request already in progress, skipping");
      toast({
        title: "Request in progress",
        description: "Please wait for the current forecast to complete",
      });
      return;
    }
    
    // Debounce API calls
    const now = Date.now();
    if (now - lastRequestTimeRef.current < 2000) {
      console.log("Debouncing custom forecast - too soon after last request");
      toast({
        title: "Please wait",
        description: "Processing previous request",
      });
      return;
    }
    
    if (!selectedProduct) {
      toast({
        title: "Missing information",
        description: "Please select a product",
        variant: "destructive",
      });
      return;
    }

    requestInProgressRef.current = true;
    lastRequestTimeRef.current = now;
    setLoading(true);
    
    try {
      // Get the average price and cost for the product from productAverages
      const productPrice = productAverages[selectedProduct]?.price || 0;
      const productCost = productAverages[selectedProduct]?.cost || 0;

      if (productPrice <= 0) {
        throw new Error("Product price information not found or invalid");
      }

      console.log(`Generating custom forecast for product ${selectedProduct} in location ${selectedLocation}`);
      
      // Call the forecast API with a direct await
      const result = await fetchForecastSales(
        selectedProduct,
        selectedLocation,
        productPrice,
        productCost,
        forecastStartDate,
        forecastEndDate,
        frequency,
        true
      );

      if (!result) {
        throw new Error("No result returned from forecast API");
      }

      console.log("Custom forecast API response:", result);

      if (result.status === "success" || result.success === true) {
        // Process the result
        const processedResult = processForecastResult(result);
        
        // Add a note if "All Locations" was selected, but let the backend handle the aggregation
        if (selectedLocation === 'All') {
          processedResult.note = "Using data combined from all locations";
        }
        
        setForecastResult(processedResult);
        toast({
          title: "Forecast generated",
          description: "Custom forecast has been successfully generated",
        });
      } else {
        // Show error instead of fallback data
        const errorMessage = result.message || result.error || "Forecast API returned an error";
        console.error("Forecast API error:", errorMessage);
        
        toast({
          title: "Forecast Error",
          description: errorMessage,
          variant: "destructive",
        });
        
        throw new Error(errorMessage);
      }
    } catch (error) {
      console.error("Error generating custom forecast:", error);
      toast({
        title: "Forecast error",
        description: typeof error === 'object' && error !== null && 'message' in error ? (error as Error).message : "Failed to generate custom forecast",
        variant: "destructive",
      });
      
      // Clear any existing forecast data on error
      setForecastResult(null);
    } finally {
      setLoading(false);
      requestInProgressRef.current = false;
    }
  }, [selectedProduct, selectedLocation, productAverages, forecastStartDate, forecastEndDate, frequency, toast, forecastResult]);

  // Add a helper function to process forecast results
  const processForecastResult = (result: any): ForecastResult => {
    // Handle different API response formats
    const forecast = result.forecast || [];
    
    // Process each forecast item to ensure proper structure
    const processedForecast = forecast.map((item: any) => {
            // Ensure we have properly structured data
            if (typeof item.quantity !== 'object') {
              item.quantity = {
          prediction: parseFloat(item.quantity) || 0,
          lower_bound: Math.max(0, (parseFloat(item.quantity) || 0) * 0.85),
          upper_bound: (parseFloat(item.quantity) || 0) * 1.15
              };
            }
            
            if (typeof item.revenue !== 'object') {
              item.revenue = {
          prediction: parseFloat(item.revenue) || 0,
          lower_bound: Math.max(0, (parseFloat(item.revenue) || 0) * 0.85),
          upper_bound: (parseFloat(item.revenue) || 0) * 1.15
              };
            }
            
            if (typeof item.profit !== 'object') {
              item.profit = {
          prediction: parseFloat(item.profit) || 0,
          lower_bound: Math.max(0, (parseFloat(item.profit) || 0) * 0.85),
          upper_bound: (parseFloat(item.profit) || 0) * 1.15
              };
            }
            
            return item;
          });
    
    // Create a processed result with properly structured data
    return {
      status: "success",
      forecast: processedForecast,
      summary: result.summary || {
        total_revenue: processedForecast.reduce((sum: number, item: any) => 
          sum + (typeof item.revenue === 'object' ? item.revenue.prediction : parseFloat(item.revenue) || 0), 0),
        total_quantity: processedForecast.reduce((sum: number, item: any) => 
          sum + (typeof item.quantity === 'object' ? item.quantity.prediction : parseFloat(item.quantity) || 0), 0),
        total_profit: processedForecast.reduce((sum: number, item: any) => 
          sum + (typeof item.profit === 'object' ? item.profit.prediction : parseFloat(item.profit) || 0), 0),
        average_revenue_per_period: processedForecast.length ? 
          processedForecast.reduce((sum: number, item: any) => 
            sum + (typeof item.revenue === 'object' ? item.revenue.prediction : parseFloat(item.revenue) || 0), 0) / processedForecast.length : 0,
        average_quantity_per_period: processedForecast.length ? 
          processedForecast.reduce((sum: number, item: any) => 
            sum + (typeof item.quantity === 'object' ? item.quantity.prediction : parseFloat(item.quantity) || 0), 0) / processedForecast.length : 0,
        average_profit_per_period: processedForecast.length ? 
          processedForecast.reduce((sum: number, item: any) => 
            sum + (typeof item.profit === 'object' ? item.profit.prediction : parseFloat(item.profit) || 0), 0) / processedForecast.length : 0,
        total_periods: processedForecast.length
      }
    };
  };

  // Prepare chart data for forecast
  const prepareChartData = (source: ForecastResult | null = forecastResult): ChartDataItem[] => {
    if (!source || !source.forecast || !Array.isArray(source.forecast)) {
      console.log("Invalid source data for chart preparation", source);
      return [];
    }
    
    try {
      // Process forecast data for charting
      let chartData = source.forecast.map(item => {
        if (!item) return null;
        
        // Handle different possible data structures
        let revenue, quantity, profit;
        let revenueLower, revenueUpper, quantityLower, quantityUpper, profitLower, profitUpper;
        
        // Extract revenue data - handle both object and scalar formats
        if (typeof item.revenue === 'object' && item.revenue !== null) {
          revenue = item.revenue.prediction || 0;
          revenueLower = item.revenue.lower_bound;
          revenueUpper = item.revenue.upper_bound;
        } else {
          revenue = parseFloat(item.revenue as any) || 0;
          revenueLower = revenue * 0.9;
          revenueUpper = revenue * 1.1;
        }
        
        // Extract quantity data - handle both object and scalar formats
        if (typeof item.quantity === 'object' && item.quantity !== null) {
          quantity = item.quantity.prediction || 0;
          quantityLower = item.quantity.lower_bound;
          quantityUpper = item.quantity.upper_bound;
        } else {
          quantity = parseFloat(item.quantity as any) || 0;
          quantityLower = quantity * 0.9;
          quantityUpper = quantity * 1.1;
        }
        
        // Extract profit data - handle both object and scalar formats
        if (typeof item.profit === 'object' && item.profit !== null) {
          profit = item.profit.prediction || 0;
          profitLower = item.profit.lower_bound;
          profitUpper = item.profit.upper_bound;
      } else {
          profit = parseFloat(item.profit as any) || 0;
          profitLower = profit * 0.9;
          profitUpper = profit * 1.1;
        }
        
        return {
          date: item.date || new Date().toISOString().split('T')[0],
          weekday: item.weekday || 'Unknown',
          revenue,
          quantity,
          profit,
          revenueLower,
          revenueUpper,
          quantityLower,
          quantityUpper,
          profitLower,
          profitUpper
        };
      }).filter(Boolean) as ChartDataItem[]; // Remove any null items
      
      // Sort by date
      chartData.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
      
      console.log(`Prepared ${chartData.length} chart data points`);
      
      // Removed seasonality trend calculation
      
      return chartData;
    } catch (error) {
      console.error("Error preparing chart data:", error);
      return [];
    }
  };
  
  const prepareAllProductsChartData = (): ChartDataItem[] => {
    try {
      if (!allProductsForecast) {
        console.log("No all products forecast data available");
        return [];
      }
      
      // Check for aggregated_forecast in the API response
      const forecastData = allProductsForecast.aggregated_forecast || allProductsForecast.forecast;
      
      if (!forecastData || !Array.isArray(forecastData)) {
        console.log("Invalid forecast data structure:", allProductsForecast);
        return [];
      }
      
      console.log("Raw forecast data sample:", forecastData.slice(0, 2));
      
      // Transform aggregated forecast data to be compatible with prepareChartData
      const transformedData = forecastData.map((item: any) => {
        // If the item has confidence intervals as separate fields (aggregated format)
        if (item.revenue_lower !== undefined || item.revenue_upper !== undefined) {
          return {
            ...item,
            revenue: {
              prediction: item.revenue,
              lower_bound: item.revenue_lower,
              upper_bound: item.revenue_upper
            },
            quantity: {
              prediction: item.quantity,
              lower_bound: item.quantity_lower,
              upper_bound: item.quantity_upper
            },
            profit: {
              prediction: item.profit,
              lower_bound: item.profit_lower,
              upper_bound: item.profit_upper
            }
          };
        }
        // Otherwise return as-is (already in correct format)
        return item;
      });
      
      // Create a temporary forecast result with the correct structure
      const tempForecast = {
        ...allProductsForecast,
        forecast: transformedData
      };
      
      const chartData = prepareChartData(tempForecast);
      console.log("Prepared chart data:", chartData.length > 0 ? `${chartData.length} items, sample: ${JSON.stringify(chartData[0])}` : "empty");
      return chartData;
    } catch (error) {
      console.error("Error preparing all products chart data:", error);
      return [];
    }
  };
  
  // Get appropriate data based on tab and forecast status
  const getChartData = (): ChartDataItem[] => {
    if (activeTab === "auto") {
      return allProductsForecast ? prepareAllProductsChartData() : [];
      } else {
      return forecastResult ? prepareChartData() : [];
    }
  };
  
  // Format currency values
  const formatCurrency = (value: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value);
  };

  // Format date labels based on frequency
  const formatDateForFrequency = (dateStr: string, freq: string, index: number): string => {
    const date = new Date(dateStr);
    
    switch (freq) {
      case 'D':
        // Daily: Show month/day format (e.g., "6/12", "6/13")
        return `${date.getMonth() + 1}/${date.getDate()}`;
        
      case 'W':
        // Weekly: Show "Week X" or "MonthName Week X"
        const weekNum = Math.floor(index / 1) + 1;
        const monthName = date.toLocaleDateString('en-US', { month: 'short' });
        return `${monthName} W${weekNum}`;
        
      case 'M':
        // Monthly: Show "MonthName Year" format (e.g., "Jun 2024", "Jul 2024")
        return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
        
      default:
        // Fallback to month/day
        return `${date.getMonth() + 1}/${date.getDate()}`;
    }
  };
  
  // Get summary data based on active tab
  const getSummary = () => {
    if (activeTab === "auto" && allProductsForecast?.summary) {
      return allProductsForecast.summary;
    } else if (forecastResult?.summary) {
      return forecastResult.summary;
    }
    return null;
  };
  
  // Convert chart data to the appropriate format for display
  const getFormattedChartData = () => {
    const chartData = getChartData();
    
    // Get current frequency (for automatic forecast, use 'M', for custom use form frequency)
    const currentFrequency = activeTab === "auto" ? 'M' : frequency;
    
    // Add formatted display dates based on frequency
    const formattedChartData = chartData.map((item, index) => ({
      ...item,
      displayDate: formatDateForFrequency(item.date, currentFrequency, index)
    }));
    
    // Calculate max values for y-axis scaling
    const maxMetricValue = Math.max(
      ...formattedChartData.map(item => {
        if (metricView === "revenue") {
          return item.revenueUpper || item.revenue;
        } else if (metricView === "quantity") {
          return item.quantityUpper || item.quantity;
        } else {
          return item.profitUpper || item.profit;
        }
      })
    );
      
    return {
      chartData: formattedChartData,
      maxMetricValue
    };
  };
  
  // Get the title of the forecast
  const getForecastTitle = () => {
    if (activeTab === "auto") {
      return "Overall Business Forecast";
    } else {
      const product = products.find(p => p.id.toString() === selectedProduct);
      const location = locations.find(l => l.id === selectedLocation);
      return `Forecast for ${product?.name || 'Selected Product'} in ${location?.name || 'Selected Location'}`;
    }
  };

  // Update the button click handler
  const handleRefreshForecastClick = () => {
    setLoading(true);
    generateAllProductsForecast()
      .then(() => {
        console.log("Forecast refresh completed successfully");
        toast({
          title: "Forecast refreshed",
          description: "Forecast data has been updated successfully",
        });
      })
      .catch((error) => {
        console.error("Error refreshing forecast:", error);
        toast({
          title: "Refresh failed", 
          description: "Could not refresh forecast data. Please check API connectivity.",
          variant: "destructive",
        });
        
        // Clear forecast data on error instead of using fallback
        setAllProductsForecast(null);
      })
      .finally(() => {
        setLoading(false);
      });
  };

  return (
    <div className="container mx-auto py-6 px-4 md:px-6">
      <h1 className="text-3xl font-bold mb-6">Sales Forecasting</h1>
      
      <Tabs defaultValue="auto" value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="auto">
            <RefreshCw className="mr-2 h-4 w-4" />
            Automatic Forecast
          </TabsTrigger>
          <TabsTrigger value="custom">
            <Calendar className="mr-2 h-4 w-4" />
            Custom Forecast
          </TabsTrigger>
        </TabsList>

        <TabsContent value="auto" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Automatic Forward-Looking Forecast</CardTitle>
              <CardDescription>
                View overall business forecast for the next 1 year based on historical patterns
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div className="flex flex-col md:flex-row items-start gap-4 mb-6">
                  <div className="w-full md:w-1/2">
                    {/* Removed Visualization Options toggles */}
                  </div>

                  <div className="w-full md:w-1/2 flex justify-end items-end h-full">
                    <Button onClick={handleRefreshForecastClick} disabled={loading || requestInProgressRef.current}>
                      {loading ? (
                        <>
                          <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                          Loading...
                        </>
                      ) : (
                        <>
                          <RefreshCw className="mr-2 h-4 w-4" />
                          Refresh Forecast
                        </>
                      )}
                    </Button>
                  </div>
                  </div>
                
                {allProductsForecast ? (
                  <div className="space-y-6">
                    <h3 className="text-xl font-bold">{getForecastTitle()}</h3>
                    
                    {/* Summary Cards */}
                    {allProductsForecast.summary && (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                        <Card>
                          <CardHeader className="py-4">
                            <CardTitle className="text-lg">Total Revenue</CardTitle>
                          </CardHeader>
                          <CardContent>
                            <p className="text-2xl font-bold">
                              {formatCurrency(allProductsForecast.summary.total_revenue)}
                            </p>
                          </CardContent>
                        </Card>
                        
                        <Card>
                          <CardHeader className="py-4">
                            <CardTitle className="text-lg">Total Profit</CardTitle>
                          </CardHeader>
                          <CardContent>
                            <p className="text-2xl font-bold">
                              {formatCurrency(allProductsForecast.summary.total_profit)}
                            </p>
                          </CardContent>
                        </Card>
                </div>
                    )}
                    
                    {/* Main Chart */}
                    <div className="h-96 w-full">
                      <div className="flex justify-end mb-2 space-x-4">
                        <div className="flex items-center space-x-2">
                          <Label htmlFor="show-revenue" className="text-sm font-medium text-blue-600">
                            Show Revenue
                          </Label>
                          <div className="relative inline-flex h-4 w-8 items-center rounded-full transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary" 
                               onClick={() => setShowRevenue(!showRevenue)}
                               style={{ backgroundColor: showRevenue ? '#2563eb' : '#d1d5db' }}>
                            <span className={`${showRevenue ? 'translate-x-4' : 'translate-x-0'} inline-block h-3 w-3 rounded-full bg-white transition-transform`}></span>
                    </div>
                    </div>
                        <div className="flex items-center space-x-2">
                          <Label htmlFor="show-profit" className="text-sm font-medium text-green-600">
                            Show Profit
                          </Label>
                          <div className="relative inline-flex h-4 w-8 items-center rounded-full transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary" 
                               onClick={() => setShowProfit(!showProfit)}
                               style={{ backgroundColor: showProfit ? '#16a34a' : '#d1d5db' }}>
                            <span className={`${showProfit ? 'translate-x-4' : 'translate-x-0'} inline-block h-3 w-3 rounded-full bg-white transition-transform`}></span>
                          </div>
                    </div>
                  </div>

                      {/* Check if we have valid chart data before rendering */}
                      {(() => {
                        const { chartData } = getFormattedChartData();
                        return chartData && chartData.length > 0 ? (
                        <ResponsiveContainer width="100%" height="100%">
                          <RechartsLineChart
                            data={chartData}
                            margin={{ top: 20, right: 20, left: 20, bottom: 20 }}
                          >
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis 
                              dataKey="displayDate" 
                              tick={{ fontSize: 12 }} 
                              height={40}
                            />
                            <YAxis 
                              yAxisId="left"
                              width={80}
                              tickFormatter={(value) => formatCurrency(value).replace('.00', '')}
                              tick={{ fontSize: 12 }}
                              domain={['auto', 'auto']}
                            />
                            <Tooltip 
                              formatter={(value, name) => {
                                if (name === 'seasonalTrend') return [value, 'Seasonal Trend'];
                                if (name === 'revenue') return [formatCurrency(Number(value)), 'Revenue'];
                                if (name === 'profit') return [formatCurrency(Number(value)), 'Profit'];
                                return [Number(value).toLocaleString(), name];
                              }}
                              labelFormatter={(label) => label} // Use formatted label directly
                            />
                            <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
                            
                            {/* Revenue */}
                            {showRevenue && (
                            <Line
                              type="monotone"
                                dataKey="revenue"
                                stroke="#2563eb" // blue-600
                              strokeWidth={2}
                                dot={{ r: 4 }}
                                activeDot={{ r: 8 }}
                                yAxisId="left"
                                name="Revenue"
                              />
                            )}
                            
                            {/* Profit */}
                            {showProfit && (
                                <Line
                                  type="monotone"
                                dataKey="profit"
                                stroke="#16a34a" // green-600
                                strokeWidth={2}
                                dot={{ r: 4 }}
                                activeDot={{ r: 8 }}
                                yAxisId="left"
                                name="Profit"
                              />
                            )}
                            
                            {/* Removed Seasonal Trend line */}
                          </RechartsLineChart>
                        </ResponsiveContainer>
                      ) : (
                        <div className="flex flex-col items-center justify-center h-full">
                          <p className="text-gray-500">No chart data available</p>
                        </div>
                      );
                      })()}
                        </div>
                        </div>
                ) : (
                  <div className="flex flex-col items-center justify-center py-12">
                    {loading ? (
                      <div className="flex flex-col items-center space-y-4">
                        <RefreshCw className="h-12 w-12 animate-spin text-gray-400" />
                        <p className="text-lg text-gray-500">Generating forecast...</p>
                        </div>
                    ) : (
                      <div className="flex flex-col items-center space-y-4">
                        <FileText className="h-12 w-12 text-gray-400" />
                        <div className="text-center">
                          <p className="text-lg text-gray-500">No forecast data yet</p>
                          <p className="text-sm text-gray-400">Click 'Refresh Forecast' to generate a forecast</p>
                      </div>
                </div>
              )}
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="custom" className="mt-4">
              <Card>
                <CardHeader>
                  <CardTitle>Custom Forecast Parameters</CardTitle>
                  <CardDescription>Configure the parameters for your forecast.</CardDescription>
                </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                <div>
                  <Label htmlFor="product" className="mb-2 block">Product</Label>
                    <Select 
                      value={selectedProduct} 
                      onValueChange={handleProductChange}
                      disabled={loading || isLoadingOptions}
                    >
                      <SelectTrigger id="product">
                        <SelectValue placeholder="Select product" />
                      </SelectTrigger>
                      <SelectContent>
                      {products.map((product) => (
                        <SelectItem key={product.id} value={product.id.toString()}>
                          {product.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                <div>
                  <Label htmlFor="location" className="mb-2 block">Location</Label>
                    <Select 
                      value={selectedLocation} 
                      onValueChange={handleLocationChange}
                      disabled={loading || isLoadingOptions}
                    >
                      <SelectTrigger id="location">
                        <SelectValue placeholder="Select location" />
                      </SelectTrigger>
                      <SelectContent>
                      {locations.map((location) => (
                        <SelectItem key={location.id} value={location.id}>
                          {location.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                <div>
                  <Label htmlFor="start-date" className="mb-2 block">Start Date</Label>
                  <Input
                    id="start-date"
                    type="date"
                    value={forecastStartDate}
                    onChange={(e) => handleStartDateChange(e.target.value)}
                    disabled={loading}
                    />
                  </div>

                <div>
                  <Label htmlFor="end-date" className="mb-2 block">End Date</Label>
                  <Input
                    id="end-date"
                        type="date"
                        value={forecastEndDate}
                    onChange={(e) => handleEndDateChange(e.target.value)}
                    disabled={loading}
                      />
                  </div>

                <div>
                  <Label className="mb-2 block">Forecast Frequency</Label>
                  <RadioGroup
                    value={frequency}
                    onValueChange={(value) => setFrequency(value as "D" | "W" | "M")}
                    className="flex space-x-4"
                    disabled={loading}
                  >
                      <div className="flex items-center space-x-2">
                      <RadioGroupItem value="D" id="daily" />
                      <Label htmlFor="daily">Daily</Label>
                      </div>
                      <div className="flex items-center space-x-2">
                      <RadioGroupItem value="W" id="weekly" />
                      <Label htmlFor="weekly">Weekly</Label>
                      </div>
                      <div className="flex items-center space-x-2">
                      <RadioGroupItem value="M" id="monthly" />
                      <Label htmlFor="monthly">Monthly</Label>
                      </div>
                  </RadioGroup>
                    </div>
                  </div>

              <div className="flex justify-end">
                  <Button
                    onClick={handleGenerateCustomForecast}
                    disabled={loading || isLoadingOptions || requestInProgressRef.current}
                  >
                    {loading ? (
                      <>
                        <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                        Generating...
                      </>
                    ) : (
                      <>
                        <LineChart className="mr-2 h-4 w-4" />
                        Generate Forecast
                      </>
                    )}
                  </Button>
            </div>
            </CardContent>
          </Card>
          
          {/* Custom Forecast Results */}
          {forecastResult && (
            <Card className="mt-6">
              <CardHeader>
                <CardTitle>{getForecastTitle()}</CardTitle>
              </CardHeader>
              <CardContent>
                {/* Summary Cards */}
                {forecastResult.summary && (
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                    <Card>
                      <CardHeader className="py-4">
                        <CardTitle className="text-lg">Total Revenue</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <p className="text-2xl font-bold">
                          {formatCurrency(forecastResult.summary.total_revenue)}
                    </p>
                  </CardContent>
                </Card>
                    
                  <Card>
                      <CardHeader className="py-4">
                        <CardTitle className="text-lg">Total Quantity</CardTitle>
                    </CardHeader>
                    <CardContent>
                          <p className="text-2xl font-bold">
                          {forecastResult.summary.total_quantity.toLocaleString()}
                        </p>
                    </CardContent>
                  </Card>

                  <Card>
                      <CardHeader className="py-4">
                        <CardTitle className="text-lg">Total Profit</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <p className="text-2xl font-bold">
                          {formatCurrency(forecastResult.summary.total_profit)}
                        </p>
                      </CardContent>
                    </Card>
                  </div>
                )}
                
                {/* Main Chart */}
                <div className="h-96 w-full">
                  <div className="flex justify-end mb-2 space-x-4">
                    <div className="flex items-center space-x-2">
                      <Label htmlFor="custom-show-revenue" className="text-sm font-medium text-blue-600">
                        Show Revenue
                      </Label>
                      <div className="relative inline-flex h-4 w-8 items-center rounded-full transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary" 
                           onClick={() => setShowCustomRevenue(!showCustomRevenue)}
                           style={{ backgroundColor: showCustomRevenue ? '#2563eb' : '#d1d5db' }}>
                        <span className={`${showCustomRevenue ? 'translate-x-4' : 'translate-x-0'} inline-block h-3 w-3 rounded-full bg-white transition-transform`}></span>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Label htmlFor="custom-show-profit" className="text-sm font-medium text-green-600">
                        Show Profit
                      </Label>
                      <div className="relative inline-flex h-4 w-8 items-center rounded-full transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary" 
                           onClick={() => setShowCustomProfit(!showCustomProfit)}
                           style={{ backgroundColor: showCustomProfit ? '#16a34a' : '#d1d5db' }}>
                        <span className={`${showCustomProfit ? 'translate-x-4' : 'translate-x-0'} inline-block h-3 w-3 rounded-full bg-white transition-transform`}></span>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Label htmlFor="custom-show-quantity" className="text-sm font-medium text-orange-600">
                        Show Quantity
                      </Label>
                      <div className="relative inline-flex h-4 w-8 items-center rounded-full transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary" 
                           onClick={() => setShowCustomQuantity(!showCustomQuantity)}
                           style={{ backgroundColor: showCustomQuantity ? '#ea580c' : '#d1d5db' }}>
                        <span className={`${showCustomQuantity ? 'translate-x-4' : 'translate-x-0'} inline-block h-3 w-3 rounded-full bg-white transition-transform`}></span>
                      </div>
                    </div>
                  </div>
                        <ResponsiveContainer width="100%" height="100%">
                    <RechartsLineChart
                            data={(() => {
                              const { chartData } = getFormattedChartData();
                              return chartData;
                            })()}
                      margin={{ top: 20, right: 20, left: 20, bottom: 20 }}
                          >
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis 
                              dataKey="displayDate" 
                              tick={{ fontSize: 12 }} 
                        height={40}
                      />
                      <YAxis 
                        yAxisId="left"
                        width={80}
                        tickFormatter={(value) => formatCurrency(value).replace('.00', '')}
                        tick={{ fontSize: 12 }}
                        domain={['auto', 'auto']}
                      />
                      {/* Right Y-axis for quantity */}
                      {showCustomQuantity && (
                        <YAxis 
                          yAxisId="right"
                          orientation="right"
                          width={60}
                          tickFormatter={(value) => Number(value).toLocaleString()}
                          tick={{ fontSize: 12 }}
                          domain={['auto', 'auto']}
                        />
                      )}
                            <Tooltip 
                        formatter={(value, name) => {
                          if (name === 'seasonalTrend') return [value, 'Seasonal Trend'];
                          if (name === 'revenue') return [formatCurrency(Number(value)), 'Revenue'];
                          if (name === 'profit') return [formatCurrency(Number(value)), 'Profit'];
                          if (name === 'quantity') return [Number(value).toLocaleString(), 'Quantity'];
                          return [Number(value).toLocaleString(), name];
                        }}
                        labelFormatter={(label) => label} // Use formatted label directly
                      />
                      <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
                      
                      {/* Revenue */}
                      {showCustomRevenue && (
                        <Line
                              type="monotone"
                          dataKey="revenue"
                          stroke="#2563eb" // blue-600
                          strokeWidth={2}
                          dot={{ r: 4 }}
                          activeDot={{ r: 8 }}
                          yAxisId="left"
                          name="Revenue"
                        />
                      )}
                      
                      {/* Profit */}
                      {showCustomProfit && (
                        <Line
                                type="monotone"
                          dataKey="profit"
                          stroke="#16a34a" // green-600
                          strokeWidth={2}
                          dot={{ r: 4 }}
                          activeDot={{ r: 8 }}
                          yAxisId="left"
                          name="Profit"
                        />
                      )}
                      
                      {/* Quantity */}
                      {showCustomQuantity && (
                        <Line
                          type="monotone"
                          dataKey="quantity"
                          stroke="#ea580c" // orange-600
                          strokeWidth={2}
                          dot={{ r: 4 }}
                          activeDot={{ r: 8 }}
                          yAxisId="right"
                          name="Quantity"
                        />
                      )}
                      
                      {/* Removed Seasonal Trend line */}
                    </RechartsLineChart>
                        </ResponsiveContainer>
                      </div>
                    </CardContent>
                  </Card>
              )}
        </TabsContent>
      </Tabs>
    </div>
  );
} 