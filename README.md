# Orange Twirl Map 📍

An interactive web application that allows users to add pins with prices of orange twirl. Built with Python, Streamlit, and Folium.

## Features

- 🗺️ **Interactive Map**: Click anywhere on the map to add new pins
- 📝 **Add Facts**: Add required information to your pins
- 💾 **Persistent Storage**: Your pins are saved automatically and persist between sessions
- 📋 **Pin Management**: View, manage, and delete existing pins from the sidebar
- 📍 **Rich Popups**: Click on pins to see detailed information

## Installation

1. Make sure you have Python 3.7+ installed
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

Run the Streamlit app:
```bash
streamlit run main.py
```

The application will open in your default web browser at `http://localhost:8501`

## How to Use

1. **Adding Pins**: Click anywhere on the map to select a location
2. **Fill the Form**: Enter a title and interesting fact in the form that appears
3. **Save**: Click "Add Pin" to save your fact to the map
4. **View Pins**: Click on red markers to see pin details, or view all pins in the sidebar
5. **Navigate**: Use the quick location presets or enter custom coordinates
6. **Manage**: Delete individual pins or clear all pins using the sidebar controls

## Data Storage

- Pins are stored in `map_pins.json` in the same directory as the application
- Data includes title, fact, coordinates, and timestamp for each pin
- Data persists between application sessions

## Customization

You can easily customize:
- Default map center location
- Map tiles and styling
- Pin icons and colors
- Quick location presets
- UI layout and styling

## Dependencies

- **Streamlit**: Web application framework
- **Folium**: Interactive map visualization
- **streamlit-folium**: Streamlit-Folium integration
- **Pandas**: Data manipulation (optional)

## License

This project is open source and available under the MIT License.
