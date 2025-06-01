import os
import yaml
import logging
from pathlib import Path
import winreg  # For Windows registry access

logger = logging.getLogger(__name__)

class GameFinder:
    """Utility to find installed games on the system"""
    
    def __init__(self, settings_path="config/settings.yaml"):
        """Initialize with global settings"""
        self.settings = self._load_settings(settings_path)
        self.found_games = {}
    
    def _load_settings(self, settings_path):
        """Load global settings from YAML"""
        try:
            if not os.path.exists(settings_path):
                logger.warning(f"Settings file not found: {settings_path}")
                return self._get_default_settings()
            
            with open(settings_path, 'r') as f:
                settings = yaml.safe_load(f)
                
            if settings is None:
                logger.warning(f"Settings file is empty: {settings_path}")
                return self._get_default_settings()
                
            return settings
        except Exception as e:
            logger.error(f"Error loading settings: {str(e)}")
            return self._get_default_settings()
    
    def _get_default_settings(self):
        """Get default settings if file is missing or corrupted"""
        return {
            'steam_path': 'C:/Program Files (x86)/Steam',
            'epic_path': 'C:/Program Files/Epic Games',
            'steam_launch_options': '',
            'screenshot_dir': 'output/screenshots',
            'log_level': 'INFO',
            'template_matching_threshold': 0.8,
            'input_delay': 0.5,
            'timeout': 300
        }
    
    def find_steam_games(self):
        """Find installed Steam games"""
        steam_path = self.settings.get('steam_path')
        if not steam_path or not os.path.exists(steam_path):
            logger.warning(f"Steam path not found: {steam_path}")
            return {}
        
        # Get Steam library folders
        library_folders = self._get_steam_libraries(steam_path)
        
        # Scan each library folder for game configs
        games = {}
        config_dir = Path('config/games')
        
        if not config_dir.exists():
            logger.warning(f"Game config directory not found: {config_dir}")
            return {}
        
        for library in library_folders:
            apps_path = os.path.join(library, 'steamapps')
            if not os.path.exists(apps_path):
                continue
            
            # Load game configs
            for config_file in config_dir.glob('*.yaml'):
                try:
                    with open(config_file, 'r') as f:
                        game_config = yaml.safe_load(f)
                    
                    # Check if config loaded properly
                    if game_config is None:
                        logger.warning(f"Empty or invalid config file: {config_file}")
                        continue
                    
                    if not isinstance(game_config, dict):
                        logger.warning(f"Invalid config format in {config_file}: expected dict, got {type(game_config)}")
                        continue
                    
                    # Check if it's a steam game
                    if game_config.get('type') != 'steam':
                        continue
                    
                    app_id = game_config.get('app_id')
                    if not app_id:
                        logger.warning(f"No app_id found in {config_file}")
                        continue
                    
                    # Check if game is installed
                    acf_path = os.path.join(apps_path, f'appmanifest_{app_id}.acf')
                    if os.path.exists(acf_path):
                        install_dir = self._parse_acf_file(acf_path)
                        if install_dir:
                            game_path = os.path.join(apps_path, 'common', install_dir)
                            if os.path.exists(game_path):
                                games[game_config['name']] = {
                                    'path': game_path,
                                    'config': game_config,
                                    'platform': 'steam',
                                    'app_id': app_id
                                }
                                logger.info(f"Found Steam game: {game_config['name']} at {game_path}")
                            else:
                                logger.warning(f"Game directory not found: {game_path}")
                
                except Exception as e:
                    logger.error(f"Error processing config file {config_file}: {str(e)}")
                    continue
        
        return games
    
    def _get_steam_libraries(self, steam_path):
        """Get all Steam library folders"""
        libraries = [steam_path]
        
        # Check for additional library folders in libraryfolders.vdf
        vdf_path = os.path.join(steam_path, 'steamapps', 'libraryfolders.vdf')
        if os.path.exists(vdf_path):
            try:
                with open(vdf_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Simple parsing of VDF format
                import re
                paths = re.findall(r'"path"\s*"([^"]+)"', content)
                for path in paths:
                    path = path.replace('\\\\', '\\')
                    if path not in libraries and os.path.exists(path):
                        libraries.append(path)
            except Exception as e:
                logger.error(f"Error parsing libraryfolders.vdf: {str(e)}")
        
        return libraries
    
    def _parse_acf_file(self, acf_path):
        """Parse Steam ACF file to get installdir"""
        try:
            with open(acf_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            import re
            match = re.search(r'"installdir"\s*"([^"]+)"', content)
            if match:
                return match.group(1)
        except Exception as e:
            logger.error(f"Error parsing ACF file {acf_path}: {str(e)}")
        
        return None
    
    def find_epic_games(self):
        """Find installed Epic Games"""
        epic_path = self.settings.get('epic_path')
        if not epic_path or not os.path.exists(epic_path):
            logger.warning(f"Epic Games path not found: {epic_path}")
            return {}
        
        # Implementation for Epic Games would go here
        # For now, return empty dict
        return {}
    
    def find_games_by_registry(self):
        """Find games by checking Windows registry"""
        games = {}
        
        try:
            import platform
            if platform.system() != 'Windows':
                logger.info("Registry search only available on Windows")
                return {}
            
            # Check Uninstall keys in registry
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall') as key:
                for i in range(0, winreg.QueryInfoKey(key)[0]):
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, subkey_name) as subkey:
                            try:
                                name = winreg.QueryValueEx(subkey, 'DisplayName')[0]
                                install_location = winreg.QueryValueEx(subkey, 'InstallLocation')[0]
                                
                                # Match with our game configs
                                config_dir = Path('config/games')
                                if config_dir.exists():
                                    for config_file in config_dir.glob('*.yaml'):
                                        try:
                                            with open(config_file, 'r') as f:
                                                game_config = yaml.safe_load(f)
                                                
                                            if game_config and isinstance(game_config, dict):
                                                if game_config.get('name') and game_config.get('name') in name:
                                                    games[game_config['name']] = {
                                                        'path': install_location,
                                                        'config': game_config,
                                                        'platform': 'registry',
                                                    }
                                                    logger.info(f"Found game in registry: {game_config['name']} at {install_location}")
                                        except Exception as e:
                                            logger.debug(f"Error checking config {config_file}: {str(e)}")
                                            continue
                            except FileNotFoundError:
                                # Missing DisplayName or InstallLocation
                                continue
                    except Exception as e:
                        logger.debug(f"Error accessing registry key {i}: {str(e)}")
                        continue
        except Exception as e:
            logger.warning(f"Failed to access Windows registry: {str(e)}")
        
        return games
    
    def find_all_games(self):
        """Find all games from configured sources"""
        self.found_games = {}
        
        try:
            # Find games from different sources
            logger.info("Searching for Steam games...")
            steam_games = self.find_steam_games()
            
            logger.info("Searching for Epic Games...")
            epic_games = self.find_epic_games()
            
            logger.info("Searching registry...")
            registry_games = self.find_games_by_registry()
            
            # Combine results
            self.found_games.update(steam_games)
            self.found_games.update(epic_games)
            self.found_games.update(registry_games)
            
            logger.info(f"Total games found: {len(self.found_games)}")
            
        except Exception as e:
            logger.error(f"Error in find_all_games: {str(e)}")
        
        return self.found_games
    
    def get_game_config(self, game_name):
        """Get configuration for a specific game"""
        if game_name in self.found_games:
            return self.found_games[game_name]
        return None