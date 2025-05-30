"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import { BarChart, CartesianGrid, XAxis, YAxis, Legend, Bar, ResponsiveContainer } from "recharts"
import { ArrowRight, RotateCcw, Check, AlertCircle } from "lucide-react"
import { useToast } from "@/components/ui/use-toast"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { simulateScenarios, mapToApiOrderFormat, getProducts, getLocations, getProductData } from "@/lib/api"

export default function ScenarioPlannerPage() {
  const { toast } = useToast()

  // Initial data will be updated from API
  const [productAverages, setProductAverages] = useState<Record<string, {price: number, cost: number}>>({});

  // Initial scenario data - completely empty, will be populated from API data
  const initialScenario = {
    locationId: "",
    productId: "",
    unitCost: 0,
    unitPrice: 0,
  }

  // State for original and simulated scenarios
  const [originalScenario, setOriginalScenario] = useState(initialScenario)
  const [simulatedScenario, setSimulatedScenario] = useState(initialScenario)
  const [isSimulated, setIsSimulated] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState("")
  const [scenarioResults, setScenarioResults] = useState<any[]>([])

  // State for products and locations
  const [products, setProducts] = useState<{id: string, name: string}[]>([])
  const [locations, setLocations] = useState<{id: string, name: string}[]>([])
  const [isLoadingOptions, setIsLoadingOptions] = useState(true)
  const [averageStats, setAverageStats] = useState({ price: 0, cost: 0 });

  // Load product data from the data file
  const loadProductData = async () => {
    try {
      setIsLoading(true);
      const response = await getProductData();
      const productData = response.products;
      
      // Create a map from product IDs to their price and cost data
      const productMap: Record<string, {price: number, cost: number}> = {};
      
      productData.forEach((product: any) => {
        // Use the productId directly as the key (as a string)
        // Format price and cost to 2 decimal places
        productMap[product.productId.toString()] = {
          price: Math.round(product.price * 100) / 100,
          cost: Math.round(product.cost * 100) / 100
        };
      });
      
      // Update the product averages state
      setProductAverages(productMap);
      
      // If we have a selected product, update its price and cost
      if (simulatedScenario.productId && productMap[simulatedScenario.productId]) {
        const selectedProductData = productMap[simulatedScenario.productId];
        
        // Format to 2 decimal places
        const price = Math.round(selectedProductData.price * 100) / 100;
        const cost = Math.round(selectedProductData.cost * 100) / 100;
        
        setSimulatedScenario(prev => ({
          ...prev,
          unitPrice: price,
          unitCost: cost
        }));
        
        setAverageStats({
          price: price,
          cost: cost
        });
      }
      
      toast({
        title: "Product data loaded",
        description: `Loaded data from ${response.source || "data file"}`,
      });
      
      // Return the product map for potential use by the caller
      return productMap;
      
    } catch (err) {
      console.error("Error loading product data:", err);
      setError("Failed to load product price data");
      
      toast({
        variant: "destructive",
        title: "Error loading product data",
        description: "Failed to load product price and cost data from the file.",
      });
      
      // Return empty map on error
      return {};
      
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch products and locations from API
  useEffect(() => {
    const fetchOptions = async () => {
      setIsLoadingOptions(true)
      
      try {
        // Load product price and cost data first to have the averages available
        await loadProductData();
        
        // Fetch products
        const productsData = await getProducts()
        
        // Map products to use numeric IDs
        const mappedProducts = productsData.map((product: any) => ({
          ...product,
          id: product.id.replace(/PROD0*/, '') // Remove PROD prefix and leading zeros
        }));
        
        setProducts(mappedProducts)
        
        // Fetch locations
        const locationsData = await getLocations()
        setLocations(locationsData)
        
        // Set default values only after data is loaded
        if (mappedProducts.length > 0 && locationsData.length > 0) {
          console.log("Setting default product and location from loaded data");
          
          // Select first product and location as defaults
          const defaultLocationId = locationsData[0].id;
          const defaultProductId = mappedProducts[0].id;
          
          // Get product averages from the current state
          const currentProductAverages = { ...productAverages };
          
          // Check if we have price/cost data for this product
          let defaultPrice = 0;
          let defaultCost = 0;
          
          if (currentProductAverages[defaultProductId]) {
            defaultPrice = Math.round(currentProductAverages[defaultProductId].price * 100) / 100;
            defaultCost = Math.round(currentProductAverages[defaultProductId].cost * 100) / 100;
          }
          
          const defaultScenario = {
            locationId: defaultLocationId,
            productId: defaultProductId,
            unitPrice: defaultPrice,
            unitCost: defaultCost
          };
          
          setOriginalScenario(defaultScenario);
          setSimulatedScenario(defaultScenario);
          
          // Also update average stats
          setAverageStats({
            price: defaultPrice,
            cost: defaultCost
          });
        }
      } catch (err) {
        console.error("Error loading options:", err)
        setError("Failed to load product and location options")
      } finally {
        setIsLoadingOptions(false)
      }
    }
    
    fetchOptions()
    
    // Listen for data file changes from other parts of the app
    const handleDataFileChanged = (event: Event) => {
      console.log("Data file changed event received in scenario planner");
      // Reload product data when file changes
      fetchOptions();
      // Reset simulation state
      setIsSimulated(false);
      setScenarioResults([]);
    };
    
    // Add event listener for data file changes
    window.addEventListener('dataFileChanged', handleDataFileChanged);
    
    // Clean up event listener when component unmounts
    return () => {
      window.removeEventListener('dataFileChanged', handleDataFileChanged);
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // Handle input changes
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    
    // Format to 2 decimal places for price and cost fields
    if (name === 'unitPrice' || name === 'unitCost') {
      const numValue = Number.parseFloat(value) || 0;
      // Round to 2 decimal places
      const formattedValue = Math.round(numValue * 100) / 100;
      
      setSimulatedScenario((prev) => ({
        ...prev,
        [name]: formattedValue,
      }))
    } else {
      setSimulatedScenario((prev) => ({
        ...prev,
        [name]: Number.parseFloat(value) || 0,
      }))
    }
  }

  // Handle select changes
  const handleSelectChange = (name: string, value: string) => {
    let updateObj: any = { [name]: value };
    
    // If product changes, update price and cost to match product average
    if (name === 'productId' && productAverages[value]) {
      // Format to 2 decimal places
      const price = Math.round(productAverages[value].price * 100) / 100;
      const cost = Math.round(productAverages[value].cost * 100) / 100;
      
      updateObj.unitPrice = price;
      updateObj.unitCost = cost;
      
      // Also update average stats
      setAverageStats({
        price: price,
        cost: cost
      });
    }
    
    setSimulatedScenario((prev) => ({
      ...prev,
      ...updateObj
    }));
  }

  // Simulate revenue prediction
  const simulateRevenue = async () => {
    setIsLoading(true)
    setError("")
    
    try {
      // Validate required fields first
      if (!simulatedScenario.locationId) {
        throw new Error("Please select a location before simulating");
      }
      
      if (!simulatedScenario.productId) {
        throw new Error("Please select a product before simulating");
      }
      
      // Map the frontend data structure to the format expected by the API
      const baseData = mapToApiOrderFormat(simulatedScenario)
      
      // Add current date values if missing
      const today = new Date();
      if (!baseData.Month) baseData.Month = today.getMonth() + 1; // Months are 0-indexed in JS
      if (!baseData.Day) baseData.Day = today.getDate();
      if (!baseData.Year) baseData.Year = today.getFullYear();
      
      console.log('Simulating with data:', baseData);
      
      // Set up a timeout
      const abortController = new AbortController();
      const timeoutId = setTimeout(() => abortController.abort(), 20000);
      
      try {
        // Call the API directly with the base data
        // The API will handle the price variations internally
        const apiResponse = await simulateScenarios(baseData);
        
        // Clear the timeout
        clearTimeout(timeoutId);
        
        console.log('API Response:', apiResponse);
        
        const resultsArray = Array.isArray(apiResponse?.results) ? apiResponse.results : 
                            (apiResponse?.simulations ? apiResponse.simulations : []);
        
        setScenarioResults(resultsArray);
        setIsSimulated(true);
        
        // Show a note if provided in the API response
        if (apiResponse?.note) {
          toast({
            title: "Scenarios simulated",
            description: apiResponse.note,
          });
        } else if (simulatedScenario.locationId === 'All') {
          // Fallback for "All Locations" if no note in response
          toast({
            title: "Scenarios simulated",
            description: "Using combined location data. Results represent the sum across all regions.",
          });
        } else {
          toast({
            title: "Scenarios simulated",
            description: "The quantity and revenue predictions have been updated based on your changes.",
          });
        }
      } catch (fetchError) {
        clearTimeout(timeoutId);
        
        if (fetchError.name === 'AbortError') {
          throw new Error('The request timed out. Please try again with simpler parameters.');
        }
        
        throw fetchError;
      }
    } catch (err) {
      console.error("Error simulating scenarios:", err);
      
      // Show a more descriptive error message
      const errorMessage = err instanceof Error 
        ? err.message 
        : "Failed to simulate scenarios. Please try again.";
      
      setError(errorMessage);
      
      toast({
        variant: "destructive",
        title: "Simulation failed",
        description: errorMessage,
      });
      
      // If we have some scenario parameters, try to at least show something
      if (scenarioResults.length === 0) {
        // Create fallback data
        const basePrice = simulatedScenario.unitPrice;
        const baseCost = simulatedScenario.unitCost;
        
        setScenarioResults([
          {
            name: "Current Scenario (Fallback)",
            revenue: basePrice * 3,
            profit: (basePrice - baseCost) * 3,
            quantity: 3
          },
          {
            name: "Higher Price (Fallback)",
            revenue: basePrice * 1.1 * 2,
            profit: (basePrice * 1.1 - baseCost) * 2,
            quantity: 2
          },
          {
            name: "Lower Price (Fallback)",
            revenue: basePrice * 0.9 * 4,
            profit: (basePrice * 0.9 - baseCost) * 4,
            quantity: 4
          }
        ]);
        
        setIsSimulated(true);
      }
    } finally {
      setIsLoading(false);
    }
  }

  // Reset to original scenario
  const resetScenario = () => {
    // Get the current product's averages
    const currentProductId = simulatedScenario.productId;
    const productAvg = productAverages[currentProductId];
    
    // Set proper values based on product averages
    const resetScenario = {
      ...simulatedScenario,
      unitPrice: productAvg ? Math.round(productAvg.price * 100) / 100 : 0,
      unitCost: productAvg ? Math.round(productAvg.cost * 100) / 100 : 0
    };
    
    setSimulatedScenario(resetScenario);
    setIsSimulated(false);
    setScenarioResults([]);
    setError("");

    // Update average stats
    if (productAvg) {
      setAverageStats({
        price: Math.round(productAvg.price * 100) / 100,
        cost: Math.round(productAvg.cost * 100) / 100
      });
    }

    toast({
      title: "Scenario reset",
      description: "Values have been reset to the product's average price and cost.",
    });
  }

  // Apply the simulated scenario
  const applyScenario = () => {
    // Get the optimal scenario from results (highest profit)
    const optimalScenario = [...scenarioResults].sort((a, b) => {
      const profitA = a.Profit || a.profit || 0;
      const profitB = b.Profit || b.profit || 0;
      return profitB - profitA; // Sort descending
    })[0];
    
    if (optimalScenario) {
      // Get the price from the optimal scenario
      const optimalPrice = optimalScenario['Unit Price'] || 100;
      
      // Update the simulated scenario with the optimal price
      setSimulatedScenario(prev => ({
        ...prev,
        unitPrice: optimalPrice
      }));
      
      // Re-simulate with the optimal price
      setTimeout(() => {
        simulateRevenue();
      }, 100);
      
      toast({
        title: "Optimal scenario applied",
        description: `Applied the highest profit scenario with price $${optimalPrice.toFixed(2)}.`,
      });
    } else {
      toast({
        title: "Scenario applied",
        description: "The simulated scenario has been applied as the new baseline.",
      });
    }
  }

  // Prepare chart data from scenario results
  const getChartData = () => {
    // Defensive: ensure scenarioResults is always an array
    const safeResults = Array.isArray(scenarioResults) ? scenarioResults : [];
    if (!isSimulated || safeResults.length === 0) {
      // Return placeholder data if not simulated yet
      return [
        {
          name: "Current",
          revenue: 0,
          profit: 0,
          quantity: 0,
          raw_quantity: 0
        }
      ]
    }
    
    // Map backend keys to frontend keys
    const chartData = safeResults.map(result => ({
      name: result.Scenario || result.scenario,
      revenue: result["Predicted Revenue"] ?? result.predicted_revenue ?? 0,
      profit: result.Profit ?? result.profit ?? 0,
      quantity: result["Predicted Quantity"] ?? result.predicted_quantity ?? 0,
      raw_quantity: result["raw_quantity"] ?? result["Predicted Quantity"] ?? result.predicted_quantity ?? 0
    }));
    
    // Check if we need to scale the quantity for better visualization
    // This is needed when the quantity is much lower than revenue/profit
    const maxQuantity = Math.max(...chartData.map(item => item.quantity));
    const maxRevenue = Math.max(...chartData.map(item => item.revenue));
    
    // If quantity is less than 5% of revenue, scale it for better visibility
    if (maxQuantity > 0 && maxRevenue > 0 && maxQuantity < maxRevenue * 0.05) {
      // Scale factor to make quantity approximately 1/3 of max revenue
      const scaleFactor = (maxRevenue / 3) / maxQuantity;
      
      // Apply scaling for display purposes only
      return chartData.map(item => ({
        ...item,
        // Store original quantity in raw_quantity if not already present
        raw_quantity: item.raw_quantity || item.quantity,
        // Use scaled quantity only for display
        quantity: item.quantity * scaleFactor
      }));
    }
    
    return chartData;
  }

  // Reload product data to get the latest values from the data file
  const reloadProductData = async () => {
    setIsLoading(true);
    try {
      await loadProductData();
      toast({
        title: "Product data reloaded",
        description: "The latest product price and cost data has been loaded from the data file.",
      });
    } catch (err) {
      console.error("Error reloading product data:", err);
      setError("Failed to reload product data");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container mx-auto py-4 sm:py-6 md:py-8 px-2 sm:px-4 md:px-6">
      <h1 className="text-2xl sm:text-3xl md:text-4xl font-bold mb-4 sm:mb-6 md:mb-8">Scenario Planner</h1>

      {error && (
        <Alert variant="destructive" className="mb-4 sm:mb-6">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="flex justify-end mb-4">
        <Button variant="outline" onClick={reloadProductData} disabled={isLoading} className="text-xs sm:text-sm">
          Reload Product Data
        </Button>
      </div>

      <div className="grid gap-4 sm:gap-6 grid-cols-1 md:grid-cols-2">
        <Card>
          <CardHeader className="p-4 sm:p-6">
            <CardTitle className="text-lg sm:text-xl">Scenario Parameters</CardTitle>
            <CardDescription className="text-xs sm:text-sm">
              Adjust the parameters to simulate different business scenarios. Our AI will
              predict the quantity that will be sold.
            </CardDescription>
          </CardHeader>
          <CardContent className="p-4 sm:p-6 pt-0 sm:pt-0">
            <div className="grid gap-3 sm:gap-4">
              <div className="grid gap-1 sm:gap-2">
                <Label htmlFor="locationId" className="text-xs sm:text-sm">Location</Label>
                <Select
                  value={simulatedScenario.locationId}
                  onValueChange={(value) => handleSelectChange("locationId", value)}
                  disabled={isLoadingOptions}
                >
                  <SelectTrigger id="locationId" className="text-xs sm:text-sm h-8 sm:h-10">
                    <SelectValue placeholder="Select a location" />
                  </SelectTrigger>
                  <SelectContent>
                    {locations.map((location) => (
                      <SelectItem key={location.id} value={location.id} className="text-xs sm:text-sm">
                        {location.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {simulatedScenario.locationId === 'All' && (
                  <div className="text-[10px] sm:text-xs text-muted-foreground">
                    "All Locations" will simulate using data summed across all regions.
                  </div>
                )}
              </div>

              <div className="grid gap-1 sm:gap-2">
                <Label htmlFor="productId" className="text-xs sm:text-sm">Product</Label>
                <Select
                  value={simulatedScenario.productId}
                  onValueChange={(value) => handleSelectChange("productId", value)}
                  disabled={isLoadingOptions}
                >
                  <SelectTrigger id="productId" className="text-xs sm:text-sm h-8 sm:h-10">
                    <SelectValue placeholder="Select a product" />
                  </SelectTrigger>
                  <SelectContent className="max-h-[40vh]">
                    {products.map((product) => (
                      <SelectItem key={product.id} value={product.id} className="text-xs sm:text-sm">
                        {product.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="grid gap-1 sm:gap-2">
                <Label htmlFor="unitPrice" className="text-xs sm:text-sm">Unit Price ($)</Label>
                <Input
                  id="unitPrice"
                  name="unitPrice"
                  type="number"
                  step="0.01"
                  min="0"
                  value={simulatedScenario.unitPrice.toFixed(2)}
                  onChange={handleInputChange}
                  className="text-xs sm:text-sm h-8 sm:h-10"
                />
                <div className="text-[10px] sm:text-xs text-muted-foreground">
                  Average price for this product: ${averageStats.price.toFixed(2)}
                </div>
              </div>

              <div className="grid gap-1 sm:gap-2">
                <Label htmlFor="unitCost" className="text-xs sm:text-sm">Unit Cost ($)</Label>
                <Input
                  id="unitCost"
                  name="unitCost"
                  type="number"
                  step="0.01"
                  min="0"
                  value={simulatedScenario.unitCost.toFixed(2)}
                  onChange={handleInputChange}
                  className="text-xs sm:text-sm h-8 sm:h-10"
                />
                <div className="text-[10px] sm:text-xs text-muted-foreground">
                  Average cost for this product: ${averageStats.cost.toFixed(2)}
                </div>
              </div>
            </div>
          </CardContent>
          <CardFooter className="flex justify-between p-4 sm:p-6 pt-2 sm:pt-2">
            <Button variant="outline" size="sm" onClick={resetScenario} disabled={isLoading} className="text-xs sm:text-sm h-8 sm:h-10">
              <RotateCcw className="mr-1 sm:mr-2 h-3 sm:h-4 w-3 sm:w-4" />
              Reset
            </Button>
            <Button onClick={simulateRevenue} disabled={isLoading} className="text-xs sm:text-sm h-8 sm:h-10">
              {isLoading ? (
                "Processing..."
              ) : (
                <>
                  Simulate Revenue
                  <ArrowRight className="ml-1 sm:ml-2 h-3 sm:h-4 w-3 sm:w-4" />
                </>
              )}
            </Button>
          </CardFooter>
        </Card>

        <Card>
          <CardHeader className="p-4 sm:p-6">
            <CardTitle className="text-lg sm:text-xl">Prediction Results</CardTitle>
            <CardDescription className="text-xs sm:text-sm">
              Comparison between different pricing scenarios and their impact on quantity,
              revenue, and profit.
            </CardDescription>
          </CardHeader>
          <CardContent className="h-60 sm:h-72 md:h-80">
            <ResponsiveContainer width="100%" height="100%">
              <ChartContainer config={{ theme: { grid: { stroke: "#ddd" } } }}>
                <BarChart 
                  data={getChartData()} 
                  className="mt-2 sm:mt-4 md:mt-6"
                  margin={{
                    top: 5,
                    right: 10,
                    left: 0,
                    bottom: 5,
                  }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="name" 
                    tick={{fontSize: '0.7rem'}}
                    height={40}
                  />
                  <YAxis 
                    tick={{fontSize: '0.7rem'}}
                    width={40}
                    tickFormatter={(value) => `$${value > 999 ? `${(value/1000).toFixed(1)}k` : value}`}
                  />
                  <ChartTooltip
                    formatter={(value, name) => {
                      // Format values with 2 decimal places for currency values
                      if (name === 'Revenue' || name === 'Profit') {
                        return [`$${value.toFixed(2)}`, name];
                      }
                      
                      // For quantity, find the original datapoint to get raw_quantity if available
                      if (name === 'Quantity') {
                        // Get the current chart data
                        const currentData = getChartData();
                        // Find the item with this value or close to it (floating point comparison)
                        const currentItem = currentData.find(item => Math.abs(item.quantity - value) < 0.001);
                        
                        // Use raw_quantity if available, otherwise use the value
                        const actualQuantity = currentItem?.raw_quantity !== undefined ? 
                                              currentItem.raw_quantity : 
                                              value;
                        
                        // Format as integer with comma separation for thousands
                        return [Math.round(actualQuantity).toLocaleString(), name];
                      }
                      
                      // Default case
                      return [value.toLocaleString(), name];
                    }}
                    labelFormatter={(label) => `Scenario: ${label}`}
                  />
                  <Legend 
                    wrapperStyle={{fontSize: '0.7rem'}}
                    iconSize={8}
                    iconType="circle"
                  />
                  <Bar 
                    dataKey="revenue" 
                    fill="#3b82f6" 
                    name="Revenue" 
                    isAnimationActive={true}
                  />
                  <Bar 
                    dataKey="profit" 
                    fill="#22c55e" 
                    name="Profit" 
                    isAnimationActive={true}
                  />
                  <Bar 
                    dataKey="quantity" 
                    fill="#eab308" 
                    name="Quantity" 
                    isAnimationActive={true}
                  />
                </BarChart>
              </ChartContainer>
            </ResponsiveContainer>
          </CardContent>
          {isSimulated && (
            <CardFooter className="flex justify-end p-4 sm:p-6 pt-2 sm:pt-2">
              <Button size="sm" onClick={applyScenario} className="text-xs sm:text-sm h-8 sm:h-10">
                <Check className="mr-1 sm:mr-2 h-3 sm:h-4 w-3 sm:w-4" />
                Apply This Scenario
              </Button>
            </CardFooter>
          )}
        </Card>
      </div>
    </div>
  )
}
