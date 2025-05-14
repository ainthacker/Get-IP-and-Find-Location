# Note:
 Moved here from my old GitHub profile to keep everything in one place


# IP Geolocation Tool

A beautiful and feature-rich command-line tool to get detailed geographic information about IP addresses. This tool provides rich information about any IP address including location, network details, and country demographics in a visually appealing format.


![image](https://github.com/user-attachments/assets/9fe137f9-66d6-4bc6-a317-61acafa006e8)


## Features

- 🔍 Lookup any IP address or automatically detect your own public IP
- 🌍 Display detailed location information (country, city, region, coordinates)
- 🖧 Show network information (ISP, organization, AS number)
- 🔄 Detect proxy, hosting, and mobile network usage
- 🗺️ Provide links to view location on maps
- 🏳️ Display country flags, demographics, and additional information
- 💾 Export results in multiple formats (JSON, CSV, HTML with interactive map)
- 🖥️ Beautiful terminal UI with colored output
- 🔧 Simple mode for script integration

## Installation

### Prerequisites

- Python 3.6 or higher
- Internet connection for IP lookups

### Setup

1. Clone this repository or download the source code:
   ```
   git clone https://github.com/yourusername/ip-geolocation.git
   cd ip-geolocation
   ```

2. Make the script executable (Linux/Mac):
   ```
   chmod +x ip-geo-tool.py
   ```

## Usage

### Basic Usage

To lookup your own IP address:
```
python ip-geo-tool.py
```

To lookup a specific IP address:
```
python ip-geo-tool.py 8.8.8.8
```

### Output Options

Display results in simple mode (no colors or fancy formatting):
```
python ip-geo-tool.py --simple 8.8.8.8
```

Get more detailed information including demographics:
```
python ip-geo-tool.py --detailed 8.8.8.8
```

### Export Options

Export the results to a JSON file:
```
python ip-geo-tool.py 8.8.8.8 --format json --output results.json
```

Export the results to a CSV file:
```
python ip-geo-tool.py 8.8.8.8 --format csv --output results.csv
```

Generate an HTML report with an interactive map:
```
python ip-geo-tool.py 8.8.8.8 --format html --output report.html
```

## Command Line Options

| Option | Description |
|--------|-------------|
| `ip` | IP address to lookup (if not provided, your public IP will be used) |
| `-s, --simple` | Display output in simple mode (no colors or fancy formatting) |
| `-d, --detailed` | Get more detailed information about the IP |
| `-f, --format {json,csv,html,terminal}` | Output format (default: terminal) |
| `-o, --output FILENAME` | Output file name (required for JSON, CSV, HTML formats) |
| `-h, --help` | Show help message and exit |

## API Information

This tool uses the following free APIs:
- [IP-API.com](http://ip-api.com/) for IP geolocation
- [RESTCountries](https://restcountries.com/) for additional country information
- [ipify](https://api.ipify.org) for determining your public IP

Please respect API rate limits and usage policies when using this tool.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Thanks to all the API providers for their free services
- Inspired by various IP geolocation tools and services

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 
