import cv2
import numpy as np
import logging
import os
import time
from datetime import datetime
from pathlib import Path
import threading

logger = logging.getLogger(__name__)

class ScreenAnalyzer:
    """Analyzes game screen using pure computer vision (no OCR)"""
    
    def __init__(self, settings_path="config/settings.yaml"):
        """Initialize with global settings"""
        import yaml
        with open(settings_path, 'r') as f:
            self.settings = yaml.safe_load(f)
        
        self.threshold = self.settings.get('template_matching_threshold', 0.8)
        self.screenshot_dir = self.settings.get('screenshot_dir', 'output/screenshots')
        
        # Ensure screenshot directory exists
        os.makedirs(self.screenshot_dir, exist_ok=True)
        
        # Thread lock for screen capture
        self._capture_lock = threading.Lock()
        
        # Initialize screen capture method
        self._initialize_capture()
    
    def _initialize_capture(self):
        """Initialize the appropriate screen capture method"""
        # Try MSS first, fall back to PyAutoGUI if there are issues
        try:
            import mss
            # Test MSS with a simple capture
            with mss.mss() as sct:
                monitor = sct.monitors[1]  # Primary monitor
                test_capture = sct.grab(monitor)
                # If we get here, MSS works
                self.capture_method = 'mss'
                logger.info("Using MSS for screen capture")
        except Exception as e:
            logger.warning(f"MSS failed, falling back to PyAutoGUI: {e}")
            try:
                import pyautogui
                # Test PyAutoGUI
                test_screenshot = pyautogui.screenshot()
                self.capture_method = 'pyautogui'
                logger.info("Using PyAutoGUI for screen capture")
            except ImportError:
                raise ImportError("Either MSS or PyAutoGUI is required for screen capture")
    
    def capture_screen(self, region=None):
        """Capture the current screen or a region of it (thread-safe)"""
        with self._capture_lock:
            return self._capture_screen_internal(region)
    
    def _capture_screen_internal(self, region=None):
        """Internal screen capture method"""
        try:
            if self.capture_method == 'mss':
                return self._capture_with_mss(region)
            elif self.capture_method == 'pyautogui':
                return self._capture_with_pyautogui(region)
        except Exception as e:
            logger.error(f"Screen capture failed with {self.capture_method}, trying fallback: {e}")
            # Try the other method as fallback
            try:
                if self.capture_method == 'mss':
                    logger.info("Falling back to PyAutoGUI")
                    self.capture_method = 'pyautogui'
                    return self._capture_with_pyautogui(region)
                else:
                    logger.info("Falling back to MSS")
                    self.capture_method = 'mss'
                    return self._capture_with_mss(region)
            except Exception as e2:
                logger.error(f"Both capture methods failed: {e2}")
                raise
    
    def _capture_with_mss(self, region=None):
        """Capture screen using MSS"""
        import mss
        
        # Create a new MSS instance for this thread
        with mss.mss() as sct:
            # Get dynamic monitor
            game_process = getattr(self, 'current_game_process', None)
            monitor_index = self._get_game_monitor(game_process)
            
            if region:
                # Convert normalized region to pixel coordinates
                monitor = sct.monitors[monitor_index]  # Dynamic monitor
                x, y, right, bottom = region
                width, height = monitor['width'], monitor['height']
                
                x = int(x * width)
                y = int(y * height)
                right = int(right * width)
                bottom = int(bottom * height)
                
                sct_region = {'top': y, 'left': x, 'width': right - x, 'height': bottom - y}
                sct_img = sct.grab(sct_region)
            else:
                sct_img = sct.grab(sct.monitors[monitor_index])  # Dynamic monitor
            
            # Convert to numpy array
            img = np.array(sct_img)
            return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    
    def _capture_with_pyautogui(self, region=None):
        """Capture screen using PyAutoGUI"""
        import pyautogui
        
        if region:
            # Convert normalized region to pixel coordinates
            screen_width, screen_height = pyautogui.size()
            x, y, right, bottom = region
            
            x = int(x * screen_width)
            y = int(y * screen_height)
            right = int(right * screen_width)
            bottom = int(bottom * screen_height)
            
            width, height = right - x, bottom - y
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
        else:
            screenshot = pyautogui.screenshot()
        
        # Convert PIL Image to numpy array
        img = np.array(screenshot)
        return cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    
    def save_screenshot(self, name=None):
        """Capture and save a screenshot (thread-safe)"""
        try:
            if not name:
                name = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            else:
                if not name.endswith('.png'):
                    name = f"{name}.png"
            
            img = self.capture_screen()
            path = os.path.join(self.screenshot_dir, name)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            success = cv2.imwrite(path, img)
            
            if success:
                logger.info(f"Screenshot saved: {path}")
                return path
            else:
                logger.error(f"Failed to save screenshot: {path}")
                return None
                
        except Exception as e:
            logger.error(f"Error saving screenshot: {e}")
            return None
    
    def match_template(self, template_path, screen=None, region=None, threshold=None):
        """Check if a template matches the current screen"""
        if threshold is None:
            threshold = self.threshold
        
        # Load template
        if not Path(template_path).exists():
            logger.error(f"Template not found: {template_path}")
            return False, None
        
        template = cv2.imread(template_path)
        if template is None:
            logger.error(f"Failed to load template: {template_path}")
            return False, None
        
        # Capture screen if not provided
        if screen is None:
            screen = self.capture_screen(region)
        
        # Ensure template isn't larger than screen
        if template.shape[0] > screen.shape[0] or template.shape[1] > screen.shape[1]:
            logger.error(f"Template larger than screen region: {template_path}")
            return False, None
        
        # Match template
        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= threshold:
            # Calculate the center point of the match
            match_h, match_w = template.shape[:2]
            center_x = max_loc[0] + match_w // 2
            center_y = max_loc[1] + match_h // 2
            
            logger.debug(f"Template matched: {template_path} (confidence: {max_val:.2f})")
            return True, (center_x, center_y)
        else:
            logger.debug(f"Template not matched: {template_path} (confidence: {max_val:.2f})")
            return False, None
    
    def wait_for_template(self, template_path, timeout=30, region=None, threshold=None):
        """Wait for a template to appear on screen"""
        if threshold is None:
            threshold = self.threshold
        
        logger.info(f"Waiting for template: {template_path}")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                matched, location = self.match_template(template_path, region=region, threshold=threshold)
                if matched:
                    return True, location
            except Exception as e:
                logger.warning(f"Error during template matching: {e}")
            
            time.sleep(0.5)
        
        logger.warning(f"Timeout waiting for template: {template_path}")
        return False, None
    
    def wait_for_any_template(self, template_paths, timeout=30, region=None, threshold=None):
        """Wait for any of multiple templates to appear"""
        if threshold is None:
            threshold = self.threshold
        
        logger.info(f"Waiting for any template: {template_paths}")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            for template_path in template_paths:
                try:
                    matched, location = self.match_template(template_path, region=region, threshold=threshold)
                    if matched:
                        return True, (template_path, location)
                except Exception as e:
                    logger.warning(f"Error matching template {template_path}: {e}")
                    continue
            
            time.sleep(0.5)
        
        logger.warning(f"Timeout waiting for any template: {template_paths}")
        return False, None
    
    def find_all_templates(self, template_path, screen=None, region=None, threshold=None):
        """Find all instances of a template on screen"""
        if threshold is None:
            threshold = self.threshold
        
        # Load template
        if not Path(template_path).exists():
            logger.error(f"Template not found: {template_path}")
            return []
        
        template = cv2.imread(template_path)
        if template is None:
            logger.error(f"Failed to load template: {template_path}")
            return []
        
        # Capture screen if not provided
        if screen is None:
            screen = self.capture_screen(region)
        
        # Match template
        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        
        # Find all matches above threshold
        locations = np.where(result >= threshold)
        matches = []
        
        match_h, match_w = template.shape[:2]
        
        for pt in zip(*locations[::-1]):  # Switch columns and rows
            center_x = pt[0] + match_w // 2
            center_y = pt[1] + match_h // 2
            confidence = result[pt[1], pt[0]]
            matches.append((center_x, center_y, confidence))
        
        logger.debug(f"Found {len(matches)} matches for template: {template_path}")
        return matches
    
    def wait_for_screen_change(self, timeout=30, region=None, threshold=0.95):
        """Wait for the screen to change significantly"""
        logger.info("Waiting for screen change...")
        
        try:
            # Capture initial screen
            initial_screen = self.capture_screen(region)
            
            start_time = time.time()
            while time.time() - start_time < timeout:
                current_screen = self.capture_screen(region)
                
                # Compare screens using template matching
                result = cv2.matchTemplate(current_screen, initial_screen, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                
                # If screens are significantly different
                if max_val < threshold:
                    logger.info(f"Screen changed (similarity: {max_val:.2f})")
                    return True
                
                time.sleep(0.5)
            
            logger.warning("Timeout waiting for screen change")
            return False
        except Exception as e:
            logger.error(f"Error waiting for screen change: {e}")
            return False
    
    def create_template_from_region(self, region, name):
        """Capture a region and save it as a template"""
        try:
            screen = self.capture_screen()
            
            # Convert normalized region to pixel coordinates
            height, width = screen.shape[:2]
            x, y, right, bottom = region
            
            x = int(x * width)
            y = int(y * height)
            right = int(right * width)
            bottom = int(bottom * height)
            
            # Extract region
            template = screen[y:bottom, x:right]
            
            # Save template
            template_path = Path("templates") / "screens" / f"{name}.png"
            template_path.parent.mkdir(parents=True, exist_ok=True)
            
            success = cv2.imwrite(str(template_path), template)
            
            if success:
                logger.info(f"Template created: {template_path}")
                return str(template_path)
            else:
                logger.error(f"Failed to create template: {template_path}")
                return None
        
        except Exception as e:
            logger.error(f"Error creating template: {e}")
            return None
    
    def set_current_game(self, game_process_name):
        """Set current game for monitor detection"""
        self.current_game_process = game_process_name

    def _get_game_monitor(self, game_process_name=None):
        """Dynamically find which monitor has the active game window"""
        import mss
        try:
            if game_process_name:
                import pyautogui
                windows = pyautogui.getAllWindows()
                
                for window in windows:
                    if game_process_name.lower() in window.title.lower():
                        center_x = window.left + window.width // 2
                        center_y = window.top + window.height // 2
                        
                        with mss.mss() as sct:
                            for i, monitor in enumerate(sct.monitors[1:], 1):
                                if (monitor['left'] <= center_x <= monitor['left'] + monitor['width'] and
                                    monitor['top'] <= center_y <= monitor['top'] + monitor['height']):
                                    logger.info(f"Game found on monitor {i}")
                                    return i
            
            return self.settings.get('monitor_index', 1)
            
        except Exception as e:
            logger.warning(f"Monitor detection failed: {e}")
            return 1