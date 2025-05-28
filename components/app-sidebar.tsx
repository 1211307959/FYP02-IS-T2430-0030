"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { BarChart3, FileInput, Home, LineChart, Settings, BellRing, FileText, BrainCircuit } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { ModeToggle } from "@/components/mode-toggle"
import { ApiStatus } from "@/components/api-status"
import { DataFileIndicator } from "@/components/ui/data-file-indicator"

export function AppSidebar() {
  const pathname = usePathname()

  const routes = [
    {
      title: "Dashboard",
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
      title: "Reports",
      icon: FileText,
      href: "/reports",
      isActive: pathname === "/reports",
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
    <div className="sidebar h-screen w-64 flex flex-col">
      <div className="sidebar-header">
        <div className="flex items-center space-x-2">
          <LineChart className="h-6 w-6 text-blue-600 dark:text-blue-400" />
          <span className="font-bold text-lg">IDSS</span>
        </div>
        <Button variant="outline" size="sm" className="h-8 w-8 p-0">
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
                "sidebar-link",
                route.isActive ? "sidebar-link-active" : "sidebar-link-inactive"
              )}
            >
              <route.icon className="h-4 w-4" />
              <span>{route.title}</span>
            </Link>
          ))}
        </nav>
      </div>
      
      <div className="border-t p-4">
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
