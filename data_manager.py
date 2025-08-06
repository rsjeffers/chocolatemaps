import json
import os
from datetime import datetime
from typing import List, Dict, Any

class DataManager:
    """
    Manages JSON data storage with cloud-friendly persistent storage.
    Automatically handles both local development and Render cloud deployment.
    """
    
    def __init__(self):
        # Determine the data directory based on environment
        self.data_dir = self._get_data_directory()
        self.pins_file = os.path.join(self.data_dir, "map_pins.json")
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize with existing data or empty list
        self._ensure_file_exists()
    
    def _get_data_directory(self) -> str:
        """
        Get the appropriate data directory based on the environment.
        
        Returns:
            str: Path to the data directory
        """
        # Check if we're running on Render (persistent disk mounted at /opt/render/project/data)
        render_data_dir = "/opt/render/project/data"
        if os.path.exists(render_data_dir):
            return render_data_dir
        
        # For local development, use a local data directory
        local_data_dir = os.path.join(os.getcwd(), "data")
        return local_data_dir
    
    def _ensure_file_exists(self):
        """Ensure the pins file exists, create empty one if not"""
        if not os.path.exists(self.pins_file):
            self._save_pins([])
    
    def _save_pins(self, pins: List[Dict[str, Any]]) -> bool:
        """
        Save pins to JSON file with error handling and atomic writes.
        
        Args:
            pins: List of pin dictionaries to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create a temporary file first (atomic write)
            temp_file = self.pins_file + ".tmp"
            
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(pins, f, indent=2, ensure_ascii=False)
            
            # Move temp file to actual file (atomic operation)
            os.rename(temp_file, self.pins_file)
            return True
            
        except Exception as e:
            print(f"Error saving pins: {e}")
            # Clean up temp file if it exists
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
            return False
    
    def load_pins(self) -> List[Dict[str, Any]]:
        """
        Load pins from JSON file with error handling.
        
        Returns:
            List[Dict]: List of pin dictionaries
        """
        try:
            with open(self.pins_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, FileNotFoundError, Exception) as e:
            print(f"Error loading pins: {e}")
            return []

    def add_pin(self, price: float, location: str, brand: str, fact: str, lat: float, lon: float, is_multi_pack: bool) -> bool:
        """
        Add a new pin to the data.
        
        Args:
            price: Price of the chocolate
            location: Location/store name
            brand: Brand of chocolate
            fact: Additional notes
            lat: Latitude
            lon: Longitude
            is_multi_pack: Whether this pin is part of a multi-pack
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            pins = self.load_pins()
            
            new_pin = {
                'price': price,
                'location': location,
                'brand': brand,
                'fact': fact,
                'lat': lat,
                'lon': lon,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'id': len(pins) + 1,  # Simple ID generation
                'is_multi_pack': is_multi_pack
            }
            
            pins.append(new_pin)
            return self._save_pins(pins)
            
        except Exception as e:
            print(f"Error adding pin: {e}")
            return False
    
    def delete_pin(self, pin_index: int) -> bool:
        """
        Delete a pin by its index.
        
        Args:
            pin_index: Index of the pin to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            pins = self.load_pins()
            
            if 0 <= pin_index < len(pins):
                pins.pop(pin_index)
                return self._save_pins(pins)
            else:
                print(f"Invalid pin index: {pin_index}")
                return False
                
        except Exception as e:
            print(f"Error deleting pin: {e}")
            return False
    
    def clear_all_pins(self) -> bool:
        """
        Clear all pins.
        
        Returns:
            bool: True if successful, False otherwise
        """
        return self._save_pins([])
    
    def get_pin_count(self) -> int:
        """
        Get the total number of pins.
        
        Returns:
            int: Number of pins
        """
        return len(self.load_pins())
    
    def backup_data(self) -> str:
        """
        Create a backup of the current data.
        
        Returns:
            str: Path to the backup file
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(self.data_dir, f"map_pins_backup_{timestamp}.json")
            
            pins = self.load_pins()
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(pins, f, indent=2, ensure_ascii=False)
            
            return backup_file
            
        except Exception as e:
            print(f"Error creating backup: {e}")
            return ""
    
    def get_data_info(self) -> Dict[str, Any]:
        """
        Get information about the data storage.
        
        Returns:
            Dict: Information about data storage
        """
        return {
            'data_directory': self.data_dir,
            'pins_file': self.pins_file,
            'file_exists': os.path.exists(self.pins_file),
            'pin_count': self.get_pin_count(),
            'file_size_bytes': os.path.getsize(self.pins_file) if os.path.exists(self.pins_file) else 0,
            'is_render_environment': self.data_dir.startswith('/opt/render')
        }

# Create a global instance
data_manager = DataManager()
