"use client"

import type React from "react"

import { useState, useEffect, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Switch } from "@/components/ui/switch"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Separator } from "@/components/ui/separator"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { ModeToggle } from "@/components/mode-toggle"
import { useToast } from "@/components/ui/use-toast"
import { Save, Trash2, Upload, RefreshCw } from "lucide-react"
import { getDataFiles, selectDataFile, reloadDataFiles, uploadFile } from "@/lib/api"
import { Alert, AlertDescription } from "@/components/ui/alert"

export default function SettingsPage() {
  const { toast } = useToast()
  const fileInputRef = useRef<HTMLInputElement>(null)

  // User profile state
  const [profile, setProfile] = useState({
    businessName: "IDSS Revenue Prediction",
    email: "admin@idssrevenue.com",
    phone: "(555) 123-4567",
    address: "123 Business Analytics Ave",
    city: "Data Science City",
    state: "DS",
    zip: "10101",
  })

  // Notification settings state
  const [notifications, setNotifications] = useState({
    emailAlerts: true,
    weeklyReports: true,
    insightAlerts: true,
    dataUpdates: false,
  })

  // Dataset state
  const [datasets, setDatasets] = useState<Array<{id: number, name: string, date: string, size: string, status: string}>>([])
  const [isLoading, setIsLoading] = useState(false)
  const [currentFile, setCurrentFile] = useState("")

  // Fetch datasets when component mounts
  useEffect(() => {
    fetchDataFiles()
  }, [])

  // Fetch data files from the API
  const fetchDataFiles = async () => {
    setIsLoading(true)
    try {
      const data = await getDataFiles()
      
      // Transform the data into the format expected by the table
      const formattedDatasets = data.files.map((file: string, index: number) => {
        return {
          id: index + 1,
          name: file,
          date: new Date().toLocaleDateString(), // Using current date since API doesn't provide dates
          size: "Unknown", // Size not available from API
          status: file === data.current_file ? "Active" : "Inactive"
        }
      })
      
      setDatasets(formattedDatasets)
      setCurrentFile(data.current_file)
    } catch (error) {
      console.error("Error fetching data files:", error)
      toast({
        title: "Error loading datasets",
        description: "Could not load dataset list. Please try again later.",
        variant: "destructive"
      })
      
      // Fallback to showing trainingdataset.csv if the API fails
      setDatasets([{
        id: 1,
        name: "trainingdataset.csv",
        date: new Date().toLocaleDateString(),
        size: "Unknown",
        status: "Active"
      }])
      setCurrentFile("trainingdataset.csv")
    } finally {
      setIsLoading(false)
    }
  }

  // Handle profile form changes
  const handleProfileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setProfile((prev) => ({
      ...prev,
      [name]: value,
    }))
  }

  // Handle notification toggle
  const handleNotificationToggle = (key: string) => {
    setNotifications((prev) => ({
      ...prev,
      [key]: !prev[key as keyof typeof prev],
    }))
  }

  // Handle selecting a dataset - now just reloads all data
  const handleReloadAllData = async () => {
    setIsLoading(true)
    try {
      // Call the API to reload all data files
      const result = await reloadDataFiles()
      
      toast({
        title: "Using combined data",
        description: `Now using combined data from all CSV files (${result.files?.length || 0} files).`,
      })
      
      // Force a refresh of all components
      window.dispatchEvent(new CustomEvent('dataFileChanged', { 
        detail: { message: 'Using combined data from all files', timestamp: new Date().toISOString() } 
      }));
    } catch (error) {
      console.error("Error reloading data:", error)
      toast({
        title: "Error reloading data",
        description: "Could not reload the dataset files. Please try again.",
        variant: "destructive"
      })
    } finally {
      setIsLoading(false)
    }
  }

  // Handle file input change
  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return
    
    const file = e.target.files[0]
    if (!file.name.endsWith('.csv')) {
      toast({
        title: "Invalid file format",
        description: "Please upload a CSV file.",
        variant: "destructive"
      })
      return
    }
    
    // Upload the file
    setIsLoading(true)
    try {
      await uploadFile(file)
      toast({
        title: "Dataset uploaded",
        description: `${file.name} has been uploaded successfully.`,
      })
      // Refresh the file list
      await fetchDataFiles()
    } catch (error) {
      toast({
        title: "Upload failed",
        description: "Could not upload the dataset. Please try again.",
        variant: "destructive"
      })
    } finally {
      setIsLoading(false)
      // Reset the file input
      if (fileInputRef.current) {
        fileInputRef.current.value = ""
      }
    }
  }

  // Handle refresh data files - now actually reloads from API
  const handleRefreshDataFiles = async () => {
    setIsLoading(true)
    try {
      await reloadDataFiles()
      await fetchDataFiles()
      toast({
        title: "Dataset list refreshed",
        description: "The list of available datasets has been updated.",
      })
    } catch (error) {
      toast({
        title: "Refresh failed",
        description: "Could not refresh the dataset list. Please try again.",
        variant: "destructive"
      })
    } finally {
      setIsLoading(false)
    }
  }

  // Handle profile save
  const handleProfileSave = () => {
    toast({
      title: "Profile updated",
      description: "Your profile information has been saved successfully.",
    })
  }

  // Handle notification settings save
  const handleNotificationSave = () => {
    toast({
      title: "Notification settings updated",
      description: "Your notification preferences have been saved successfully.",
    })
  }

  // Handle file upload button click
  const handleUploadClick = () => {
    // Trigger the hidden file input
    if (fileInputRef.current) {
      fileInputRef.current.click()
    }
  }
  
  // Handle delete dataset button click
  const handleDeleteClick = (datasetId: number) => {
    const dataset = datasets.find(d => d.id === datasetId)
    if (dataset?.status === "Active") {
      toast({
        title: "Cannot delete active dataset",
        description: "Please select another dataset before deleting this one.",
        variant: "destructive"
      })
      return
    }
    
    toast({
      title: "Delete not implemented",
      description: "The delete functionality will be available in a future update.",
      variant: "destructive"
    })
  }
  
  // Handle appearance save
  const handleAppearanceSave = () => {
    toast({
      title: "Appearance updated",
      description: "Your appearance settings have been saved successfully.",
    })
  }

  // Handle dataset settings save
  const handleDatasetSettingsSave = () => {
    toast({
      title: "Dataset settings updated",
      description: "Your dataset retention settings have been saved successfully.",
    })
  }

  return (
    <div className="container py-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
      </div>

      {/* Hidden file input for CSV upload */}
      <input 
        type="file" 
        accept=".csv" 
        ref={fileInputRef} 
        onChange={handleFileChange}
        style={{ display: 'none' }} 
      />

      <Tabs defaultValue="datasets" className="space-y-4">
        <TabsList>
          <TabsTrigger value="profile">User Profile</TabsTrigger>
          <TabsTrigger value="notifications">Notifications</TabsTrigger>
          <TabsTrigger value="appearance">Appearance</TabsTrigger>
          <TabsTrigger value="datasets">Datasets</TabsTrigger>
        </TabsList>

        <TabsContent value="profile">
          <Card>
            <CardHeader>
              <CardTitle>Business Profile</CardTitle>
              <CardDescription>Manage your business information and contact details.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="businessName">Business Name</Label>
                  <Input
                    id="businessName"
                    name="businessName"
                    value={profile.businessName}
                    onChange={handleProfileChange}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input id="email" name="email" type="email" value={profile.email} onChange={handleProfileChange} />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="phone">Phone</Label>
                  <Input id="phone" name="phone" value={profile.phone} onChange={handleProfileChange} />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="address">Address</Label>
                  <Input id="address" name="address" value={profile.address} onChange={handleProfileChange} />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="city">City</Label>
                  <Input id="city" name="city" value={profile.city} onChange={handleProfileChange} />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="state">State</Label>
                    <Input id="state" name="state" value={profile.state} onChange={handleProfileChange} />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="zip">ZIP Code</Label>
                    <Input id="zip" name="zip" value={profile.zip} onChange={handleProfileChange} />
                  </div>
                </div>
              </div>
            </CardContent>
            <CardFooter>
              <Button onClick={handleProfileSave}>
                <Save className="mr-2 h-4 w-4" />
                Save Changes
              </Button>
            </CardFooter>
          </Card>
        </TabsContent>

        <TabsContent value="notifications">
          <Card>
            <CardHeader>
              <CardTitle>Notification Preferences</CardTitle>
              <CardDescription>Configure how and when you receive notifications and alerts.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="emailAlerts">Email Alerts</Label>
                    <p className="text-sm text-muted-foreground">Receive important alerts via email</p>
                  </div>
                  <Switch
                    id="emailAlerts"
                    checked={notifications.emailAlerts}
                    onCheckedChange={() => handleNotificationToggle("emailAlerts")}
                  />
                </div>

                <Separator />

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="weeklyReports">Weekly Reports</Label>
                    <p className="text-sm text-muted-foreground">Receive weekly summary reports</p>
                  </div>
                  <Switch
                    id="weeklyReports"
                    checked={notifications.weeklyReports}
                    onCheckedChange={() => handleNotificationToggle("weeklyReports")}
                  />
                </div>

                <Separator />

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="insightAlerts">Insight Alerts</Label>
                    <p className="text-sm text-muted-foreground">Receive alerts when new insights are available</p>
                  </div>
                  <Switch
                    id="insightAlerts"
                    checked={notifications.insightAlerts}
                    onCheckedChange={() => handleNotificationToggle("insightAlerts")}
                  />
                </div>

                <Separator />

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="dataUpdates">Data Update Notifications</Label>
                    <p className="text-sm text-muted-foreground">Receive notifications when data is updated</p>
                  </div>
                  <Switch
                    id="dataUpdates"
                    checked={notifications.dataUpdates}
                    onCheckedChange={() => handleNotificationToggle("dataUpdates")}
                  />
                </div>
              </div>
            </CardContent>
            <CardFooter>
              <Button onClick={handleNotificationSave}>
                <Save className="mr-2 h-4 w-4" />
                Save Preferences
              </Button>
            </CardFooter>
          </Card>
        </TabsContent>

        <TabsContent value="appearance">
          <Card>
            <CardHeader>
              <CardTitle>Appearance Settings</CardTitle>
              <CardDescription>Customize the look and feel of your dashboard.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label>Theme</Label>
                  <div className="flex items-center space-x-2">
                    <ModeToggle />
                    <span className="text-sm text-muted-foreground">Choose between light, dark, or system theme</span>
                  </div>
                </div>

                <Separator />

                <div className="space-y-2">
                  <Label htmlFor="density">Display Density</Label>
                  <Select defaultValue="comfortable">
                    <SelectTrigger id="density">
                      <SelectValue placeholder="Select density" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="compact">Compact</SelectItem>
                      <SelectItem value="comfortable">Comfortable</SelectItem>
                      <SelectItem value="spacious">Spacious</SelectItem>
                    </SelectContent>
                  </Select>
                  <p className="text-sm text-muted-foreground">Adjust the spacing between elements</p>
                </div>

                <Separator />

                <div className="space-y-2">
                  <Label htmlFor="defaultView">Default Dashboard View</Label>
                  <Select defaultValue="overview">
                    <SelectTrigger id="defaultView">
                      <SelectValue placeholder="Select default view" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="overview">Overview</SelectItem>
                      <SelectItem value="sales">Sales Analytics</SelectItem>
                      <SelectItem value="products">Product Performance</SelectItem>
                      <SelectItem value="customers">Customer Insights</SelectItem>
                    </SelectContent>
                  </Select>
                  <p className="text-sm text-muted-foreground">
                    Choose which view to show when you first open the dashboard
                  </p>
                </div>
              </div>
            </CardContent>
            <CardFooter>
              <Button onClick={handleAppearanceSave}>
                <Save className="mr-2 h-4 w-4" />
                Save Appearance
              </Button>
            </CardFooter>
          </Card>
        </TabsContent>

        <TabsContent value="datasets">
          <Card>
            <CardHeader>
              <CardTitle>Manage Datasets</CardTitle>
              <CardDescription>View and manage the datasets used for predictions and analysis.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-between mb-4">
                <Button variant="outline" onClick={handleRefreshDataFiles} disabled={isLoading}>
                  <RefreshCw className="mr-2 h-4 w-4" />
                  Refresh List
                </Button>
                <Button onClick={handleUploadClick} disabled={isLoading}>
                  <Upload className="mr-2 h-4 w-4" />
                  Upload New Dataset
                </Button>
              </div>

              {isLoading ? (
                <div className="py-8 text-center text-muted-foreground">Loading datasets...</div>
              ) : datasets.length === 0 ? (
                <div className="py-8 text-center text-muted-foreground">No datasets found. Upload a CSV file to get started.</div>
              ) : (
                <>
                  <Alert className="mb-4">
                    <AlertDescription>
                      All CSV files in the data folder are now used simultaneously. The system automatically combines data from all files.
                    </AlertDescription>
                  </Alert>
                  <div className="rounded-md border">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Dataset Name</TableHead>
                          <TableHead>Upload Date</TableHead>
                          <TableHead>Size</TableHead>
                          <TableHead>Status</TableHead>
                          <TableHead className="text-right">Actions</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {datasets.map((dataset) => (
                          <TableRow key={dataset.id}>
                            <TableCell className="font-medium">
                              {dataset.name}
                            </TableCell>
                            <TableCell>{dataset.date}</TableCell>
                            <TableCell>{dataset.size}</TableCell>
                            <TableCell>
                              <span className="inline-flex items-center rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-800 dark:bg-green-900 dark:text-green-300">
                                Active
                              </span>
                            </TableCell>
                            <TableCell className="text-right">
                              <Button 
                                variant="ghost" 
                                size="sm" 
                                onClick={() => handleDeleteClick(dataset.id)}
                                disabled={isLoading}
                              >
                                <Trash2 className="h-4 w-4 text-muted-foreground" />
                                <span className="sr-only">Delete</span>
                              </Button>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                  <div className="mt-4 flex justify-end">
                    <Button onClick={handleReloadAllData} disabled={isLoading}>
                      <RefreshCw className="mr-2 h-4 w-4" />
                      Reload All Data
                    </Button>
                  </div>
                </>
              )}

              <div className="space-y-2 mt-4">
                <Label htmlFor="dataRetention">Data Retention Policy</Label>
                <Select defaultValue="1year">
                  <SelectTrigger id="dataRetention">
                    <SelectValue placeholder="Select retention period" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="3months">3 Months</SelectItem>
                    <SelectItem value="6months">6 Months</SelectItem>
                    <SelectItem value="1year">1 Year</SelectItem>
                    <SelectItem value="2years">2 Years</SelectItem>
                    <SelectItem value="indefinite">Indefinite</SelectItem>
                  </SelectContent>
                </Select>
                <p className="text-sm text-muted-foreground">Choose how long to keep historical data</p>
              </div>
            </CardContent>
            <CardFooter>
              <Button onClick={handleDatasetSettingsSave}>
                <Save className="mr-2 h-4 w-4" />
                Save Dataset Settings
              </Button>
            </CardFooter>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
