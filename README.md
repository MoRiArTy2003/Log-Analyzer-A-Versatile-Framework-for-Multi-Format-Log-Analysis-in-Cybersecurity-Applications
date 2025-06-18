# Log Analyzer

A comprehensive log analysis tool for cybersecurity professionals, built with Streamlit.

## Features

### Core Features
- **Multi-format Log Analysis**: Support for browsing logs, virus logs, mail logs, and more
- **Interactive Visualizations**: Dynamic charts and graphs for data analysis
- **Advanced Charts**: Enhanced visualizations using Plotly for deeper insights
- **Historical Dashboard**: Comprehensive historical analysis with time-based filtering
- **Real-time Monitoring**: Live log monitoring with syslog integration

### Advanced Analytics
- **Anomaly Detection**: Machine learning-based detection of unusual patterns in logs
- **Time Series Forecasting**: Predictive analytics for future log volumes and trends
- **Geospatial Analysis**: IP geolocation and map-based visualizations
- **Log Correlation**: Cross-log correlation to identify related events
- **Event Sequence Detection**: Identify sequences of related events

### Performance & Security
- **Performance Optimization**: Caching and memory optimization for large log files
- **User Authentication**: Secure login and role-based access control
- **Role-based Access**: Different capabilities for analysts and administrators

### User Experience
- **Custom Report Generation**: Create and export customized reports
- **Responsive Design**: Works on desktop and mobile devices
- **Theme Switching**: Light and dark mode support

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/log-analyzer.git
cd log-analyzer
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

3. Set up Firebase Authentication:
   - Create a Firebase project at [Firebase Console](https://console.firebase.google.com/)
   - Generate a service account key and save it as `log-analyser-960ca-efb8cc98a12b.json` in the project root directory

## Usage

1. Run the Streamlit app:
```bash
streamlit run log_analyser/app.py
```

2. Open your browser and navigate to `http://localhost:8501`

3. Log in or create a new account

4. Upload log files or use the example log file for analysis

## Log Formats

The application supports the following log formats:

### Browsing Logs
```
timestamp ip_address username url bandwidth status_code content_type category device_info
```

### Virus Logs
```
timestamp ip_address username virus_name file_path action_taken scan_engine severity
```

### Mail Logs
```
timestamp sender recipient subject size status attachment_count spam_score
```

## Project Structure

### Core Components
- `app.py`: Main application entry point
- `auth.py`: Authentication and user management
- `config.py`: Application configuration settings
- `models.py`: Data models and structures
- `pages.py`: Application pages and views
- `sidebar.py`: Sidebar navigation configuration
- `utils.py`: Utility functions for data processing and formatting

### Data Processing
- `log_parser.py`: Log parsing and processing for different formats
- `performance.py`: Performance optimization with caching and parallel processing

### Visualization
- `charts.py`: Basic data visualization and chart generation
- `advanced_charts.py`: Enhanced visualizations using Plotly
- `historical_dashboard.py`: Historical data analysis dashboard
- `geo_visualization.py`: Geospatial visualization and IP geolocation

### Advanced Analytics
- `ml_engine.py`: Machine learning for anomaly detection and forecasting
- `correlation_engine.py`: Log correlation and event sequence detection
- `real_time_monitor.py`: Real-time log monitoring functionality

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
