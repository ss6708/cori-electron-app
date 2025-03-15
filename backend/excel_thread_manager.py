"""
Excel Thread Manager for Cori backend.
Provides a dedicated thread for Excel operations with proper COM initialization.
"""

import os
import platform
import threading
import queue
import logging
import time
import uuid
from pathlib import Path
from typing import Dict, Any, Optional, Callable, Tuple, List, Union

# Configure logging
logger = logging.getLogger(__name__)

# Windows-specific imports
if platform.system() == "Windows":
    import pythoncom
    import win32com.client

class ExcelThreadManager:
    """
    Thread manager for Excel operations.
    Ensures all Excel COM operations run in a single dedicated thread with proper COM initialization.
    """
    
    def __init__(self):
        """Initialize the Excel thread manager."""
        self._excel_app = None
        self._thread = None
        self._running = False
        self._task_queue = queue.Queue()
        self._result_map = {}
        self._lock = threading.Lock()
    
    def start(self):
        """Start the Excel thread if not already running."""
        if self._running:
            logger.info("Excel thread already running")
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._excel_thread_worker, daemon=True)
        self._thread.start()
        logger.info("Excel thread started")
    
    def stop(self):
        """Stop the Excel thread and clean up resources."""
        if not self._running:
            logger.info("Excel thread not running")
            return
        
        self._running = False
        if self._thread:
            self._task_queue.put(("quit", None, None))
            self._thread.join(timeout=5)
            logger.info("Excel thread stopped")
    
    def _excel_thread_worker(self):
        """Worker function for the Excel thread."""
        system = platform.system()
        
        if system == "Windows":
            # Initialize COM for this thread with STA model
            pythoncom.CoInitializeEx(pythoncom.COINIT_APARTMENTTHREADED)
            logger.info("COM initialized with STA model in Excel thread")
            
            try:
                # Create Excel application instance
                self._excel_app = win32com.client.Dispatch("Excel.Application")
                self._excel_app.Visible = True
                logger.info("Excel application created in dedicated thread")
                
                # Process tasks from the queue
                while self._running:
                    try:
                        task_type, task_id, task_args = self._task_queue.get(timeout=0.5)
                        
                        if task_type == "quit":
                            break
                        
                        try:
                            if task_type == "open_workbook":
                                result = self._handle_open_workbook(task_args)
                            elif task_type == "create_workbook":
                                result = self._handle_create_workbook()
                            elif task_type == "capture_screenshot":
                                result = self._handle_capture_screenshot()
                            else:
                                result = (False, f"Unknown task type: {task_type}")
                            
                            # Store the result
                            with self._lock:
                                self._result_map[task_id] = result
                                
                        except Exception as e:
                            logger.error(f"Error executing Excel task {task_type}: {str(e)}")
                            with self._lock:
                                self._result_map[task_id] = (False, f"Error: {str(e)}")
                        
                        self._task_queue.task_done()
                        
                    except queue.Empty:
                        # No tasks in queue, continue waiting
                        pass
                
                # Clean up Excel application
                if self._excel_app:
                    try:
                        self._excel_app.Quit()
                    except Exception as e:
                        logger.error(f"Error quitting Excel: {str(e)}")
                    self._excel_app = None
                
                # Uninitialize COM
                pythoncom.CoUninitialize()
                logger.info("COM uninitialized in Excel thread")
                
            except Exception as e:
                logger.error(f"Error in Excel thread: {str(e)}")
                with self._lock:
                    for task_id in list(self._result_map.keys()):
                        if self._result_map[task_id] is None:
                            self._result_map[task_id] = (False, f"Excel thread error: {str(e)}")
        
        else:
            logger.warning(f"ExcelThreadManager is only supported on Windows, not {system}")
    
    def _handle_open_workbook(self, args):
        """Handle opening an existing workbook."""
        try:
            file_path = args.get("file_path")
            
            if not file_path:
                return (False, "No file path provided")
            
            if not os.path.exists(file_path):
                return (False, f"File not found: {file_path}")
            
            workbook = self._excel_app.Workbooks.Open(file_path)
            return (True, "Workbook opened successfully")
            
        except Exception as e:
            return (False, f"Error opening workbook: {str(e)}")
    
    def _handle_create_workbook(self):
        """Handle creating a new workbook."""
        try:
            workbook = self._excel_app.Workbooks.Add()
            return (True, "New workbook created successfully")
            
        except Exception as e:
            return (False, f"Error creating workbook: {str(e)}")
    
    def _handle_capture_screenshot(self):
        """Handle capturing a screenshot of the Excel window."""
        try:
            import win32gui
            import win32ui
            import win32con
            from PIL import Image
            import io
            
            # Find Excel window handle
            hwnd = win32gui.FindWindow(None, self._excel_app.Caption)
            if not hwnd:
                return (False, "Excel window not found")
            
            # Get window dimensions
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            width = right - left
            height = bottom - top
            
            # Create device context
            hwnd_dc = win32gui.GetWindowDC(hwnd)
            mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
            save_dc = mfc_dc.CreateCompatibleDC()
            
            # Create bitmap
            save_bitmap = win32ui.CreateBitmap()
            save_bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
            save_dc.SelectObject(save_bitmap)
            
            # Copy screen to bitmap
            save_dc.BitBlt((0, 0), (width, height), mfc_dc, (0, 0), win32con.SRCCOPY)
            
            # Convert bitmap to image
            bmpinfo = save_bitmap.GetInfo()
            bmpstr = save_bitmap.GetBitmapBits(True)
            img = Image.frombuffer(
                'RGB',
                (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                bmpstr, 'raw', 'BGRX', 0, 1
            )
            
            # Save image to bytes
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            
            # Clean up
            win32gui.DeleteObject(save_bitmap.GetHandle())
            save_dc.DeleteDC()
            mfc_dc.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwnd_dc)
            
            return (True, img_byte_arr)
            
        except Exception as e:
            return (False, f"Error capturing screenshot: {str(e)}")
    
    def open_spreadsheet(self, file_path=None):
        """
        Open a spreadsheet in Excel.
        
        Args:
            file_path: Path to the Excel file to open. If None, creates a new workbook.
            
        Returns:
            Tuple of (success, message)
        """
        if platform.system() != "Windows":
            return (False, "Excel operations are only supported on Windows")
        
        # Start the Excel thread if not already running
        if not self._running:
            self.start()
        
        # Generate a unique task ID
        task_id = str(uuid.uuid4())
        
        # Initialize result
        with self._lock:
            self._result_map[task_id] = None
        
        if file_path:
            # Queue task to open existing workbook
            self._task_queue.put(("open_workbook", task_id, {"file_path": file_path}))
        else:
            # Queue task to create new workbook
            self._task_queue.put(("create_workbook", task_id, None))
        
        # Wait for the result
        start_time = time.time()
        while time.time() - start_time < 10:  # 10 second timeout
            with self._lock:
                result = self._result_map.get(task_id)
                if result is not None:
                    del self._result_map[task_id]
                    return result
            
            time.sleep(0.1)
        
        # Timeout
        with self._lock:
            if task_id in self._result_map:
                del self._result_map[task_id]
        
        return (False, "Timeout waiting for Excel operation to complete")
    
    def capture_screenshot(self):
        """
        Capture a screenshot of the Excel window.
        
        Returns:
            Tuple of (success, image_bytes or error_message)
        """
        if platform.system() != "Windows":
            return (False, "Excel operations are only supported on Windows")
        
        if not self._running:
            return (False, "Excel thread not running")
        
        # Generate a unique task ID
        task_id = str(uuid.uuid4())
        
        # Initialize result
        with self._lock:
            self._result_map[task_id] = None
        
        # Queue task to capture screenshot
        self._task_queue.put(("capture_screenshot", task_id, None))
        
        # Wait for the result
        start_time = time.time()
        while time.time() - start_time < 10:  # 10 second timeout
            with self._lock:
                result = self._result_map.get(task_id)
                if result is not None:
                    del self._result_map[task_id]
                    return result
            
            time.sleep(0.1)
        
        # Timeout
        with self._lock:
            if task_id in self._result_map:
                del self._result_map[task_id]
        
        return (False, "Timeout waiting for Excel screenshot to complete")

# Singleton instance
excel_manager = ExcelThreadManager()
