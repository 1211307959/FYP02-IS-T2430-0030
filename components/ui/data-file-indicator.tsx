"use client"

import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { getDataFiles } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { FileIcon, FilesIcon } from "lucide-react";

export function DataFileIndicator() {
  const [fileCount, setFileCount] = useState<number>(0);
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const fetchDataFilesInfo = async () => {
    try {
      setIsLoading(true);
      const data = await getDataFiles();
      setFileCount(data.files?.length || 0);
      setLastUpdated(new Date().toLocaleTimeString());
    } catch (error) {
      console.error("Error fetching data files info:", error);
      setFileCount(0);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDataFilesInfo();

    // Listen for data file changes
    const handleDataFileChanged = (event: Event) => {
      // Reload file info when data changes
      fetchDataFilesInfo();
    };

    window.addEventListener('dataFileChanged', handleDataFileChanged);

    return () => {
      window.removeEventListener('dataFileChanged', handleDataFileChanged);
    };
  }, []);

  if (fileCount === 0) return null;

  return (
    <div className="flex items-center space-x-2 text-sm">
      <FilesIcon className="h-4 w-4 text-muted-foreground" />
      <span className="text-muted-foreground">Using combined data from:</span>
      <Badge variant="outline" className="font-mono">
        {fileCount} file{fileCount !== 1 ? 's' : ''}
      </Badge>
      {lastUpdated && (
        <span className="text-xs text-muted-foreground">
          (updated at {lastUpdated})
        </span>
      )}
    </div>
  );
} 