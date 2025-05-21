"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Checkbox } from "@/components/ui/checkbox"
import { Label } from "@/components/ui/label"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { FileText, Download, Calendar, Tag, Users, Filter } from "lucide-react"
import { useToast } from "@/components/ui/use-toast"

export default function ReportsPage() {
  const { toast } = useToast()
  const [month, setMonth] = useState<string>("")
  const [product, setProduct] = useState<string>("")
  const [customer, setCustomer] = useState<string>("")
  const [reportType, setReportType] = useState<string>("sales")

  // Report sections to include
  const [includeSections, setIncludeSections] = useState({
    salesTrends: true,
    profitMargins: true,
    predictions: true,
    customerAnalysis: false,
    productPerformance: false,
  })

  const handleSectionChange = (section: string, checked: boolean) => {
    setIncludeSections((prev) => ({
      ...prev,
      [section]: checked,
    }))
  }

  const handleGenerateReport = () => {
    toast({
      title: "Generating report",
      description: "Your report is being generated and will be ready to download shortly.",
    })

    // Simulate report generation delay
    setTimeout(() => {
      toast({
        title: "Report ready",
        description: "Your report has been generated and is ready to download.",
      })
    }, 2000)
  }

  return (
    <div className="container py-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold tracking-tight">Report Generator</h1>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        <div className="md:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle>Report Options</CardTitle>
              <CardDescription>Configure the parameters for your report.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="reportType">Report Type</Label>
                <Select value={reportType} onValueChange={setReportType}>
                  <SelectTrigger id="reportType">
                    <SelectValue placeholder="Select report type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="sales">Sales Report</SelectItem>
                    <SelectItem value="profit">Profit Analysis</SelectItem>
                    <SelectItem value="forecast">Revenue Forecast</SelectItem>
                    <SelectItem value="customer">Customer Analysis</SelectItem>
                    <SelectItem value="product">Product Performance</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="month">Month Filter</Label>
                <Select value={month} onValueChange={setMonth}>
                  <SelectTrigger id="month">
                    <SelectValue placeholder="All months" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">All months</SelectItem>
                    <SelectItem value="january">January</SelectItem>
                    <SelectItem value="february">February</SelectItem>
                    <SelectItem value="march">March</SelectItem>
                    <SelectItem value="april">April</SelectItem>
                    <SelectItem value="may">May</SelectItem>
                    <SelectItem value="june">June</SelectItem>
                    <SelectItem value="july">July</SelectItem>
                    <SelectItem value="august">August</SelectItem>
                    <SelectItem value="september">September</SelectItem>
                    <SelectItem value="october">October</SelectItem>
                    <SelectItem value="november">November</SelectItem>
                    <SelectItem value="december">December</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="product">Product Filter</Label>
                <Select value={product} onValueChange={setProduct}>
                  <SelectTrigger id="product">
                    <SelectValue placeholder="All products" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">All products</SelectItem>
                    <SelectItem value="prod001">Premium Widget</SelectItem>
                    <SelectItem value="prod002">Deluxe Gadget</SelectItem>
                    <SelectItem value="prod003">Super Tool</SelectItem>
                    <SelectItem value="prod004">Ultra Device</SelectItem>
                    <SelectItem value="prod005">Mega Product</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="customer">Customer Filter</Label>
                <Select value={customer} onValueChange={setCustomer}>
                  <SelectTrigger id="customer">
                    <SelectValue placeholder="All customers" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">All customers</SelectItem>
                    <SelectItem value="cust001">Acme Corp</SelectItem>
                    <SelectItem value="cust002">Globex Inc</SelectItem>
                    <SelectItem value="cust003">Initech</SelectItem>
                    <SelectItem value="cust004">Umbrella Corp</SelectItem>
                    <SelectItem value="cust005">Stark Industries</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>

          <Card className="mt-6">
            <CardHeader>
              <CardTitle>Report Sections</CardTitle>
              <CardDescription>Select which sections to include in your report.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="salesTrends"
                  checked={includeSections.salesTrends}
                  onCheckedChange={(checked) => handleSectionChange("salesTrends", checked as boolean)}
                />
                <Label htmlFor="salesTrends">Sales Trends</Label>
              </div>

              <div className="flex items-center space-x-2">
                <Checkbox
                  id="profitMargins"
                  checked={includeSections.profitMargins}
                  onCheckedChange={(checked) => handleSectionChange("profitMargins", checked as boolean)}
                />
                <Label htmlFor="profitMargins">Profit Margins</Label>
              </div>

              <div className="flex items-center space-x-2">
                <Checkbox
                  id="predictions"
                  checked={includeSections.predictions}
                  onCheckedChange={(checked) => handleSectionChange("predictions", checked as boolean)}
                />
                <Label htmlFor="predictions">Model Predictions</Label>
              </div>

              <div className="flex items-center space-x-2">
                <Checkbox
                  id="customerAnalysis"
                  checked={includeSections.customerAnalysis}
                  onCheckedChange={(checked) => handleSectionChange("customerAnalysis", checked as boolean)}
                />
                <Label htmlFor="customerAnalysis">Customer Analysis</Label>
              </div>

              <div className="flex items-center space-x-2">
                <Checkbox
                  id="productPerformance"
                  checked={includeSections.productPerformance}
                  onCheckedChange={(checked) => handleSectionChange("productPerformance", checked as boolean)}
                />
                <Label htmlFor="productPerformance">Product Performance</Label>
              </div>
            </CardContent>
            <CardFooter>
              <Button className="w-full" onClick={handleGenerateReport}>
                <FileText className="mr-2 h-4 w-4" />
                Generate Report
              </Button>
            </CardFooter>
          </Card>
        </div>

        <div className="md:col-span-2">
          <Card className="h-full">
            <CardHeader>
              <CardTitle>Report Preview</CardTitle>
              <CardDescription>Preview of your report based on selected options.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold">
                  {reportType === "sales" && "Sales Report"}
                  {reportType === "profit" && "Profit Analysis"}
                  {reportType === "forecast" && "Revenue Forecast"}
                  {reportType === "customer" && "Customer Analysis"}
                  {reportType === "product" && "Product Performance"}
                </h2>
                <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                  <span className="flex items-center">
                    <Calendar className="mr-1 h-4 w-4" />
                    {month ? month.charAt(0).toUpperCase() + month.slice(1) : "All months"}
                  </span>
                  {product && (
                    <span className="flex items-center">
                      <Tag className="mr-1 h-4 w-4" />
                      {product === "prod001" && "Premium Widget"}
                      {product === "prod002" && "Deluxe Gadget"}
                      {product === "prod003" && "Super Tool"}
                      {product === "prod004" && "Ultra Device"}
                      {product === "prod005" && "Mega Product"}
                    </span>
                  )}
                  {customer && (
                    <span className="flex items-center">
                      <Users className="mr-1 h-4 w-4" />
                      {customer === "cust001" && "Acme Corp"}
                      {customer === "cust002" && "Globex Inc"}
                      {customer === "cust003" && "Initech"}
                      {customer === "cust004" && "Umbrella Corp"}
                      {customer === "cust005" && "Stark Industries"}
                    </span>
                  )}
                </div>
              </div>

              <Tabs defaultValue="preview" className="space-y-4">
                <TabsList>
                  <TabsTrigger value="preview">Preview</TabsTrigger>
                  <TabsTrigger value="filters">Applied Filters</TabsTrigger>
                </TabsList>

                <TabsContent value="preview" className="space-y-4">
                  {includeSections.salesTrends && (
                    <div className="space-y-2">
                      <h3 className="text-lg font-semibold">Sales Trends</h3>
                      <div className="rounded-md border p-4">
                        <div className="h-40 w-full bg-muted/30 flex items-center justify-center">
                          <span className="text-muted-foreground">Sales trend chart will appear here</span>
                        </div>
                        <p className="mt-2 text-sm text-muted-foreground">
                          This section will include a detailed analysis of sales trends over time, highlighting key
                          patterns and growth opportunities.
                        </p>
                      </div>
                    </div>
                  )}

                  {includeSections.profitMargins && (
                    <div className="space-y-2">
                      <h3 className="text-lg font-semibold">Profit Margins</h3>
                      <div className="rounded-md border p-4">
                        <div className="h-40 w-full bg-muted/30 flex items-center justify-center">
                          <span className="text-muted-foreground">Profit margin chart will appear here</span>
                        </div>
                        <p className="mt-2 text-sm text-muted-foreground">
                          This section will analyze profit margins across products and customers, identifying high and
                          low-margin areas of your business.
                        </p>
                      </div>
                    </div>
                  )}

                  {includeSections.predictions && (
                    <div className="space-y-2">
                      <h3 className="text-lg font-semibold">Model Predictions</h3>
                      <div className="rounded-md border p-4">
                        <div className="h-40 w-full bg-muted/30 flex items-center justify-center">
                          <span className="text-muted-foreground">Prediction summary will appear here</span>
                        </div>
                        <p className="mt-2 text-sm text-muted-foreground">
                          This section will summarize the machine learning model's revenue predictions, including
                          confidence intervals and key factors influencing the predictions.
                        </p>
                      </div>
                    </div>
                  )}

                  {includeSections.customerAnalysis && (
                    <div className="space-y-2">
                      <h3 className="text-lg font-semibold">Customer Analysis</h3>
                      <div className="rounded-md border p-4">
                        <div className="h-40 w-full bg-muted/30 flex items-center justify-center">
                          <span className="text-muted-foreground">Customer analysis will appear here</span>
                        </div>
                        <p className="mt-2 text-sm text-muted-foreground">
                          This section will provide detailed insights into customer behavior, including purchase
                          patterns, lifetime value, and retention metrics.
                        </p>
                      </div>
                    </div>
                  )}

                  {includeSections.productPerformance && (
                    <div className="space-y-2">
                      <h3 className="text-lg font-semibold">Product Performance</h3>
                      <div className="rounded-md border p-4">
                        <div className="h-40 w-full bg-muted/30 flex items-center justify-center">
                          <span className="text-muted-foreground">Product performance will appear here</span>
                        </div>
                        <p className="mt-2 text-sm text-muted-foreground">
                          This section will analyze the performance of individual products, highlighting top performers
                          and products that may need attention.
                        </p>
                      </div>
                    </div>
                  )}
                </TabsContent>

                <TabsContent value="filters" className="space-y-4">
                  <div className="rounded-md border p-4 space-y-4">
                    <div className="flex items-center">
                      <Filter className="h-5 w-5 mr-2 text-muted-foreground" />
                      <h3 className="text-lg font-semibold">Applied Filters</h3>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <h4 className="text-sm font-medium">Report Type</h4>
                        <p className="text-sm text-muted-foreground">
                          {reportType === "sales" && "Sales Report"}
                          {reportType === "profit" && "Profit Analysis"}
                          {reportType === "forecast" && "Revenue Forecast"}
                          {reportType === "customer" && "Customer Analysis"}
                          {reportType === "product" && "Product Performance"}
                        </p>
                      </div>

                      <div>
                        <h4 className="text-sm font-medium">Time Period</h4>
                        <p className="text-sm text-muted-foreground">
                          {month ? month.charAt(0).toUpperCase() + month.slice(1) : "All months"}
                        </p>
                      </div>

                      <div>
                        <h4 className="text-sm font-medium">Product</h4>
                        <p className="text-sm text-muted-foreground">
                          {product ? (
                            <>
                              {product === "prod001" && "Premium Widget"}
                              {product === "prod002" && "Deluxe Gadget"}
                              {product === "prod003" && "Super Tool"}
                              {product === "prod004" && "Ultra Device"}
                              {product === "prod005" && "Mega Product"}
                            </>
                          ) : (
                            "All products"
                          )}
                        </p>
                      </div>

                      <div>
                        <h4 className="text-sm font-medium">Customer</h4>
                        <p className="text-sm text-muted-foreground">
                          {customer ? (
                            <>
                              {customer === "cust001" && "Acme Corp"}
                              {customer === "cust002" && "Globex Inc"}
                              {customer === "cust003" && "Initech"}
                              {customer === "cust004" && "Umbrella Corp"}
                              {customer === "cust005" && "Stark Industries"}
                            </>
                          ) : (
                            "All customers"
                          )}
                        </p>
                      </div>
                    </div>

                    <div>
                      <h4 className="text-sm font-medium">Included Sections</h4>
                      <ul className="mt-2 text-sm text-muted-foreground space-y-1">
                        {includeSections.salesTrends && <li>Sales Trends</li>}
                        {includeSections.profitMargins && <li>Profit Margins</li>}
                        {includeSections.predictions && <li>Model Predictions</li>}
                        {includeSections.customerAnalysis && <li>Customer Analysis</li>}
                        {includeSections.productPerformance && <li>Product Performance</li>}
                      </ul>
                    </div>
                  </div>
                </TabsContent>
              </Tabs>
            </CardContent>
            <CardFooter className="flex justify-between">
              <Button variant="outline">Preview Full Report</Button>
              <Button>
                <Download className="mr-2 h-4 w-4" />
                Download PDF
              </Button>
            </CardFooter>
          </Card>
        </div>
      </div>
    </div>
  )
}
