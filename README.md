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

The application now supports **PostgreSQL database storage** for production deployment on Render, with automatic fallback to JSON file storage for local development.

### Production (Render)
- Uses PostgreSQL database (`chocolate-app-db`)
- Automatic data persistence and backup
- Environment variable `DATABASE_URL` is automatically set by Render

### Local Development
- Falls back to JSON file storage if no database is available
- Pins stored in `data/map_pins.json`
- Data persists between application sessions


## Environment Setup

### For Render Deployment
1. The `render.yaml` file is already configured
2. Database URL is automatically provided by Render
3. No additional setup required

### For Local Development
Use JSON storage (default) - no setup required

## Dependencies

- **Streamlit**: Web application framework
- **Folium**: Interactive map visualization
- **streamlit-folium**: Streamlit-Folium integration
- **Pandas**: Data manipulation (optional)
- **psycopg2-binary**: PostgreSQL adapter for Python
- **python-dotenv**: Environment variable management

## License

This project is open source and available under the MIT License.
