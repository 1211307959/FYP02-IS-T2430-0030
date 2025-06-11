import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "@/components/ui/card"
import { BarChart3, FileInput, Settings, BellRing, FileText, BrainCircuit, ArrowRight } from "lucide-react"
import Link from "next/link"

export default function Home() {
  return (
    <div className="flex flex-col h-full">
      <header className="border-b">
        <div className="container flex items-center justify-between py-4">
          <h1 className="text-2xl font-bold">Intelligent Decision Support System</h1>
        </div>
      </header>
      <main className="flex-1 overflow-auto">
        <div className="container py-6">
          <div className="grid gap-6">
            <section className="space-y-4">
              <h2 className="text-3xl font-bold tracking-tight">Welcome to your Business Intelligence Dashboard</h2>
              <p className="text-muted-foreground">
                Make data-driven decisions with machine learning predictions for your small business.
              </p>
            </section>

            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Data Input</CardTitle>
                  <FileInput className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">Upload Sales Data</div>
                  <p className="text-xs text-muted-foreground">
                    Upload your CSV data or manually input sales information
                  </p>
                  <Button asChild className="mt-4 w-full">
                    <Link href="/data-input">
                      Get Started <ArrowRight className="ml-2 h-4 w-4" />
                    </Link>
                  </Button>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Dashboard</CardTitle>
                  <BarChart3 className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">View Analytics</div>
                  <p className="text-xs text-muted-foreground">See KPIs, revenue trends, and performance metrics</p>
                  <Button asChild className="mt-4 w-full">
                    <Link href="/dashboard">
                      View Dashboard <ArrowRight className="ml-2 h-4 w-4" />
                    </Link>
                  </Button>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Scenario Planner</CardTitle>
                  <BrainCircuit className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">Simulate Scenarios</div>
                  <p className="text-xs text-muted-foreground">Test different pricing and quantity scenarios</p>
                  <Button asChild className="mt-4 w-full">
                    <Link href="/scenario-planner">
                      Plan Scenarios <ArrowRight className="ml-2 h-4 w-4" />
                    </Link>
                  </Button>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Sales Forecasting</CardTitle>
                  <BarChart3 className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">Generate Forecasts</div>
                  <p className="text-xs text-muted-foreground">Create downloadable PDF summaries of your data</p>
                  <Button asChild className="mt-4 w-full">
                    <Link href="/sales-forecasting">
                      Create Forecasts <ArrowRight className="ml-2 h-4 w-4" />
                    </Link>
                  </Button>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Insights</CardTitle>
                  <BellRing className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">View Insights</div>
                  <p className="text-xs text-muted-foreground">Discover AI-generated insights about your business</p>
                  <Button asChild className="mt-4 w-full">
                    <Link href="/insights">
                      See Insights <ArrowRight className="ml-2 h-4 w-4" />
                    </Link>
                  </Button>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Settings</CardTitle>
                  <Settings className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">Manage Settings</div>
                  <p className="text-xs text-muted-foreground">Configure your profile and application preferences</p>
                  <Button asChild className="mt-4 w-full">
                    <Link href="/settings">
                      Open Settings <ArrowRight className="ml-2 h-4 w-4" />
                    </Link>
                  </Button>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
