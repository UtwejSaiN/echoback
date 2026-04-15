import json
from pathlib import Path

DEFAULT_CONFIG = {
    "buffer_duration": 120,      # 2 minutes
    "future_duration": 60,        # 1 minute
    "sample_rate": 16000,         # 16kHz (voice optimized)
    "channels": 1,                # Mono
    "recordings_dir": "recordings"
}

def load_config():
    """Load configuration from file or use defaults"""
    config_path = Path("config/config.json")

    if config_path.exists():
        try:
            with open(config_path) as f:
                user_config = json.load(f)
            # Merge with defaults
            config = {**DEFAULT_CONFIG, **user_config}
            print(f"Loaded config from {config_path}")
            return config
        except Exception as e:
            print(f"Error loading config: {e}, using defaults")

    return DEFAULT_CONFIG.copy()

def save_config(config):
    """Save configuration to file"""
    config_path = Path("config/config.json")
    config_path.parent.mkdir(exist_ok=True)

    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

    print(f"Saved config to {config_path}")
