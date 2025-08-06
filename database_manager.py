import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file for local development
load_dotenv()

class DatabaseManager:
    """
    Manages PostgreSQL database operations for chocolate price pins.
    Handles both local development (with local database) and Render cloud
    deployment.
    """
    
    def __init__(self):
        self.connection = None
        self.use_database = self._init_database()
    
    def _init_database(self) -> bool:
        """
        Initialize database connection.
        
        Returns:
            bool: True if database connection successful, False otherwise
        """
        try:
            # Get database URL from environment
            # (Render automatically provides this, otherwise use local .env)
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
    
    def test_connection(self) -> bool:
        """
        Test if the database connection is working.
        
        Returns:
            bool: True if connection is working, False otherwise
        """
        try:
            if not self.connection or self.connection.closed:
                return False
            
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                return True
                
        except Exception as e:
            print(f"Database connection test failed: {e}")
            return False
    
    def _create_table(self):
        """Create the pins table if it doesn't exist and ensure all columns are
        present"""
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
                
                # Add columns that might not exist in older versions
                cursor.execute("""
                    ALTER TABLE chocolate_pins 
                    ADD COLUMN IF NOT EXISTS is_multi_pack BOOLEAN DEFAULT FALSE
                """)
                
                print("Table 'chocolate_pins' created or verified with all columns")
        except Exception as e:
            print(f"Error creating table: {e}")
            raise
    
    def load_pins(self) -> List[Dict[str, Any]]:
        """
        Load all pins from database.
        
        Returns:
            List[Dict]: List of pin dictionaries
        """
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
                    # Ensure is_multi_pack has a default value
                    if pin.get('is_multi_pack') is None:
                        pin['is_multi_pack'] = False
                    pins.append(pin)
                
                return pins
                
        except Exception as e:
            raise Exception(f"Error loading pins from database: {e}")

    def add_pin(self, price: float, location: str, brand: str, fact: str, lat: float, lon: float, is_multi_pack: bool) -> bool:
        """
        Add a new pin to database.
        
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
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO chocolate_pins (price, location, brand, fact, lat, lon, is_multi_pack)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (price, location, brand, fact, lat, lon, is_multi_pack))
                return True
                
        except Exception as e:
            print(f"Error adding pin to database: {e}")
            print(f"Database connection status: {self.connection.closed if self.connection else 'No connection'}")
            return False

    def delete_pin(self, pin_id: int) -> bool:
        """
        Delete a pin by its ID.
        
        Args:
            pin_id: ID of the pin to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
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
        try:
            # Check connection status
            if not self.connection or self.connection.closed:
                return {
                    'storage_type': 'PostgreSQL Database (Disconnected)',
                    'database_url': os.getenv('DATABASE_URL', 'Not set'),
                    'connection_status': 'Disconnected',
                    'error': 'Database connection is closed',
                    'pin_count': 0
                }
            
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM chocolate_pins")
                pin_count = cursor.fetchone()[0]
                
                # Test connection with a simple query
                cursor.execute("SELECT 1")
                cursor.fetchone()
                
                return {
                    'storage_type': 'PostgreSQL Database',
                    'database_url': os.getenv('DATABASE_URL', 'Not set'),
                    'pin_count': pin_count,
                    'table_name': 'chocolate_pins',
                    'connection_status': 'Connected'
                }
                
        except Exception as e:
            return {
                'storage_type': 'PostgreSQL Database (Error)',
                'database_url': os.getenv('DATABASE_URL', 'Not set'),
                'error': str(e),
                'connection_status': 'Error',
                'pin_count': 0
            }
    
    def __del__(self):
        """Close database connection when object is destroyed"""
        if self.connection:
            try:
                self.connection.close()
            except:
                pass

# Create a global instance
database_manager = DatabaseManager()
