"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { BarChart3, FileInput, Home, LineChart, Settings, BellRing, FileText, BrainCircuit, BarChart2 } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { ModeToggle } from "@/components/mode-toggle"
import { ApiStatus } from "@/components/api-status"
import { DataFileIndicator } from "@/components/ui/data-file-indicator"
import { useState } from "react"

export function AppSidebar() {
  const pathname = usePathname()
  const [isSidebarOpen, setIsSidebarOpen] = useState(true)

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen)
  }

  const routes = [
    {
      title: "Home",
      icon: Home,
      href: "/",
      isActive: pathname === "/",
    },
    {
      title: "Data Input",
      icon: FileInput,
      href: "/data-input",
      isActive: pathname === "/data-input",
    },
    {
      title: "Dashboard",
      icon: BarChart3,
      href: "/dashboard",
      isActive: pathname === "/dashboard",
    },
    {
      title: "Scenario Planner",
      icon: BrainCircuit,
      href: "/scenario-planner",
      isActive: pathname === "/scenario-planner",
    },
    {
      title: "Sales Forecasting",
      icon: BarChart2,
      href: "/sales-forecasting",
      isActive: pathname === "/sales-forecasting",
    },
    {
      title: "Insights",
      icon: BellRing,
      href: "/insights",
      isActive: pathname === "/insights",
    },
    {
      title: "Settings",
      icon: Settings,
      href: "/settings",
      isActive: pathname === "/settings",
    },
  ]

  return (
    <div className={`sidebar h-screen ${isSidebarOpen ? 'w-64' : 'w-16'} flex flex-col transition-all duration-300`}>
      <div className="sidebar-header flex items-center justify-between px-4 py-3 border-b">
        <div className="flex items-center space-x-2">
          <LineChart className="h-6 w-6 text-blue-600 dark:text-blue-400" />
          {isSidebarOpen && <span className="font-bold text-lg">IDSS</span>}
        </div>
        <Button 
          variant="outline" 
          size="sm" 
          className="h-8 w-8 p-0"
          onClick={toggleSidebar}
        >
          <span className="sr-only">Toggle Sidebar</span>
          <MenuIcon className="h-4 w-4" />
        </Button>
      </div>
      
      <div className="flex-1 overflow-auto py-2">
        <nav className="grid gap-1 px-2">
          {routes.map((route) => (
            <Link
              key={route.href}
              href={route.href}
              className={cn(
                "sidebar-link flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors",
                route.isActive 
                  ? "bg-muted text-primary hover:bg-muted/80" 
                  : "text-muted-foreground hover:bg-muted hover:text-primary",
                isSidebarOpen ? "justify-start space-x-3" : "justify-center"
              )}
              title={!isSidebarOpen ? route.title : undefined}
            >
              <route.icon className="h-4 w-4 flex-shrink-0" />
              {isSidebarOpen && <span>{route.title}</span>}
            </Link>
          ))}
        </nav>
      </div>
      
      <div className="border-t p-4">
        {isSidebarOpen && (
          <>
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs text-gray-500 dark:text-gray-400">Business Intelligence</span>
              <ModeToggle />
            </div>
            <div className="mt-2">
              <ApiStatus />
            </div>
            <div className="mt-2">
              <DataFileIndicator />
            </div>
          </>
        )}
        {!isSidebarOpen && (
          <div className="flex justify-center">
            <ModeToggle />
          </div>
        )}
      </div>
    </div>
  )
}

// Simple menu icon component
function MenuIcon(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <line x1="4" x2="20" y1="12" y2="12" />
      <line x1="4" x2="20" y1="6" y2="6" />
      <line x1="4" x2="20" y1="18" y2="18" />
    </svg>
  )
}
