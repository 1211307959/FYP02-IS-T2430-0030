"use client"

import type React from "react"

import { useState, useEffect, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Upload, FileUp, BarChart, AlertCircle, Check, Database, Calendar } from "lucide-react"
import { useToast } from "@/components/ui/use-toast"
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert"
import { getProducts, getLocations, loadSampleCsvData } from "@/lib/api"
import Papa from 'papaparse'
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { cn } from "@/lib/utils"
import { format } from "date-fns"

// Define a type for our CSV row data
type CsvRowData = {
  id?: number;
  Location: string;
  _ProductID: number | string;
  "Unit Cost": number;
  "Unit Price": number;
  "Total Revenue": number;
  Year?: number;
  Month: number;
  Day: number;
  Weekday: string;
  [key: string]: any;
}

export default function DataInputPage() {
  const { toast } = useToast()
  const [file, setFile] = useState<File | null>(null)
  const [previewData, setPreviewData] = useState<CsvRowData[]>([])
  const [selectedRowIndex, setSelectedRowIndex] = useState<number | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [formData, setFormData] = useState({
    unitCost: "",
    unitPrice: "",
    totalRevenue: "",
    date: undefined as Date | undefined,
    location: "",
    productId: "",
  })

  // State for products and locations
  const [products, setProducts] = useState<{id: string, name: string}[]>([])
  const [locations, setLocations] = useState<{id: string, name: string}[]>([])
  const [isLoadingOptions, setIsLoadingOptions] = useState(true)
  const [isCustomProduct, setIsCustomProduct] = useState(false)
  const [isCustomLocation, setIsCustomLocation] = useState(false)
  const [error, setError] = useState("")
  const [predictionResults, setPredictionResults] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(false)
  
  // Fetch products and locations from API
  useEffect(() => {
    const fetchOptions = async () => {
      setIsLoadingOptions(true)
      
      try {
        // Fetch products
        const productsData = await getProducts()
        setProducts(productsData)
        
        // Fetch locations and filter out "All Locations" for manual entry
        const locationsData = await getLocations()
        const filteredLocations = locationsData.filter((location: {id: string, name: string}) => location.id !== 'All')
        setLocations(filteredLocations)
      } catch (err) {
        console.error("Error loading options:", err)
        setError("Failed to load product and location options")
      } finally {
        setIsLoadingOptions(false)
      }
    }
    
    fetchOptions()
  }, [])
  
  // Helper function to get date components
  const getDateComponents = (date: Date) => {
    const weekdays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    return {
      year: date.getFullYear(),
      month: date.getMonth() + 1, // getMonth() returns 0-11
      day: date.getDate(),
      weekday: weekdays[date.getDay()]
    }
  }

  // Handle parsing CSV file with Papa Parse
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (!selectedFile) return
    
      setFile(selectedFile)
    setError("")
    
    Papa.parse(selectedFile, {
      header: true,
      skipEmptyLines: true,
      dynamicTyping: true, // Automatically convert numbers
      complete: function(results) {
        if (results.errors.length > 0) {
          setError(`Error parsing CSV: ${results.errors[0].message}`)
          return
        }
        
        // Add ID to each row for tracking
        const dataWithIds = results.data.map((row: any, index: number) => ({ 
          ...row,
          id: index + 1 
        }))
        
        setPreviewData(dataWithIds as CsvRowData[])

      toast({
        title: "File uploaded successfully",
          description: `${selectedFile.name} has been uploaded with ${dataWithIds.length} rows.`,
        })
      },
      error: function(error) {
        setError(`Error parsing CSV: ${error.message}`)
        toast({
          variant: "destructive",
          title: "Upload failed",
          description: `Error parsing CSV: ${error.message}`,
      })
    }
    })
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  const handleSelectChange = (name: string, value: string) => {
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  const handleManualSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    try {
      // Validate all required fields are present
      const requiredFields = ['unitCost', 'unitPrice', 'totalRevenue', 'date', 'location', 'productId']
      const missingFields = requiredFields.filter(field => {
        if (field === 'date') return !formData.date
        return !formData[field as keyof typeof formData]
      })
      
      if (missingFields.length > 0) {
        throw new Error(`Missing required fields: ${missingFields.join(', ')}`)
      }
      
      // Extract date components from the selected date
      const dateComponents = getDateComponents(formData.date!)
      
      // Prepare data for API call (matching the expected backend format)
      const apiData = {
        location: formData.location,
        _ProductID: formData.productId,
        unit_cost: Number(formData.unitCost),
        unit_price: Number(formData.unitPrice),
        total_revenue: Number(formData.totalRevenue),
        year: dateComponents.year,
        month: dateComponents.month,
        day: dateComponents.day,
        weekday: dateComponents.weekday,
      }
      
      // Call the manual entry API endpoint
      const response = await fetch('/api/manual-entry', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(apiData)
      })
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || `API call failed: ${response.statusText}`)
      }
      
      const result = await response.json()
      
      // Create new entry for preview data (using the frontend display format)
      const newEntry: CsvRowData = {
        id: previewData.length + 1,
        Location: formData.location,
        _ProductID: formData.productId,
        "Unit Cost": Number(formData.unitCost),
        "Unit Price": Number(formData.unitPrice),
        "Total Revenue": Number(formData.totalRevenue),
        Year: dateComponents.year,
        Month: dateComponents.month,
        Day: dateComponents.day,
        Weekday: dateComponents.weekday,
      }

      setPreviewData([...previewData, newEntry])

      toast({
        title: "Data saved successfully",
        description: `Manual entry has been saved to server: ${result.filename}`,
      })

      // Reset form
      setFormData({
        unitCost: "",
        unitPrice: "",
        totalRevenue: "",
        date: undefined,
        location: "",
        productId: "",
      })
      
      // Reset custom input states
      setIsCustomProduct(false)
      setIsCustomLocation(false)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "An unknown error occurred"
      setError(errorMessage)
      toast({
        variant: "destructive",
        title: "Error saving data",
        description: errorMessage,
      })
    }
  }

  // Handle row selection
  const handleRowSelect = (index: number) => {
    setSelectedRowIndex(index === selectedRowIndex ? null : index)
  }

  // Format data for API prediction
  const formatRowForPrediction = (row: CsvRowData) => {
    // The API expects specific field names
    return {
      "Location": row.Location,
      "_ProductID": typeof row._ProductID === 'string' ? 
        parseInt(row._ProductID.replace("PROD", "")) : 
        row._ProductID,
      "Unit Cost": row["Unit Cost"],
      "Unit Price": row["Unit Price"],
      "Year": row.Year || new Date().getFullYear(),
      "Month": row.Month,
      "Day": row.Day,
      "Weekday": row.Weekday
    }
  }

  const handlePredictRevenue = async () => {
    if (previewData.length === 0) {
      toast({
        variant: "destructive",
        title: "No data to predict",
        description: "Please add at least one entry before predicting revenue.",
      })
      return
    }
    
    setIsLoading(true)
    setError("")
    
    try {
      // Get the selected row or use the last entry
      const rowIndex = selectedRowIndex !== null ? selectedRowIndex : previewData.length - 1
      const selectedRow = previewData[rowIndex]
      
      // Format the data for the API
      const orderData = formatRowForPrediction(selectedRow)
      
      // Call the prediction API
      const response = await fetch('/api/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(orderData)
      });
      
      if (!response.ok) {
        throw new Error(`Prediction failed: ${response.statusText}`);
      }
      
      const result = await response.json();
      
      // Store the prediction results
      setPredictionResults(result)
      
      // Update the preview data with predicted values
      const updatedPreviewData = [...previewData]
      updatedPreviewData[rowIndex] = {
        ...updatedPreviewData[rowIndex],
        "Total Revenue": result.predicted_revenue,
        "Profit": result.profit
      }
      setPreviewData(updatedPreviewData)
      
      toast({
        title: "Prediction complete",
        description: `Predicted Revenue: $${result.predicted_revenue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
      })
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "An unknown error occurred"
      setError(errorMessage)
      toast({
        variant: "destructive",
        title: "Prediction failed",
        description: errorMessage,
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleClearFile = () => {
    setFile(null)
    setPreviewData([])
    setSelectedRowIndex(null)
    setPredictionResults(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ""
    }
  }

  // Add this function to load sample data
  const handleLoadSampleData = async () => {
    setError("")
    
    try {
      const csvText = await loadSampleCsvData()
      
      Papa.parse(csvText, {
        header: true,
        skipEmptyLines: true,
        dynamicTyping: true,
        complete: function(results) {
          if (results.errors.length > 0) {
            setError(`Error parsing sample CSV: ${results.errors[0].message}`)
            return
          }
          
          // Take only first 20 rows to avoid performance issues
          const limitedData = results.data.slice(0, 20)
          
          // Add ID to each row for tracking
          const dataWithIds = limitedData.map((row: any, index: number) => ({ 
            ...row,
            id: index + 1 
          }))
          
          setPreviewData(dataWithIds as CsvRowData[])
          setFile(null)
          
          toast({
            title: "Sample data loaded",
            description: `Loaded ${dataWithIds.length} rows from sample data.`,
          })
        },
        error: function(error: any) {
          setError(`Error parsing sample CSV: ${error.message}`)
        }
      })
    } catch (error: any) {
      const errorMessage = error instanceof Error ? error.message : "Failed to load sample data"
      setError(errorMessage)
      toast({
        variant: "destructive",
        title: "Failed to load sample data",
        description: errorMessage,
      })
    }
  }

  // Add function to reload data
  const handleReloadData = async () => {
    setIsLoading(true);
    setError("");
    
    try {
      const response = await fetch('/api/reload-data', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`Failed to reload data: ${response.statusText}`);
      }
      
      const result = await response.json();
      
      toast({
        title: "Data reloaded successfully",
        description: `Loaded ${result.files_loaded} files with ${result.total_rows} total rows.`,
      });
      
      // Clear current preview data to show that new data is loaded
      setPreviewData([]);
      setSelectedRowIndex(null);
      setPredictionResults(null);
      
    } catch (error: any) {
      const errorMessage = error instanceof Error ? error.message : "Failed to reload data";
      setError(errorMessage);
      toast({
        variant: "destructive",
        title: "Failed to reload data",
        description: errorMessage,
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Add this function after the handleClearFile function and before the return statement
  const handleUploadToServer = async (file: File) => {
    setIsLoading(true)
    setError("")
    
    try {
      // Create a FormData object
      const formData = new FormData()
      formData.append('file', file)
      
      // Make a POST request to upload the file
      const response = await fetch('/api/upload-csv', {
        method: 'POST',
        body: formData,
      })
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Failed to upload file to server')
      }
      
      const result = await response.json()
      
    toast({
        title: "File uploaded to server",
        description: `${file.name} has been uploaded to the data directory and is now available for analysis.`,
    })

      // Clear the file input after successful upload
      if (fileInputRef.current) {
        fileInputRef.current.value = ""
      }
      
    } catch (error: any) {
      const errorMessage = error instanceof Error ? error.message : "Failed to upload file to server"
      setError(errorMessage)
      toast({
        variant: "destructive",
        title: "Upload failed",
        description: errorMessage,
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="container py-4 sm:py-6 md:py-8 px-2 sm:px-4 md:px-6">
      <h1 className="text-2xl sm:text-3xl md:text-4xl font-bold mb-4 sm:mb-6">Data Input</h1>

      {error && (
        <Alert variant="destructive" className="mb-4 sm:mb-6">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <Tabs defaultValue="file-upload" className="space-y-4 sm:space-y-6">
        <TabsList className="flex flex-wrap">
          <TabsTrigger className="flex-grow text-xs sm:text-sm" value="file-upload">
            <Upload className="mr-2 h-4 w-4" />
            File Upload
          </TabsTrigger>
          <TabsTrigger className="flex-grow text-xs sm:text-sm" value="manual-entry">
            <FileUp className="mr-2 h-4 w-4" />
            Manual Entry
          </TabsTrigger>
        </TabsList>

        <TabsContent value="file-upload" className="space-y-4">
          <Card>
            <CardHeader className="p-4 sm:p-6">
              <CardTitle className="text-lg sm:text-xl">Upload Data File</CardTitle>
              <CardDescription className="text-xs sm:text-sm">
                Upload a CSV file with your sales data for analysis.
              </CardDescription>
            </CardHeader>
            <CardContent className="p-4 sm:p-6 pt-0 sm:pt-0">
              <div className="grid gap-4">
                <div className="flex flex-col sm:flex-row gap-4">
                  <div className="flex-1">
                    <Label htmlFor="file-upload" className="text-xs sm:text-sm">Select CSV File</Label>
                  <Input 
                    id="file-upload" 
                    type="file" 
                    accept=".csv" 
                      ref={fileInputRef}
                    onChange={handleFileChange} 
                      className="mt-1 text-xs sm:text-sm h-9 sm:h-10"
                    />
                  </div>
                  <div className="flex flex-row gap-2 items-end">
                    <Button
                      variant="outline"
                      size="sm"
                      type="button"
                      onClick={handleClearFile}
                      className="text-xs sm:text-sm h-9 sm:h-10"
                      disabled={!file}
                    >
                      Clear File
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      type="button"
                      onClick={handleLoadSampleData}
                      className="text-xs sm:text-sm h-9 sm:h-10"
                    >
                      <Database className="mr-1 sm:mr-2 h-3 sm:h-4 w-3 sm:w-4" />
                      Load Sample
                      </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      type="button"
                      onClick={handleReloadData}
                      className="text-xs sm:text-sm h-9 sm:h-10"
                      disabled={isLoading}
                    >
                      {isLoading ? "Reloading..." : "Reload Data"}
                    </Button>
                  </div>
                </div>

                  {file && (
                  <div className="mt-2">
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <Check className="h-4 w-4 text-green-500" />
                      <span>
                        {file.name} ({(file.size / 1024).toFixed(1)} KB)
                      </span>
                    </div>
                    </div>
                  )}
              </div>
            </CardContent>
            <CardFooter className="p-4 sm:p-6 flex flex-col sm:flex-row justify-end gap-2">
              <Button
                type="button"
                disabled={!file}
                onClick={() => file && handleUploadToServer(file)}
                className="w-full sm:w-auto text-xs sm:text-sm"
              >
                Process File
              </Button>
            </CardFooter>
          </Card>

          {previewData.length > 0 && (
            <Card>
              <CardHeader className="p-4 sm:p-6">
                <CardTitle className="text-lg sm:text-xl">Data Preview</CardTitle>
                <CardDescription className="text-xs sm:text-sm">
                  Preview of the uploaded data. Click on a row to select it for prediction.
                </CardDescription>
              </CardHeader>
              <CardContent className="p-0">
                <div className="overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead className="w-12 text-xs">ID</TableHead>
                        <TableHead className="text-xs">Product</TableHead>
                        <TableHead className="text-xs">Customer</TableHead>
                        <TableHead className="text-xs">Unit Price</TableHead>
                        <TableHead className="text-xs">Unit Cost</TableHead>
                        <TableHead className="text-xs">Quantity</TableHead>
                        <TableHead className="text-xs">Date</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {previewData.slice(0, 10).map((row, index) => (
                        <TableRow
                          key={row.id}
                          className={selectedRowIndex === index ? "bg-muted" : ""}
                          onClick={() => handleRowSelect(index)}
                        >
                          <TableCell className="text-xs font-medium">{row.id}</TableCell>
                          <TableCell className="text-xs">{row._ProductID}</TableCell>
                          <TableCell className="text-xs">{row._CustomerID}</TableCell>
                          <TableCell className="text-xs">${row["Unit Price"]}</TableCell>
                          <TableCell className="text-xs">${row["Unit Cost"]}</TableCell>
                          <TableCell className="text-xs">{row["Order Quantity"]}</TableCell>
                          <TableCell className="text-xs">{`${row.Month}/${row.Day} (${row.Weekday})`}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
                {previewData.length > 10 && (
                  <div className="p-4 text-center text-xs text-muted-foreground">
                    Showing 10 of {previewData.length} rows
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="manual-entry">
          <Card>
            <CardHeader className="p-4 sm:p-6">
              <CardTitle className="text-lg sm:text-xl">Manual Data Entry</CardTitle>
              <CardDescription className="text-xs sm:text-sm">
                Enter sales data manually for individual transactions.
              </CardDescription>
            </CardHeader>
            <form onSubmit={handleManualSubmit}>
              <CardContent className="p-4 sm:p-6 pt-0 sm:pt-0">
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-x-4 gap-y-3">
                  <div className="grid gap-1 sm:gap-2">
                    <Label htmlFor="productId" className="text-xs sm:text-sm">Product</Label>
                    {isCustomProduct ? (
                      <div className="flex gap-2">
                        <Input
                          id="productId"
                          name="productId"
                          value={formData.productId}
                          onChange={handleInputChange}
                          placeholder="Enter new product name"
                          className="text-xs sm:text-sm h-8 sm:h-10 flex-1"
                        />
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          onClick={() => {
                            setIsCustomProduct(false)
                            setFormData(prev => ({ ...prev, productId: "" }))
                          }}
                          className="h-8 sm:h-10 px-2"
                        >
                          ↩
                        </Button>
                      </div>
                    ) : (
                      <div className="flex gap-2">
                        <Select
                          value={formData.productId}
                          onValueChange={(value) => handleSelectChange("productId", value)}
                          disabled={isLoadingOptions}
                        >
                          <SelectTrigger id="productId" className="text-xs sm:text-sm h-8 sm:h-10 flex-1">
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
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          onClick={() => setIsCustomProduct(true)}
                          className="h-8 sm:h-10 px-2"
                        >
                          +
                        </Button>
                      </div>
                    )}
                  </div>

                  <div className="grid gap-1 sm:gap-2">
                    <Label htmlFor="location" className="text-xs sm:text-sm">Location</Label>
                    {isCustomLocation ? (
                      <div className="flex gap-2">
                        <Input
                          id="location"
                          name="location"
                          value={formData.location}
                          onChange={handleInputChange}
                          placeholder="Enter new location name"
                          className="text-xs sm:text-sm h-8 sm:h-10 flex-1"
                        />
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          onClick={() => {
                            setIsCustomLocation(false)
                            setFormData(prev => ({ ...prev, location: "" }))
                          }}
                          className="h-8 sm:h-10 px-2"
                        >
                          ↩
                        </Button>
                      </div>
                    ) : (
                      <div className="flex gap-2">
                        <Select
                          value={formData.location}
                          onValueChange={(value) => handleSelectChange("location", value)}
                          disabled={isLoadingOptions}
                        >
                          <SelectTrigger id="location" className="text-xs sm:text-sm h-8 sm:h-10 flex-1">
                            <SelectValue placeholder="Select a location" />
                          </SelectTrigger>
                          <SelectContent className="max-h-[40vh]">
                            {locations.map((location) => (
                              <SelectItem key={location.id} value={location.id} className="text-xs sm:text-sm">
                                {location.name}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          onClick={() => setIsCustomLocation(true)}
                          className="h-8 sm:h-10 px-2"
                        >
                          +
                        </Button>
                      </div>
                    )}
                  </div>

                  <div className="grid gap-1 sm:gap-2">
                    <Label htmlFor="unitPrice" className="text-xs sm:text-sm">Unit Price ($)</Label>
                  <Input
                    id="unitPrice"
                    name="unitPrice"
                    type="number"
                    step="0.01"
                      min="0"
                    value={formData.unitPrice}
                    onChange={handleInputChange}
                      className="text-xs sm:text-sm h-8 sm:h-10"
                    />
                  </div>

                  <div className="grid gap-1 sm:gap-2">
                    <Label htmlFor="unitCost" className="text-xs sm:text-sm">Unit Cost ($)</Label>
                    <Input
                      id="unitCost"
                      name="unitCost"
                      type="number"
                      step="0.01"
                      min="0"
                      value={formData.unitCost}
                      onChange={handleInputChange}
                      className="text-xs sm:text-sm h-8 sm:h-10"
                  />
                </div>

                  <div className="grid gap-1 sm:gap-2">
                    <Label htmlFor="totalRevenue" className="text-xs sm:text-sm">Total Revenue ($)</Label>
                  <Input
                    id="totalRevenue"
                    name="totalRevenue"
                    type="number"
                      min="0"
                      step="0.01"
                    value={formData.totalRevenue}
                    onChange={handleInputChange}
                      className="text-xs sm:text-sm h-8 sm:h-10"
                  />
                </div>

                  <div className="grid gap-1 sm:gap-2">
                    <Label htmlFor="date" className="text-xs sm:text-sm">Date</Label>
                    <Popover>
                      <PopoverTrigger asChild>
                        <Button
                          variant="outline"
                          className={cn(
                            "w-full justify-start text-left font-normal text-xs sm:text-sm h-8 sm:h-10",
                            !formData.date && "text-muted-foreground"
                          )}
                        >
                          <Calendar className="mr-2 h-4 w-4" />
                          {formData.date ? format(formData.date, "PPP") : "Pick a date"}
                        </Button>
                      </PopoverTrigger>
                      <PopoverContent className="w-auto p-0" align="start">
                        <input
                          type="date"
                          value={formData.date ? format(formData.date, "yyyy-MM-dd") : ""}
                          onChange={(e) => {
                            const date = e.target.value ? new Date(e.target.value) : undefined
                            setFormData(prev => ({ ...prev, date }))
                          }}
                          className="w-full p-3 border-0 outline-none"
                        />
                      </PopoverContent>
                    </Popover>
                  </div>
                </div>
              </CardContent>
              <CardFooter className="p-4 sm:p-6 flex justify-end">
                <Button type="submit" className="w-full sm:w-auto text-xs sm:text-sm">Add Entry</Button>
              </CardFooter>
              </form>
          </Card>
        </TabsContent>


      </Tabs>
    </div>
  )
}
