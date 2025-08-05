import streamlit as st
import folium
from streamlit_folium import st_folium
import os
from datetime import datetime
from database_manager import database_manager

# Set page config
st.set_page_config(
    page_title="Orange Twirl Map",
    page_icon="📍",
    layout="wide"
)

# Data management functions using the persistent database manager
def load_pins():
    """Load pins using the database manager"""
    return database_manager.load_pins()

def save_pin(price, location, brand, fact, lat, lon):
    """Save a new pin using the database manager"""
    return database_manager.add_pin(price, location, brand, fact, lat, lon)

def create_map(pins, center_lat, center_lon):
    """Create a folium map with existing pins"""

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=10,
        tiles="OpenStreetMap"
    )
    
    # Add existing pins to the map
    for pin in pins:
        popup_html = f"""
        <div style="width: 250px;">
            <h4 style="color: #2E86AB; margin-bottom: 10px;">{pin['location']}</h4>
            <p style="margin-bottom: 8px; font-size: 18px; font-weight: bold; color: #D2691E;">
                💰 ${pin.get('price', 'N/A'):.2f}
            </p>
            {f'<p style="margin-bottom: 8px;"><strong>Notes:</strong></p><p style="margin-bottom: 8px;">{pin["fact"]}</p>' if pin.get('fact') else ''}
            <p style="margin-bottom: 8px;"><strong>Added:</strong> {pin['timestamp']}</p>
            <p style="margin: 0;"><strong>Location:</strong> {pin['lat']:.4f}, {pin['lon']:.4f}</p>
        </div>
        """
        
        folium.Marker(
            location=[pin['lat'], pin['lon']],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=pin['price'],
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m)
    
    return m

