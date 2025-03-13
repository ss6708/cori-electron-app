import { useState, useEffect, useRef } from 'react'

interface UseExcelScreenshotProps {
  enabled: boolean
  interval?: number
}

interface UseExcelScreenshotResult {
  screenshotUrl: string | null
  isLoading: boolean
  error: string | null
  startCapturing: () => void
  stopCapturing: () => void
}

export function useExcelScreenshot({ 
  enabled = true, 
  interval = 1000 
}: UseExcelScreenshotProps): UseExcelScreenshotResult {
  const [screenshotUrl, setScreenshotUrl] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)
  const [isCapturing, setIsCapturing] = useState<boolean>(enabled)
  const intervalRef = useRef<NodeJS.Timeout | null>(null)

  const fetchScreenshot = async () => {
    try {
      setIsLoading(true)
      setError(null)
      
      // Add timestamp to prevent caching
      const response = await fetch(`http://localhost:5000/excel-screenshot?t=${Date.now()}`)
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Failed to fetch screenshot')
      }
      
      const blob = await response.blob()
      const url = URL.createObjectURL(blob)
      
      // Revoke previous URL to prevent memory leaks
      if (screenshotUrl) {
        URL.revokeObjectURL(screenshotUrl)
      }
      
      setScreenshotUrl(url)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setIsLoading(false)
    }
  }

  const startCapturing = () => {
    setIsCapturing(true)
  }

  const stopCapturing = () => {
    setIsCapturing(false)
  }

  useEffect(() => {
    if (isCapturing) {
      // Fetch immediately on start
      fetchScreenshot()
      
      // Set up interval for continuous fetching
      intervalRef.current = setInterval(fetchScreenshot, interval)
    }
    
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
        intervalRef.current = null
      }
      
      // Clean up any object URLs when component unmounts
      if (screenshotUrl) {
        URL.revokeObjectURL(screenshotUrl)
      }
    }
  }, [isCapturing, interval, fetchScreenshot, screenshotUrl])

  return {
    screenshotUrl,
    isLoading,
    error,
    startCapturing,
    stopCapturing
  }
}
