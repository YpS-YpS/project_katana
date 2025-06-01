import os
import time
import subprocess
import logging
import psutil
from pathlib import Path

logger = logging.getLogger(__name__)

class GameController:
    """Controls game processes (launch, close, etc.)"""
    
    def __init__(self, settings_path="config/settings.yaml"):
        """Initialize with global settings"""
        import yaml
        try:
            with open(settings_path, 'r') as f:
                self.settings = yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
            self.settings = {}
        
        self.current_game = None
        self.process = None
    
    def launch_steam_game(self, app_id, launch_options=None):
        """Launch a game through Steam"""
        steam_path = self.settings.get('steam_path')
        if not steam_path:
            raise ValueError("Steam path not configured")
        
        steam_exe = os.path.join(steam_path, 'steam.exe')
        if not os.path.exists(steam_exe):
            raise FileNotFoundError(f"Steam executable not found: {steam_exe}")
        
        # Build Steam launch command with proper quoting
        cmd = [steam_exe]
        
        # Add global Steam launch options
        steam_launch_opts = self.settings.get('steam_launch_options')
        if steam_launch_opts:
            cmd.extend(steam_launch_opts.split())
        
        # Add the app launch command
        cmd.extend(['-applaunch', str(app_id)])
        
        # Add game-specific launch options
        if launch_options:
            if isinstance(launch_options, str):
                cmd.extend(launch_options.split())
            elif isinstance(launch_options, list):
                cmd.extend(launch_options)
        
        logger.info(f"Launching Steam game {app_id}")
        logger.debug(f"Command: {' '.join(cmd)}")
        
        try:
            # Launch the game using subprocess with proper handling
            self.process = subprocess.Popen(cmd, 
                                          stdout=subprocess.PIPE, 
                                          stderr=subprocess.PIPE,
                                          creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            
            logger.info(f"Steam launch command executed for app {app_id}")
            return self.process
        except Exception as e:
            logger.error(f"Failed to launch Steam game: {e}")
            raise
    
    def launch_game_direct(self, exe_path, args=None):
        """Launch a game directly by its executable"""
        if not os.path.exists(exe_path):
            raise FileNotFoundError(f"Game executable not found: {exe_path}")
        
        cmd = [exe_path]
        if args:
            if isinstance(args, list):
                cmd.extend(args)
            elif isinstance(args, str):
                cmd.extend(args.split())
        
        logger.info(f"Launching game directly: {exe_path}")
        logger.debug(f"Command: {' '.join(cmd)}")
        
        try:
            # Launch the game
            self.process = subprocess.Popen(cmd,
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE)
            return self.process
        except Exception as e:
            logger.error(f"Failed to launch game directly: {e}")
            raise
    
    def launch_game(self, game_config):
        """Launch a game based on its configuration"""
        self.current_game = game_config
        
        if game_config['platform'] == 'steam':
            return self.launch_steam_game(
                game_config['app_id'],
                game_config['config'].get('launch_options')
            )
        else:
            # For direct launch, find the executable
            exe_name = game_config['config'].get('exe_name')
            if not exe_name:
                raise ValueError(f"No executable name specified for {game_config['config']['name']}")
            
            exe_path = Path(game_config['path']) / exe_name
            if not exe_path.exists():
                # Try searching for the executable
                for root, dirs, files in os.walk(game_config['path']):
                    if exe_name in files:
                        exe_path = Path(root) / exe_name
                        break
            
            if not exe_path.exists():
                raise FileNotFoundError(f"Could not find executable {exe_name} in {game_config['path']}")
            
            return self.launch_game_direct(
                str(exe_path),
                game_config['config'].get('launch_options')
            )
    
    def is_game_running(self, process_name=None):
        """Check if a game is currently running"""
        if not process_name and self.current_game:
            process_name = self.current_game['config'].get('process_name') or Path(self.current_game['config'].get('exe_name', '')).stem
        
        if not process_name:
            return False
        
        # Handle different process name formats
        possible_names = [
            process_name,
            f"{process_name}.exe",
            process_name.replace('.exe', ''),
        ]
        
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                proc_name = proc.info['name'].lower()
                for name in possible_names:
                    if name.lower() in proc_name:
                        logger.debug(f"Found running process: {proc.info['name']} (PID: {proc.info['pid']})")
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return False
    
    def close_game(self, process_name=None, force=False):
        """Close a running game"""
        if not process_name and self.current_game:
            process_name = self.current_game['config'].get('process_name') or Path(self.current_game['config'].get('exe_name', '')).stem
        
        if not process_name:
            logger.error("No process name specified for game closure")
            return False
        
        logger.info(f"Attempting to close game: {process_name}")
        
        # Handle different process name formats
        possible_names = [
            process_name,
            f"{process_name}.exe",
            process_name.replace('.exe', ''),
        ]
        
        closed_any = False
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                proc_name = proc.info['name'].lower()
                for name in possible_names:
                    if name.lower() in proc_name:
                        if force:
                            proc.kill()
                            logger.info(f"Killed process: {proc.info['name']} (PID: {proc.info['pid']})")
                        else:
                            proc.terminate()
                            logger.info(f"Terminated process: {proc.info['name']} (PID: {proc.info['pid']})")
                        closed_any = True
                        break
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                logger.debug(f"Process access error: {e}")
                continue
        
        return closed_any
    
    def wait_for_game_to_start(self, timeout=60, process_name=None):
        """Wait for the game to start"""
        if not process_name and self.current_game:
            process_name = self.current_game['config'].get('process_name') or Path(self.current_game['config'].get('exe_name', '')).stem
        
        if not process_name:
            logger.error("No process name specified for waiting")
            return False
        
        logger.info(f"Waiting for game to start: {process_name}")
        
        start_time = time.time()
        check_interval = 2  # Check every 2 seconds
        
        while time.time() - start_time < timeout:
            if self.is_game_running(process_name):
                elapsed = time.time() - start_time
                logger.info(f"Game started: {process_name} (took {elapsed:.1f}s)")
                return True
            
            logger.debug(f"Game not running yet, waiting... ({time.time() - start_time:.1f}s)")
            time.sleep(check_interval)
        
        logger.warning(f"Timeout waiting for game to start: {process_name}")
        return False
    
    def wait_for_game_to_close(self, timeout=60, process_name=None):
        """Wait for the game to close"""
        if not process_name and self.current_game:
            process_name = self.current_game['config'].get('process_name') or Path(self.current_game['config'].get('exe_name', '')).stem
        
        if not process_name:
            logger.error("No process name specified for waiting")
            return False
        
        logger.info(f"Waiting for game to close: {process_name}")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            if not self.is_game_running(process_name):
                elapsed = time.time() - start_time
                logger.info(f"Game closed: {process_name} (took {elapsed:.1f}s)")
                return True
            time.sleep(1)
        
        logger.warning(f"Timeout waiting for game to close: {process_name}")
        return False
    
    def get_running_games(self):
        """Get list of currently running games"""
        running_games = []
        
        # Check all configured games
        from katana.core.game_finder import GameFinder
        finder = GameFinder()
        all_games = finder.find_all_games()
        
        for game_name, game_info in all_games.items():
            process_name = game_info['config'].get('process_name')
            if process_name and self.is_game_running(process_name):
                running_games.append(game_name)
        
        return running_games