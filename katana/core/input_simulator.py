import time
import logging
import platform
import pyautogui

logger = logging.getLogger(__name__)

class InputSimulator:
    """Simulates keyboard and mouse inputs for game automation"""
    
    def __init__(self, settings_path="config/settings.yaml"):
        """Initialize with global settings"""
        import yaml
        with open(settings_path, 'r') as f:
            self.settings = yaml.safe_load(f)
        
        self.default_delay = self.settings.get('input_delay', 0.5)
        self._initialize_backend()
    
    def _initialize_backend(self):
        """Initialize the appropriate input backend based on platform"""
        system = platform.system()
        
        if system == 'Windows':
            # Use pyautogui for cross-platform compatibility
            try:
                import pyautogui
                self.backend = 'pyautogui'
                self.input_module = pyautogui
                pyautogui.FAILSAFE = False  # Disable fail-safe
                logger.info("Using PyAutoGUI for input simulation")
            except ImportError:
                raise ImportError("PyAutoGUI is required for input simulation. Install it with 'pip install pyautogui'")
        elif system == 'Linux':
            # Try to use xdotool on Linux
            try:
                import subprocess
                subprocess.run(['xdotool', '--version'], check=True)
                self.backend = 'xdotool'
                logger.info("Using xdotool for input simulation")
            except:
                # Fall back to PyAutoGUI
                try:
                    import pyautogui
                    self.backend = 'pyautogui'
                    self.input_module = pyautogui
                    pyautogui.FAILSAFE = False
                    logger.info("Using PyAutoGUI for input simulation")
                except ImportError:
                    raise ImportError("PyAutoGUI is required for input simulation. Install it with 'pip install pyautogui'")
        else:
            # Default to PyAutoGUI for other platforms
            try:
                import pyautogui
                self.backend = 'pyautogui'
                self.input_module = pyautogui
                pyautogui.FAILSAFE = False
                logger.info("Using PyAutoGUI for input simulation")
            except ImportError:
                raise ImportError("PyAutoGUI is required for input simulation. Install it with 'pip install pyautogui'")
    
    def press_key(self, key, delay=None):
        """Press and release a key"""
        delay = delay if delay is not None else self.default_delay
        
        logger.debug(f"Pressing key: {key}")
        
        if self.backend == 'pyautogui':
            self.input_module.press(key)
        elif self.backend == 'xdotool':
            import subprocess
            subprocess.run(['xdotool', 'key', key])
        
        time.sleep(delay)
    
    def hold_key(self, key, duration=1.0):
        """Hold a key for the specified duration"""
        logger.debug(f"Holding key {key} for {duration}s")
        
        if self.backend == 'pyautogui':
            self.input_module.keyDown(key)
            time.sleep(duration)
            self.input_module.keyUp(key)
        elif self.backend == 'xdotool':
            import subprocess
            subprocess.run(['xdotool', 'keydown', key])
            time.sleep(duration)
            subprocess.run(['xdotool', 'keyup', key])
    
    def type_text(self, text, delay=None):
        """Type a string of text"""
        delay = delay if delay is not None else self.default_delay
        
        logger.debug(f"Typing text: {text}")
        
        if self.backend == 'pyautogui':
            self.input_module.write(text)
        elif self.backend == 'xdotool':
            import subprocess
            subprocess.run(['xdotool', 'type', text])
        
        time.sleep(delay)
    
    def mouse_move(self, x, y, duration=0.5):
        """Move mouse to specified coordinates"""
        logger.debug(f"Moving mouse to ({x}, {y})")
        
        if self.backend == 'pyautogui':
            self.input_module.moveTo(x, y, duration=duration)
        elif self.backend == 'xdotool':
            import subprocess
            subprocess.run(['xdotool', 'mousemove', str(x), str(y)])
    
    def mouse_click(self, x, y, button='left', delay=None, move_duration=0.5, pre_click_delay=0.3, post_click_delay=0.5):
        """Click at the specified coordinates with smooth movement and delays
        
        Args:
            x (int): X coordinate
            y (int): Y coordinate
            button (str): Mouse button ('left', 'middle', 'right')
            delay (float): Deprecated, use post_click_delay instead
            move_duration (float): Time to move mouse to target in seconds
            pre_click_delay (float): Delay before clicking in seconds
            post_click_delay (float): Delay after clicking in seconds
            
        Returns:
            bool: True if click was performed
        """
        # Use delay parameter for backwards compatibility
        if delay is not None:
            post_click_delay = delay
        
        logger.info(f"🖱️ Moving mouse to ({x}, {y}) and clicking with {button} button")
        
        try:
            # Get current mouse position for logging
            current_x, current_y = pyautogui.position()
            logger.debug(f"Mouse moving from ({current_x}, {current_y}) to ({x}, {y})")
            
            # Move mouse smoothly to target position
            pyautogui.moveTo(x, y, duration=move_duration)
            logger.debug(f"Mouse moved to target position in {move_duration}s")
            
            # Wait before clicking
            time.sleep(pre_click_delay)
            logger.debug(f"Pre-click delay: {pre_click_delay}s")
            
            # Perform the click
            pyautogui.click(x=x, y=y, button=button)
            logger.debug(f"Click performed at ({x}, {y})")
            
            # Wait after clicking
            time.sleep(post_click_delay)
            logger.debug(f"Post-click delay: {post_click_delay}s")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Click failed: {e}")
            return False