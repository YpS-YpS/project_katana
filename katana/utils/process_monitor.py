import psutil
import time
import logging
from threading import Thread, Event

logger = logging.getLogger(__name__)

class ProcessMonitor:
    """Monitors processes and triggers callbacks on state changes"""
    
    def __init__(self, interval=1.0):
        """Initialize with monitoring interval in seconds"""
        self.interval = interval
        self.processes = {}
        self.running = False
        self.stop_event = Event()
        self.monitor_thread = None
    
    def add_process(self, process_name, on_start=None, on_exit=None):
        """Add a process to monitor with callbacks"""
        self.processes[process_name] = {
            'on_start': on_start,
            'on_exit': on_exit,
            'running': False
        }
    
    def remove_process(self, process_name):
        """Remove a process from monitoring"""
        if process_name in self.processes:
            del self.processes[process_name]
    
    def is_process_running(self, process_name):
        """Check if a process is currently running"""
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if process_name.lower() in proc.info['name'].lower():
                    return True
            except:
                continue
        return False
    
    def start_monitoring(self):
        """Start the monitoring thread"""
        if self.running:
            return
        
        self.running = True
        self.stop_event.clear()
        self.monitor_thread = Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        logger.info("Process monitoring started")
    
    def stop_monitoring(self):
        """Stop the monitoring thread"""
        if not self.running:
            return
        
        self.running = False
        self.stop_event.set()
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
            self.monitor_thread = None
        
        logger.info("Process monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running and not self.stop_event.is_set():
            # Check each monitored process
            for process_name, info in self.processes.items():
                currently_running = self.is_process_running(process_name)
                
                # Process started
                if currently_running and not info['running']:
                    logger.info(f"Process started: {process_name}")
                    self.processes[process_name]['running'] = True
                    
                    if info['on_start']:
                        try:
                            info['on_start'](process_name)
                        except Exception as e:
                            logger.error(f"Error in on_start callback for {process_name}: {str(e)}")
                
                # Process exited
                elif not currently_running and info['running']:
                    logger.info(f"Process exited: {process_name}")
                    self.processes[process_name]['running'] = False
                    
                    if info['on_exit']:
                        try:
                            info['on_exit'](process_name)
                        except Exception as e:
                            logger.error(f"Error in on_exit callback for {process_name}: {str(e)}")
            
            # Wait for next check
            time.sleep(self.interval)