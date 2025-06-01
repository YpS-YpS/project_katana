import yaml
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def load_settings(settings_path="config/settings.yaml"):
    """Load global settings from YAML"""
    try:
        with open(settings_path, 'r') as f:
            settings = yaml.safe_load(f)
        return settings
    except Exception as e:
        logger.error(f"Error loading settings: {str(e)}")
        return {}

def load_game_config(game_name):
    """Load configuration for a specific game"""
    config_path = Path("config/games") / f"{game_name.lower().replace(' ', '_')}.yaml"
    
    if not config_path.exists():
        logger.error(f"Game configuration not found: {config_path}")
        return None
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        logger.error(f"Error loading game configuration: {str(e)}")
        return None

def save_game_config(config, game_name=None):
    """Save game configuration to YAML"""
    if not game_name and 'name' in config:
        game_name = config['name']
    
    if not game_name:
        logger.error("No game name specified for configuration")
        return False
    
    config_path = Path("config/games") / f"{game_name.lower().replace(' ', '_')}.yaml"
    
    try:
        # Ensure directory exists
        os.makedirs(config_path.parent, exist_ok=True)
        
        # Save configuration
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        logger.info(f"Game configuration saved: {config_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving game configuration: {str(e)}")
        return False