def main():
    st.title("🍫 Orange Twirl Price Map")
    st.markdown("Click on the map to add pins for chocolate prices!")
    
    # Initialize session state
    if 'pins' not in st.session_state:
        st.session_state.pins = load_pins()
    
    if 'show_form' not in st.session_state:
        st.session_state.show_form = False
    
    if 'selected_location' not in st.session_state:
        st.session_state.selected_location = None

    # Price statistics
    if st.session_state.pins:
        prices = [pin.get('price', 0) for pin in st.session_state.pins if pin.get('price', 0) > 0]
        if prices:
            st.markdown("### 📊 Price Statistics")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Lowest Price", f"£{min(prices):.2f}")
            with col2:
                st.metric("Highest Price", f"£{max(prices):.2f}")
            with col3:
                st.metric("Average Price", f"£{sum(prices)/len(prices):.2f}")
            with col4:
                st.metric("Total Locations", len(prices))
    
    # Sidebar for controls and pin list
    with st.sidebar:
        
        # Map center controls
        col1, col2 = st.columns(2)
        center_lat = 51.5907
        center_lon = -0.0208
        
        # Display existing pins
        st.subheader(f"📌 Saved Pins ({len(st.session_state.pins)})")
        
        if st.session_state.pins:
            order = st.radio(
                    "Order by:",
                    ["price", "timestamp"],
                )
            reverse_dict = {"price": False, "timestamp": True}
            for i, pin in enumerate(sorted(st.session_state.pins, key=lambda x: x[order], reverse=reverse_dict[order])):
                price_display = f"£{pin.get('price', 0):.2f}" if 'price' in pin else "No price"
                with st.expander(f"{pin['location']} - {price_display}", expanded=False):
                    if 'price' in pin:
                        st.write(f"**Price:** £{pin['price']:.2f}")
                    if pin.get('fact'):
                        st.write(f"**Notes:** {pin['fact']}")
                    st.write(f"**Location:** {pin['lat']:.4f}, {pin['lon']:.4f}")
                    st.write(f"**Added:** {pin['timestamp']}")
                    
                    if st.button(f"Delete Pin {i+1}", key=f"delete_{i}"):
                        # Use the pin's ID for database, or index for JSON
                        pin_id = pin.get('id', i)
                        if database_manager.delete_pin(pin_id):
                            st.session_state.pins = load_pins()  # Refresh from storage
                            st.rerun()
                        else:
                            st.error("Failed to delete pin")
        else:
            st.info("No chocolate prices added yet. Click on the map to add your first price entry!")
        
        # Data storage info (for debugging/transparency)
        with st.expander("📁 Storage Info", expanded=False):
            info = database_manager.get_data_info()
            st.write(f"**Storage Type:** {info['storage_type']}")
            if 'database_url' in info:
                st.write(f"**Database:** Connected" if info['connection_status'] == 'Connected' else f"**Database:** {info['connection_status']}")
            elif 'data_directory' in info:
                st.write(f"**Environment:** {'Render Cloud' if info.get('is_render_environment') else 'Local Development'}")
                st.write(f"**Data Directory:** {info['data_directory']}")
                st.write(f"**File Size:** {info.get('file_size_bytes', 0)} bytes")
            st.write(f"**Total Pins:** {info['pin_count']}")
            
            # Only show backup for JSON storage
            if 'data_directory' in info and st.button("📋 Create Backup"):
                backup_path = database_manager.json_manager.backup_data() if hasattr(database_manager, 'json_manager') else None
                if backup_path:
                    st.success(f"Backup created: {os.path.basename(backup_path)}")
                else:
                    st.error("Failed to create backup")
        
        if st.button("🗑️ Clear All Pins"):
            if database_manager.clear_all_pins():
                st.session_state.pins = []
                st.rerun()
            else:
                st.error("Failed to clear pins")
    
    # Main map area
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Create and display the map
        m = create_map(st.session_state.pins, center_lat, center_lon)
        
        # Display the map and capture click events
        map_data = st_folium(
            m,
            width=800,
            height=600,
            returned_objects=["last_object_clicked", "last_clicked"],
            key="map"
        )
        
        # Handle map clicks
        if map_data['last_object_clicked'] is None and map_data['last_clicked'] is not None:
            clicked_lat = map_data['last_clicked']['lat']
            clicked_lon = map_data['last_clicked']['lng']
            st.session_state.selected_location = (clicked_lat, clicked_lon)
            st.session_state.show_form = True
    
    with col2:
        # Form for adding new pins
        if st.session_state.show_form and st.session_state.selected_location:
            st.subheader("🍫 Add Price Entry")
            
            lat, lon = st.session_state.selected_location
            st.write(f"**Selected Location:**")
            st.write(f"Latitude: {lat:.4f}")
            st.write(f"Longitude: {lon:.4f}")
            
            with st.form("pin_form"):
                price = st.number_input(
                    "Price per chocolate bar (£)",
                    min_value=0.0,
                    max_value=10.0,
                    value=0.0,
                    step=0.01,
                    format="%.2f"
                )

                location = st.text_input(
                    "Location/Store Name",
                    placeholder="e.g., Local Chocolate Shop, Supermarket Name..."
                )

                brand = st.radio(
                    "The type of chocolate",
                    ["Cadbury Orange Twirl", "Off-brand orange twirl"]
                )
                
                fact = ""
                if brand == "Off-brand orange twirl":
                    fact = st.text_area(
                        "Name of alternative brand",
                        placeholder="e.g., Brand ...",
                        height=100
                    )
                
                submit_col1, submit_col2 = st.columns(2)
                
                with submit_col1:
                    submitted = st.form_submit_button("📍 Add Pin", use_container_width=True)
                
                with submit_col2:
                    cancelled = st.form_submit_button("❌ Cancel", use_container_width=True)
                
                if submitted and location and price > 0:
                    if save_pin(price, location, brand, fact, lat, lon):
                        st.success("Pin added successfully!")
                        st.session_state.pins = load_pins()  # Refresh from storage
                        st.session_state.show_form = False
                        st.session_state.selected_location = None
                        st.rerun()
                    else:
                        st.error("Failed to save pin. Please try again.")

                elif submitted and (not location or price <= 0):
                    if not location:
                        st.error("Please enter a location/store name.")
                    if price <= 0:
                        st.error("Please enter a valid price greater than £0.")
                
                if cancelled:
                    st.session_state.show_form = False
                    st.session_state.selected_location = None
                    st.rerun()
        
        elif not st.session_state.show_form:
            st.info("👆 Click anywhere on the map to add a chocolate price entry!")
    
    # Instructions
    st.markdown("---")
    st.markdown("""
    ### 🍫 How to use this chocolate price tracker:
    1. **Click anywhere on the map** to select a location for your price entry
    2. **Fill in the form** with store/location name and chocolate price
    3. **Add notes** (optional) about the chocolate brand, type, size, etc.
    4. **Click "Add Pin"** to save your price to the map
    5. **View saved prices** in the sidebar or click on map markers to see details
    6. **Compare prices** across different locations to find the best deals!
    
    Your price data is automatically saved and will persist between sessions!
    """)

if __name__ == "__main__":
    main()