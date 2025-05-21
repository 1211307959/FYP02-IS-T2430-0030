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
import { Upload, FileUp, BarChart, AlertCircle, Check, Database } from "lucide-react"
import { useToast } from "@/components/ui/use-toast"
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert"
import { predictRevenue, getProducts, getCustomers, loadSampleCsvData } from "@/lib/api"
import Papa from 'papaparse'

// Define a type for our CSV row data
type CsvRowData = {
  id?: number;
  OrderDate?: string;
  _CustomerID: number | string;
  _ProductID: number | string;
  "Order Quantity": number;
  "Unit Cost": number;
  "Unit Price": number;
  "Total Cost"?: number;
  "Total Revenue"?: number;
  Profit?: number;
  "Profit Margin (%)"?: number;
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
    orderQuantity: "",
    month: "",
    day: "",
    weekday: "",
    customerId: "",
    productId: "",
  })

  // State for products and customers
  const [products, setProducts] = useState<{id: string, name: string}[]>([])
  const [customers, setCustomers] = useState<{id: string, name: string}[]>([])
  const [isLoadingOptions, setIsLoadingOptions] = useState(true)
  const [error, setError] = useState("")
  const [predictionResults, setPredictionResults] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(false)
  
  // Fetch products and customers from API
  useEffect(() => {
    const fetchOptions = async () => {
      setIsLoadingOptions(true)
      
      try {
        // Fetch products
        const productsData = await getProducts()
        setProducts(productsData)
        
        // Fetch customers
        const customersData = await getCustomers()
        setCustomers(customersData)
      } catch (err) {
        console.error("Error loading options:", err)
        setError("Failed to load product and customer options")
      } finally {
        setIsLoadingOptions(false)
      }
    }
    
    fetchOptions()
  }, [])
  
  // Get month options
  const monthOptions = [
    { value: "1", label: "January" },
    { value: "2", label: "February" },
    { value: "3", label: "March" },
    { value: "4", label: "April" },
    { value: "5", label: "May" },
    { value: "6", label: "June" },
    { value: "7", label: "July" },
    { value: "8", label: "August" },
    { value: "9", label: "September" },
    { value: "10", label: "October" },
    { value: "11", label: "November" },
    { value: "12", label: "December" },
  ]

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

  const handleManualSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    try {
      // Validate all required fields are present
      const requiredFields = ['unitCost', 'unitPrice', 'orderQuantity', 'month', 'day', 'weekday', 'customerId', 'productId']
      const missingFields = requiredFields.filter(field => !formData[field as keyof typeof formData])
      
      if (missingFields.length > 0) {
        throw new Error(`Missing required fields: ${missingFields.join(', ')}`)
      }
      
      // Create new entry for preview data
      const newEntry: CsvRowData = {
      id: previewData.length + 1,
        _CustomerID: formData.customerId,
        _ProductID: formData.productId,
        "Order Quantity": Number(formData.orderQuantity),
        "Unit Cost": Number(formData.unitCost),
        "Unit Price": Number(formData.unitPrice),
        Month: Number(formData.month),
        Day: Number(formData.day),
        Weekday: formData.weekday,
        "Total Cost": Number(formData.unitCost) * Number(formData.orderQuantity),
    }

    setPreviewData([...previewData, newEntry])

    toast({
      title: "Data added successfully",
      description: "Your manual entry has been added to the dataset.",
    })

    // Reset form
    setFormData({
      unitCost: "",
      unitPrice: "",
      orderQuantity: "",
      month: "",
      day: "",
      weekday: "",
      customerId: "",
      productId: "",
    })
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "An unknown error occurred"
      setError(errorMessage)
      toast({
        variant: "destructive",
        title: "Error adding data",
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
      "_CustomerID": typeof row._CustomerID === 'string' ? 
        parseInt(row._CustomerID.replace("CUST", "")) : 
        row._CustomerID,
      "_ProductID": typeof row._ProductID === 'string' ? 
        parseInt(row._ProductID.replace("PROD", "")) : 
        row._ProductID,
      "Order Quantity": row["Order Quantity"],
      "Unit Cost": row["Unit Cost"],
      "Unit Price": row["Unit Price"],
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
      
      // Call the API
      const result = await predictRevenue(orderData)
      
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
        error: function(error) {
          setError(`Error parsing sample CSV: ${error.message}`)
        }
      })
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Failed to load sample data"
      setError(errorMessage)
      toast({
        variant: "destructive",
        title: "Failed to load sample data",
        description: errorMessage,
      })
    }
  }

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
      
    } catch (error) {
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
    <div className="container py-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold tracking-tight">Sales Data Input</h1>
      </div>

      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <Tabs defaultValue="upload" className="space-y-4">
        <TabsList>
          <TabsTrigger value="upload">Upload CSV</TabsTrigger>
          <TabsTrigger value="manual">Manual Input</TabsTrigger>
        </TabsList>

        <TabsContent value="upload" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Upload Sales Data</CardTitle>
              <CardDescription>Upload your CSV file with sales data in the required format.</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid w-full items-center gap-4">
                <div className="flex flex-col items-center justify-center border-2 border-dashed rounded-lg p-12 text-center">
                  <Upload className="h-10 w-10 text-muted-foreground mb-4" />
                  <div className="mb-4 text-sm text-muted-foreground">
                    <span className="font-medium">Click to upload</span> or drag and drop
                  </div>
                  <Input 
                    id="file-upload" 
                    ref={fileInputRef}
                    type="file" 
                    accept=".csv" 
                    className="hidden" 
                    onChange={handleFileChange} 
                  />
                  <div className="flex space-x-2">
                  <Button asChild>
                    <label htmlFor="file-upload" className="cursor-pointer">
                      <FileUp className="mr-2 h-4 w-4" />
                      Select CSV File
                    </label>
                  </Button>
                    <Button variant="outline" onClick={handleLoadSampleData}>
                      <Database className="mr-2 h-4 w-4" />
                      Load Sample Data
                    </Button>
                    {file && (
                      <Button variant="outline" onClick={handleClearFile}>
                        Clear File
                      </Button>
                    )}
                  </div>
                  {file && (
                    <div className="mt-4">
                      <p className="text-sm text-muted-foreground mb-2">Selected file: {file.name}</p>
                      <Button 
                        variant="secondary" 
                        onClick={() => file && handleUploadToServer(file)}
                        disabled={isLoading}
                      >
                        <Upload className="mr-2 h-4 w-4" />
                        Save to Data Directory
                      </Button>
                    </div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="manual" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Manual Data Entry</CardTitle>
              <CardDescription>Enter sales data manually using the form below.</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleManualSubmit} className="grid gap-4 md:grid-cols-2">
                <div className="grid gap-2">
                  <Label htmlFor="unitCost">Unit Cost</Label>
                  <Input
                    id="unitCost"
                    name="unitCost"
                    type="number"
                    step="0.01"
                    placeholder="10.00"
                    value={formData.unitCost}
                    onChange={handleInputChange}
                    required
                  />
                </div>

                <div className="grid gap-2">
                  <Label htmlFor="unitPrice">Unit Price</Label>
                  <Input
                    id="unitPrice"
                    name="unitPrice"
                    type="number"
                    step="0.01"
                    placeholder="25.00"
                    value={formData.unitPrice}
                    onChange={handleInputChange}
                    required
                  />
                </div>

                <div className="grid gap-2">
                  <Label htmlFor="orderQuantity">Order Quantity</Label>
                  <Input
                    id="orderQuantity"
                    name="orderQuantity"
                    type="number"
                    placeholder="100"
                    value={formData.orderQuantity}
                    onChange={handleInputChange}
                    required
                  />
                </div>

                <div className="grid gap-2">
                  <Label htmlFor="month">Month</Label>
                  <Select value={formData.month} onValueChange={(value) => handleSelectChange("month", value)}>
                    <SelectTrigger id="month">
                      <SelectValue placeholder="Select month" />
                    </SelectTrigger>
                    <SelectContent>
                      {monthOptions.map((month) => (
                        <SelectItem key={month.value} value={month.value}>
                          {month.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="grid gap-2">
                  <Label htmlFor="day">Day</Label>
                  <Input
                    id="day"
                    name="day"
                    type="number"
                    min="1"
                    max="31"
                    placeholder="15"
                    value={formData.day}
                    onChange={handleInputChange}
                    required
                  />
                </div>

                <div className="grid gap-2">
                  <Label htmlFor="weekday">Weekday</Label>
                  <Select value={formData.weekday} onValueChange={(value) => handleSelectChange("weekday", value)}>
                    <SelectTrigger id="weekday">
                      <SelectValue placeholder="Select weekday" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Monday">Monday</SelectItem>
                      <SelectItem value="Tuesday">Tuesday</SelectItem>
                      <SelectItem value="Wednesday">Wednesday</SelectItem>
                      <SelectItem value="Thursday">Thursday</SelectItem>
                      <SelectItem value="Friday">Friday</SelectItem>
                      <SelectItem value="Saturday">Saturday</SelectItem>
                      <SelectItem value="Sunday">Sunday</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="grid gap-2">
                  <Label htmlFor="customerId">Location</Label>
                  <Select value={formData.customerId} onValueChange={(value) => handleSelectChange("customerId", value)}>
                    <SelectTrigger id="customerId">
                      <SelectValue placeholder="Select location" />
                    </SelectTrigger>
                    <SelectContent>
                      {customers.map((customer) => (
                        <SelectItem key={customer.id} value={customer.id}>
                          {customer.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="grid gap-2">
                  <Label htmlFor="productId">Product ID</Label>
                  <Select value={formData.productId} onValueChange={(value) => handleSelectChange("productId", value)}>
                    <SelectTrigger id="productId">
                      <SelectValue placeholder="Select product" />
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

                <div className="md:col-span-2">
                  <Button type="submit" className="w-full">
                    Add Entry
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {previewData.length > 0 && (
        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Data Preview</CardTitle>
            <CardDescription>Preview of the data that will be used for prediction. Click on a row to select it for prediction.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="rounded-md border overflow-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-12"></TableHead>
                    <TableHead>Unit Cost</TableHead>
                    <TableHead>Unit Price</TableHead>
                    <TableHead>Quantity</TableHead>
                    <TableHead>Month</TableHead>
                    <TableHead>Day</TableHead>
                    <TableHead>Weekday</TableHead>
                    <TableHead>Location</TableHead>
                    <TableHead>Product ID</TableHead>
                    <TableHead>Predicted Revenue</TableHead>
                    <TableHead>Profit</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {previewData.map((row, index) => (
                    <TableRow 
                      key={row.id} 
                      className={selectedRowIndex === index ? "bg-muted" : ""}
                      onClick={() => handleRowSelect(index)}
                    >
                      <TableCell>
                        {selectedRowIndex === index && <Check className="h-4 w-4 text-green-500" />}
                      </TableCell>
                      <TableCell>${row["Unit Cost"].toFixed(2)}</TableCell>
                      <TableCell>${row["Unit Price"].toFixed(2)}</TableCell>
                      <TableCell>{row["Order Quantity"]}</TableCell>
                      <TableCell>{row.Month}</TableCell>
                      <TableCell>{row.Day}</TableCell>
                      <TableCell>{row.Weekday}</TableCell>
                      <TableCell>{row._CustomerID}</TableCell>
                      <TableCell>{row._ProductID}</TableCell>
                      <TableCell>
                        {row["Total Revenue"] ? 
                          `$${row["Total Revenue"].toFixed(2)}` : 
                          "-"}
                      </TableCell>
                      <TableCell>
                        {row["Profit"] ? 
                          `$${row["Profit"].toFixed(2)}` : 
                          "-"}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </CardContent>
          <CardFooter className="flex justify-between">
            <Button variant="outline" onClick={handleClearFile}>
              Clear Data
            </Button>
            <Button 
              onClick={handlePredictRevenue} 
              disabled={isLoading || previewData.length === 0}
            >
              <BarChart className="mr-2 h-4 w-4" />
              {isLoading ? "Predicting..." : "Predict Revenue"}
            </Button>
          </CardFooter>
        </Card>
      )}

      {predictionResults && (
        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Prediction Results</CardTitle>
            <CardDescription>Revenue prediction based on the selected data</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              <div className="rounded-lg border p-4">
                <h3 className="text-lg font-semibold mb-1">Predicted Revenue</h3>
                <p className="text-2xl font-bold text-green-600">
                  ${predictionResults.predicted_revenue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </p>
              </div>
              <div className="rounded-lg border p-4">
                <h3 className="text-lg font-semibold mb-1">Predicted Profit</h3>
                <p className="text-2xl font-bold text-blue-600">
                  ${predictionResults.profit.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </p>
              </div>
            </div>
            
            {predictionResults.profit < 0 && (
              <Alert variant="destructive" className="mt-4">
                <AlertCircle className="h-4 w-4" />
                <AlertTitle>Warning</AlertTitle>
                <AlertDescription>
                  This transaction is predicted to result in a loss. Consider adjusting the price or quantity.
                </AlertDescription>
              </Alert>
            )}
            
            {predictionResults.profit > 0 && 
              (predictionResults.profit / predictionResults.predicted_revenue) < 0.1 && (
              <Alert className="mt-4 border-amber-500 text-amber-500">
                <AlertCircle className="h-4 w-4" />
                <AlertTitle>Low Profit Margin</AlertTitle>
                <AlertDescription>
                  This transaction has a profit margin below 10%. Consider strategies to increase margins.
                </AlertDescription>
              </Alert>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
