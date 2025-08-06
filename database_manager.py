import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from typing import List, Dict, Any, Optional
import json

class DatabaseManager:
    """
    Manages PostgreSQL database operations for chocolate shop pins.
    Handles both local development (with fallback to JSON) and Render cloud deployment.
    """
    
    def __init__(self):
        self.connection = None
        self.use_database = self._init_database()
        
        # Fallback to JSON if database is not available (for local development)
        if not self.use_database:
            from data_manager import DataManager
            self.json_manager = DataManager()
            print("Warning: Using JSON fallback. Database not available.")
    
    def _init_database(self) -> bool:
        """
        Initialize database connection.
        
        Returns:
            bool: True if database connection successful, False otherwise
        """
        try:
            # Get database URL from environment (Render automatically provides this)
            database_url = os.getenv('DATABASE_URL')
            
            if not database_url:
                print("No DATABASE_URL found in environment")
                return False
            
            # Connect to database
            self.connection = psycopg2.connect(database_url)
            self.connection.autocommit = True
            
            # Create table if it doesn't exist
            self._create_table()
            
            print("Database connection established successfully")
            return True
            
        except Exception as e:
            print(f"Database connection failed: {e}")
            return False
    
    def _create_table(self):
        """Create the pins table if it doesn't exist"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS chocolate_pins (
                        id SERIAL PRIMARY KEY,
                        price DECIMAL(10, 2) NOT NULL,
                        location VARCHAR(255) NOT NULL,
                        brand VARCHAR(255),
                        fact TEXT,
                        lat DECIMAL(10, 8) NOT NULL,
                        lon DECIMAL(11, 8) NOT NULL,
                        is_multi_pack BOOLEAN DEFAULT FALSE,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                print("Table 'chocolate_pins' created or verified")
        except Exception as e:
            print(f"Error creating table: {e}")
            raise
    
    def load_pins(self) -> List[Dict[str, Any]]:
        """
        Load all pins from database or JSON fallback.
        
        Returns:
            List[Dict]: List of pin dictionaries
        """
        if not self.use_database:
            return self.json_manager.load_pins()
        
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT id, price, location, brand, fact, lat, lon, is_multi_pack,
                           TO_CHAR(timestamp, 'YYYY-MM-DD HH24:MI:SS') as timestamp
                    FROM chocolate_pins 
                    ORDER BY created_at DESC
                """)
                
                rows = cursor.fetchall()
                
                # Convert to list of dictionaries
                pins = []
                for row in rows:
                    pin = dict(row)
                    # Convert Decimal to float for JSON serialization
                    pin['price'] = float(pin['price'])
                    pin['lat'] = float(pin['lat'])
                    pin['lon'] = float(pin['lon'])
                    pins.append(pin)
                
                return pins
                
        except Exception as e:
            print(f"Error loading pins from database: {e}")
            return []

    def add_pin(self, price: float, location: str, brand: str, fact: str, lat: float, lon: float, is_multi_pack: bool) -> bool:
        """
        Add a new pin to database or JSON fallback.
        
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
        if not self.use_database:
            return self.json_manager.add_pin(price, location, brand, fact, lat, lon, is_multi_pack)
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO chocolate_pins (price, location, brand, fact, lat, lon, is_multi_pack)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (price, location, brand, fact, lat, lon, is_multi_pack))
                return True
                
        except Exception as e:
            print(f"Error adding pin to database: {e}")
            return False
    
    def delete_pin(self, pin_id: int) -> bool:
        """
        Delete a pin by its ID.
        
        Args:
            pin_id: ID of the pin to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.use_database:
            # For JSON fallback, pin_id is actually the index
            return self.json_manager.delete_pin(pin_id)
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("DELETE FROM chocolate_pins WHERE id = %s", (pin_id,))
                return cursor.rowcount > 0
                
        except Exception as e:
            print(f"Error deleting pin from database: {e}")
            return False
    
    def clear_all_pins(self) -> bool:
        """
        Clear all pins from database or JSON fallback.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.use_database:
            return self.json_manager.clear_all_pins()
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("DELETE FROM chocolate_pins")
                return True
                
        except Exception as e:
            print(f"Error clearing pins from database: {e}")
            return False
    
    def get_pin_count(self) -> int:
        """
        Get the total number of pins.
        
        Returns:
            int: Number of pins
        """
        if not self.use_database:
            return self.json_manager.get_pin_count()
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM chocolate_pins")
                return cursor.fetchone()[0]
                
        except Exception as e:
            print(f"Error getting pin count from database: {e}")
            return 0
    
    def get_data_info(self) -> Dict[str, Any]:
        """
        Get information about the data storage.
        
        Returns:
            Dict: Information about data storage
        """
        if not self.use_database:
            info = self.json_manager.get_data_info()
            info['storage_type'] = 'JSON (fallback)'
            return info
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM chocolate_pins")
                pin_count = cursor.fetchone()[0]
                
                return {
                    'storage_type': 'PostgreSQL Database',
                    'database_url': os.getenv('DATABASE_URL', 'Not set'),
                    'pin_count': pin_count,
                    'table_name': 'chocolate_pins',
                    'connection_status': 'Connected' if self.connection else 'Disconnected'
                }
                
        except Exception as e:
            return {
                'storage_type': 'PostgreSQL Database (Error)',
                'error': str(e),
                'connection_status': 'Error'
            }
    
    def migrate_from_json(self, json_file_path: str) -> bool:
        """
        Migrate data from JSON file to database.
        
        Args:
            json_file_path: Path to the JSON file to migrate from
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.use_database:
            print("Cannot migrate to database: database not available")
            return False
        
        try:
            # Load data from JSON file
            with open(json_file_path, 'r', encoding='utf-8') as f:
                pins = json.load(f)
            
            # Insert each pin into database
            for pin in pins:
                self.add_pin(
                    price=pin.get('price', 0.0),
                    location=pin.get('location', ''),
                    brand=pin.get('brand', ''),
                    fact=pin.get('fact', ''),
                    lat=pin.get('lat', 0.0),
                    lon=pin.get('lon', 0.0),
                    is_multi_pack=pin.get('is_multi_pack', False)
                )
            
            print(f"Successfully migrated {len(pins)} pins from JSON to database")
            return True
            
        except Exception as e:
            print(f"Error migrating from JSON: {e}")
            return False
    
    def __del__(self):
        """Close database connection when object is destroyed"""
        if self.connection:
            try:
                self.connection.close()
            except:
                pass

# Create a global instance
database_manager = DatabaseManager()
