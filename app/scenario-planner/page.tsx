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

  // Initial scenario data
  const initialScenario = {
    locationId: "North",
    productId: "12", // Use numeric ID directly as string
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
        productMap[product.productId.toString()] = {
          price: product.price,
          cost: product.cost
        };
      });
      
      setProductAverages(productMap);
      
      // If we have a selected product, update its price and cost
      if (simulatedScenario.productId && productMap[simulatedScenario.productId]) {
        const selectedProductData = productMap[simulatedScenario.productId];
        
        setSimulatedScenario(prev => ({
          ...prev,
          unitPrice: selectedProductData.price,
          unitCost: selectedProductData.cost
        }));
        
        setAverageStats({
          price: selectedProductData.price,
          cost: selectedProductData.cost
        });
      }
      // If no product is selected but we have product data, use the first one
      else if (productData.length > 0) {
        const firstProductId = productData[0].productId.toString();
        const updatedScenario = {
          ...simulatedScenario, 
          productId: firstProductId,
          unitCost: productMap[firstProductId].cost,
          unitPrice: productMap[firstProductId].price
        };
        
        setOriginalScenario(updatedScenario);
        setSimulatedScenario(updatedScenario);
        
        setAverageStats({
          price: productMap[firstProductId].price,
          cost: productMap[firstProductId].cost
        });
      }
      
      toast({
        title: "Product data loaded",
        description: `Loaded data from ${response.source || "data file"}`,
      });
      
    } catch (err) {
      console.error("Error loading product data:", err);
      setError("Failed to load product price data");
      
      toast({
        variant: "destructive",
        title: "Error loading product data",
        description: "Failed to load product price and cost data from the file.",
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch products and locations from API
  useEffect(() => {
    const fetchOptions = async () => {
      setIsLoadingOptions(true)
      
      try {
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
        
        // Load product price and cost data
        await loadProductData();
      } catch (err) {
        console.error("Error loading options:", err)
        setError("Failed to load product and location options")
      } finally {
        setIsLoadingOptions(false)
      }
    }
    
    fetchOptions()
  }, [])

  // Handle input changes
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setSimulatedScenario((prev) => ({
      ...prev,
      [name]: Number.parseFloat(value) || 0,
    }))
  }

  // Handle select changes
  const handleSelectChange = (name: string, value: string) => {
    let updateObj: any = { [name]: value };
    
    // If product changes, update price and cost to match product average
    if (name === 'productId' && productAverages[value]) {
      updateObj.unitPrice = productAverages[value].price;
      updateObj.unitCost = productAverages[value].cost;
      
      // Also update average stats
      setAverageStats({
        price: productAverages[value].price,
        cost: productAverages[value].cost
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
      // Map the frontend data structure to the format expected by the API
      const baseData = mapToApiOrderFormat(simulatedScenario)
      
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
        
        toast({
          title: "Scenarios simulated",
          description: "The quantity and revenue predictions have been updated based on your changes.",
        });
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
      unitPrice: productAvg ? productAvg.price : 0,
      unitCost: productAvg ? productAvg.cost : 0
    };
    
    setSimulatedScenario(resetScenario);
    setIsSimulated(false);
    setScenarioResults([]);
    setError("");

    // Update average stats
    if (productAvg) {
      setAverageStats({
        price: productAvg.price,
        cost: productAvg.cost
      });
    }

    toast({
      title: "Scenario reset",
      description: "Values have been reset to the product's average price and cost.",
    });
  }

  // Apply the simulated scenario
  const applyScenario = () => {
    toast({
      title: "Scenario applied",
      description: "The simulated scenario has been applied as the new baseline.",
    })
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
          quantity: 0
        }
      ]
    }
    // Map backend keys to frontend keys
    return safeResults.map(result => ({
      name: result.Scenario || result.scenario,
      revenue: result["Predicted Revenue"] ?? result.predicted_revenue ?? 0,
      profit: result.Profit ?? result.profit ?? 0,
      quantity: result["Predicted Quantity"] ?? result.predicted_quantity ?? 0
    }))
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
    <div className="container mx-auto py-8">
      <h1 className="text-4xl font-bold mb-8">Scenario Planner</h1>

      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="flex justify-end mb-4">
        <Button variant="outline" onClick={reloadProductData} disabled={isLoading}>
          Reload Product Data
        </Button>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Scenario Parameters</CardTitle>
            <CardDescription>
              Adjust the parameters to simulate different business scenarios. Our AI will
              predict the quantity that will be sold.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4">
              <div className="grid gap-2">
                <Label htmlFor="locationId">Location</Label>
                <Select
                  value={simulatedScenario.locationId}
                  onValueChange={(value) => handleSelectChange("locationId", value)}
                  disabled={isLoadingOptions}
                >
                  <SelectTrigger id="locationId">
                    <SelectValue placeholder="Select a location" />
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

              <div className="grid gap-2">
                <Label htmlFor="productId">Product</Label>
                <Select
                  value={simulatedScenario.productId}
                  onValueChange={(value) => handleSelectChange("productId", value)}
                  disabled={isLoadingOptions}
                >
                  <SelectTrigger id="productId">
                    <SelectValue placeholder="Select a product" />
                  </SelectTrigger>
                  <SelectContent>
                    {products.map((product) => (
                      <SelectItem key={product.id} value={product.id}>
                        {product.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="grid gap-2">
                <Label htmlFor="unitPrice">Unit Price ($)</Label>
                <Input
                  id="unitPrice"
                  name="unitPrice"
                  type="number"
                  step="0.01"
                  min="0"
                  value={simulatedScenario.unitPrice}
                  onChange={handleInputChange}
                />
                <div className="text-xs text-muted-foreground">
                  Average price for this product: ${averageStats.price.toFixed(2)}
                </div>
              </div>

              <div className="grid gap-2">
                <Label htmlFor="unitCost">Unit Cost ($)</Label>
                <Input
                  id="unitCost"
                  name="unitCost"
                  type="number"
                  step="0.01"
                  min="0"
                  value={simulatedScenario.unitCost}
                  onChange={handleInputChange}
                />
                <div className="text-xs text-muted-foreground">
                  Average cost for this product: ${averageStats.cost.toFixed(2)}
                </div>
              </div>
            </div>
          </CardContent>
          <CardFooter className="flex justify-between">
            <Button variant="outline" size="sm" onClick={resetScenario} disabled={isLoading}>
              <RotateCcw className="mr-2 h-4 w-4" />
              Reset
            </Button>
            <Button onClick={simulateRevenue} disabled={isLoading}>
              {isLoading ? (
                "Processing..."
              ) : (
                <>
                  Simulate Revenue
                  <ArrowRight className="ml-2 h-4 w-4" />
                </>
              )}
            </Button>
          </CardFooter>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Prediction Results</CardTitle>
            <CardDescription>
              Comparison between different pricing scenarios and their impact on quantity,
              revenue, and profit.
            </CardDescription>
          </CardHeader>
          <CardContent className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <ChartContainer config={{ theme: { grid: { stroke: "#ddd" } } }}>
                <BarChart data={getChartData()} className="mt-6">
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <ChartTooltip
                    content={({ active, payload }) => {
                      if (active && payload && payload.length) {
                        return (
                          <ChartTooltipContent
                            content={
                              <div className="grid gap-2">
                                <div className="flex items-center gap-2">
                                  <div className="bg-blue-500 rounded-full w-3 h-3" />
                                  <div className="grid gap-1">
                                    <div className="text-xs">Revenue</div>
                                    <div>${payload[0].value?.toFixed(2)}</div>
                                  </div>
                                </div>
                                <div className="flex items-center gap-2">
                                  <div className="bg-green-500 rounded-full w-3 h-3" />
                                  <div className="grid gap-1">
                                    <div className="text-xs">Profit</div>
                                    <div>${payload[1].value?.toFixed(2)}</div>
                                  </div>
                                </div>
                                <div className="flex items-center gap-2">
                                  <div className="bg-amber-500 rounded-full w-3 h-3" />
                                  <div className="grid gap-1">
                                    <div className="text-xs">Quantity</div>
                                    <div>{payload[2].value}</div>
                                  </div>
                                </div>
                              </div>
                            }
                          />
                        )
                      }
                      return null
                    }}
                  />
                  <Legend />
                  <Bar dataKey="revenue" fill="#3b82f6" name="Revenue" />
                  <Bar dataKey="profit" fill="#22c55e" name="Profit" />
                  <Bar dataKey="quantity" fill="#eab308" name="Quantity" />
                </BarChart>
              </ChartContainer>
            </ResponsiveContainer>
          </CardContent>
          {isSimulated && (
            <CardFooter className="flex justify-end">
              <Button size="sm" onClick={applyScenario}>
                <Check className="mr-2 h-4 w-4" />
                Apply This Scenario
              </Button>
            </CardFooter>
          )}
        </Card>
      </div>
    </div>
  )
}
