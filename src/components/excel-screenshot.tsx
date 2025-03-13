import React, { useState } from 'react'
import { Button } from "./ui/button"
import { useExcelScreenshot } from '../hooks/use-excel-screenshot'
import { TechSpreadsheetLargeIcon } from "./tech-icons"

interface ExcelScreenshotProps {
  className?: string
}

export function ExcelScreenshot({ className }: ExcelScreenshotProps) {
  const [isExcelRunning, setIsExcelRunning] = useState(false)
  const { 
    screenshotUrl, 
    isLoading, 
    error, 
    startCapturing, 
    stopCapturing 
  } = useExcelScreenshot({
    enabled: isExcelRunning,
    interval: 1000 // Update every second
  })

  const handleOpenExcel = async () => {
    try {
      const response = await fetch('http://localhost:5000/open-excel')
      const data = await response.json()
      
      if (data.error) {
        console.error('Error opening Excel:', data.error)
        return
      }
      
      setIsExcelRunning(true)
    } catch (err) {
      console.error('Failed to open Excel:', err)
    }
  }

  return (
    <div className={`flex flex-col items-center ${className}`}>
      {!isExcelRunning ? (
        <div className="flex flex-col items-center justify-center h-full p-6 text-center">
          <div className="w-16 h-16 mb-4 text-blue-400/70 opacity-70 animate-float">
            <TechSpreadsheetLargeIcon />
          </div>
          <h3 className="text-lg font-thin mb-2 text-gray-300/90 tracking-wide text-gradient">Excel Viewer</h3>
          <p className="text-sm text-gray-400/80 max-w-md font-mono">
            Click the button below to open Excel and start viewing screenshots.
          </p>
          <Button 
            onClick={handleOpenExcel}
            className="mt-6 bg-blue-600/30 hover:bg-blue-600/50 text-white backdrop-blur-sm border border-[#ffffff1a] px-4 shadow-[0_0_15px_rgba(59,130,246,0.3)] transition-all duration-300 hover:shadow-[0_0_20px_rgba(59,130,246,0.5)] hover:scale-105"
          >
            Open Excel
          </Button>
        </div>
      ) : (
        <div className="relative w-full h-full flex flex-col">
          {isLoading && !screenshotUrl && (
            <div className="absolute inset-0 flex items-center justify-center bg-[#1a2035]/50 backdrop-blur-sm">
              <div className="text-blue-300 animate-pulse">Loading...</div>
            </div>
          )}
          
          {error && (
            <div className="absolute top-2 right-2 p-2 bg-red-500/20 text-red-300 text-xs rounded backdrop-blur-sm">
              {error}
            </div>
          )}
          
          {screenshotUrl ? (
            <img 
              src={screenshotUrl} 
              alt="Excel Screenshot" 
              className="w-full h-full object-contain"
            />
          ) : (
            <div className="flex items-center justify-center h-full">
              <p className="text-gray-400">Waiting for Excel window...</p>
            </div>
          )}
          
          <div className="absolute bottom-2 right-2 flex gap-2">
            <Button 
              onClick={stopCapturing}
              className="bg-red-600/30 hover:bg-red-600/50 text-white text-xs backdrop-blur-sm border border-[#ffffff1a] px-2 py-1"
              size="sm"
            >
              Pause
            </Button>
            <Button 
              onClick={startCapturing}
              className="bg-green-600/30 hover:bg-green-600/50 text-white text-xs backdrop-blur-sm border border-[#ffffff1a] px-2 py-1"
              size="sm"
            >
              Resume
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
