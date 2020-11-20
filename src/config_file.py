from pathlib import Path

root_path = Path(__file__).parent.parent.absolute()
config_path = root_path / 'configs'


Path.mkdir(root_path, exist_ok=True, parents=True)
Path.mkdir(config_path, exist_ok=True, parents=True)