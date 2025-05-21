"use client"

import { useState, useEffect } from "react"
import { CheckCircle, XCircle } from "lucide-react"

export function ApiStatus() {
  const [status, setStatus] = useState<"loading" | "healthy" | "unhealthy">("loading")

  useEffect(() => {
    const checkApiStatus = async () => {
      try {
        const response = await fetch("/api/health", {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        })

        if (response.ok) {
          setStatus("healthy")
        } else {
          setStatus("unhealthy")
        }
      } catch (error) {
        console.error("API Health Check Error:", error)
        setStatus("unhealthy")
      }
    }

    // Initial check
    checkApiStatus()

    // Set up interval for recurring checks
    const interval = setInterval(checkApiStatus, 30000) // 30 seconds

    return () => clearInterval(interval)
  }, [])

  return (
    <div className="flex items-center gap-2 rounded border px-3 py-1">
      {status === "loading" ? (
        <div className="h-2 w-2 animate-pulse rounded-full bg-yellow-500" />
      ) : status === "healthy" ? (
        <CheckCircle className="h-4 w-4 text-green-500" />
      ) : (
        <XCircle className="h-4 w-4 text-red-500" />
      )}
      <span className="text-xs font-medium">
        API {status === "loading" ? "checking" : status}
      </span>
    </div>
  )
} 