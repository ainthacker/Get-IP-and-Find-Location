#!/usr/bin/env python3
"""
IP Geolocation CLI Tool
A beautiful command-line tool to get geographic information about IP addresses.
"""

import argparse
import csv
import json
import os
import sys
import urllib.request
from urllib.error import URLError
import socket
import textwrap
import webbrowser
from datetime import datetime

# Terminal colors and styles
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    BG_BLUE = '\033[44m'
    BG_BLACK = '\033[40m'

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    """Print a beautiful ASCII art banner."""
    banner = f"""
    {Colors.CYAN}{Colors.BOLD}╔═════════════════════════════════════════════════╗
    ║                                                 ║
    ║  {Colors.BLUE}██╗██████╗  ██████╗ ███████╗ ██████╗{Colors.CYAN}         ║
    ║  {Colors.BLUE}██║██╔══██╗██╔════╝ ██╔════╝██╔═══██╗{Colors.CYAN}        ║
    ║  {Colors.BLUE}██║██████╔╝██║  ███╗█████╗  ██║   ██║{Colors.CYAN}        ║
    ║  {Colors.BLUE}██║██╔═══╝ ██║   ██║██╔══╝  ██║   ██║{Colors.CYAN}        ║
    ║  {Colors.BLUE}██║██║     ╚██████╔╝███████╗╚██████╔╝{Colors.CYAN}        ║
    ║  {Colors.BLUE}╚═╝╚═╝      ╚═════╝ ╚══════╝ ╚═════╝{Colors.CYAN}         ║
    ║                                                 ║
    ║       {Colors.GREEN}IP Geolocation Tool v1.1{Colors.CYAN}                ║
    ║       {Colors.YELLOW}Find location details for any IP{Colors.CYAN}         ║
    ║                                                 ║
    ╚═════════════════════════════════════════════════╝{Colors.ENDC}
    """
    print(banner)

def validate_ip(ip):
    """Validate if the input is a valid IP address."""
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False

def get_public_ip():
    """Get the public IP address of the current machine."""
    try:
        with urllib.request.urlopen("https://api.ipify.org") as response:
            return response.read().decode('utf-8')
    except URLError:
        print(f"{Colors.RED}Unable to determine your public IP address. Check your internet connection.{Colors.ENDC}")
        sys.exit(1)

def get_ip_info(ip, detailed=False):
    """Get geolocation information for the given IP address."""
    try:
        # For basic information
        fields = "status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,query"
        
        # For more detailed information
        if detailed:
            fields += ",currency,proxy,hosting,mobile,continent,continentCode,district,asname,reverse,offset,languages"
        
        url = f"http://ip-api.com/json/{ip}?fields={fields}"
        with urllib.request.urlopen(url) as response:
            return json.loads(response.read().decode())
    except URLError:
        print(f"{Colors.RED}Error connecting to the geolocation API. Check your internet connection.{Colors.ENDC}")
        sys.exit(1)

def get_additional_info(ip_info):
    """Get additional demographic and regional information using external APIs."""
    additional_info = {}
    
    # If we have country code, we can get additional information
    if 'countryCode' in ip_info:
        try:
            # Get country information from restcountries.com
            country_code = ip_info['countryCode']
            url = f"https://restcountries.com/v3.1/alpha/{country_code}"
            with urllib.request.urlopen(url) as response:
                country_data = json.loads(response.read().decode())
                if country_data and len(country_data) > 0:
                    country = country_data[0]
                    additional_info['population'] = country.get('population')
                    additional_info['capital'] = country.get('capital', [''])[0]
                    additional_info['currencies'] = country.get('currencies', {})
                    additional_info['languages'] = country.get('languages', {})
                    additional_info['flag'] = country.get('flags', {}).get('png', '')
                    additional_info['region'] = country.get('region')
                    additional_info['subregion'] = country.get('subregion')
        except Exception as e:
            # Just continue if additional info fails
            pass
    
    return additional_info

def display_ip_info(ip_info, additional_info=None):
    """Display the IP information in a beautiful format."""
    if ip_info.get('status') != 'success':
        print(f"{Colors.RED}Error: {ip_info.get('message', 'Unknown error')}{Colors.ENDC}")
        return

    # Get local time in the IP's timezone
    time_info = ""
    if 'timezone' in ip_info:
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            time_info = f"{Colors.BLUE}Local Time:{Colors.ENDC} {current_time} (Approx. based on timezone)"
        except Exception:
            time_info = ""

    # Create a pretty border around the info
    terminal_width = os.get_terminal_size().columns
    width = min(80, terminal_width - 4)  # Leave some margin

    # Header with IP address
    print(f"\n{Colors.BG_BLUE}{Colors.BOLD}{' ' * width}{Colors.ENDC}")
    ip_header = f"  IP: {ip_info['query']}  "
    pad_length = width - len(ip_header) + len(Colors.BG_BLUE + Colors.BOLD + Colors.ENDC)
    print(f"{Colors.BG_BLUE}{Colors.BOLD}{ip_header}{' ' * pad_length}{Colors.ENDC}")
    print(f"{Colors.BG_BLUE}{Colors.BOLD}{' ' * width}{Colors.ENDC}\n")

    # Location information
    location_parts = []
    if ip_info.get('city'):
        location_parts.append(ip_info['city'])
    if ip_info.get('regionName'):
        location_parts.append(ip_info['regionName'])
    if ip_info.get('country'):
        if ip_info.get('countryCode'):
            location_parts.append(f"{ip_info['country']} ({ip_info['countryCode']})")
        else:
            location_parts.append(ip_info['country'])
    
    location = ", ".join(location_parts)
    
    # Display the information in a structured way
    print(f"{Colors.GREEN}┌{'─' * (width - 2)}┐{Colors.ENDC}")
    
    # Location
    print(f"{Colors.GREEN}│ {Colors.BOLD}Location:{Colors.ENDC} {location}{' ' * (width - 11 - len(location))} {Colors.GREEN}│{Colors.ENDC}")
    
    # Continent if available
    if ip_info.get('continent'):
        continent = f"{ip_info['continent']} ({ip_info.get('continentCode', '')})"
        print(f"{Colors.GREEN}│ {Colors.BOLD}Continent:{Colors.ENDC} {continent}{' ' * (width - 12 - len(continent))} {Colors.GREEN}│{Colors.ENDC}")
    
    # District if available
    if ip_info.get('district'):
        district = ip_info['district']
        print(f"{Colors.GREEN}│ {Colors.BOLD}District:{Colors.ENDC} {district}{' ' * (width - 11 - len(district))} {Colors.GREEN}│{Colors.ENDC}")
    
    # Coordinates
    if 'lat' in ip_info and 'lon' in ip_info:
        coords = f"{ip_info['lat']}, {ip_info['lon']}"
        print(f"{Colors.GREEN}│ {Colors.BOLD}Coordinates:{Colors.ENDC} {coords}{' ' * (width - 14 - len(coords))} {Colors.GREEN}│{Colors.ENDC}")
    
    # Zip/Postal Code
    if ip_info.get('zip'):
        zip_code = ip_info['zip']
        print(f"{Colors.GREEN}│ {Colors.BOLD}Postal Code:{Colors.ENDC} {zip_code}{' ' * (width - 14 - len(zip_code))} {Colors.GREEN}│{Colors.ENDC}")
    
    # Timezone
    if ip_info.get('timezone'):
        timezone = ip_info['timezone']
        print(f"{Colors.GREEN}│ {Colors.BOLD}Timezone:{Colors.ENDC} {timezone}{' ' * (width - 11 - len(timezone))} {Colors.GREEN}│{Colors.ENDC}")
    
    # Time offset if available
    if ip_info.get('offset') is not None:
        offset = f"UTC {'+' if ip_info['offset'] >= 0 else ''}{ip_info['offset']}"
        print(f"{Colors.GREEN}│ {Colors.BOLD}Time Offset:{Colors.ENDC} {offset}{' ' * (width - 14 - len(offset))} {Colors.GREEN}│{Colors.ENDC}")
    
    # Time info if available
    if time_info:
        # Format the time info to fit within the width
        time_display = time_info.replace(Colors.BLUE, '').replace(Colors.ENDC, '')
        time_length = len(time_display)
        formatted_time = textwrap.fill(time_display, width - 4)
        formatted_lines = formatted_time.split('\n')
        
        for i, line in enumerate(formatted_lines):
            prefix = f"{Colors.GREEN}│ " if i == 0 else f"{Colors.GREEN}│  "
            suffix = f"{' ' * (width - 2 - len(line))} {Colors.GREEN}│{Colors.ENDC}"
            if i == 0:
                print(f"{Colors.GREEN}│ {Colors.BLUE}Local Time:{Colors.ENDC} {line.replace('Local Time: ', '')}{' ' * (width - 12 - len(line) + len('Local Time: '))} {Colors.GREEN}│{Colors.ENDC}")
            else:
                print(f"{Colors.GREEN}│  {line}{' ' * (width - 4 - len(line))} {Colors.GREEN}│{Colors.ENDC}")
    
    # Additional information section if we have more data
    if (ip_info.get('proxy') is not None or ip_info.get('hosting') is not None or 
        ip_info.get('mobile') is not None or additional_info):
        print(f"{Colors.GREEN}├{'─' * (width - 2)}┤{Colors.ENDC}")
        print(f"{Colors.GREEN}│ {Colors.BOLD}{Colors.YELLOW}Additional Information{' ' * (width - 23)}{Colors.ENDC} {Colors.GREEN}│{Colors.ENDC}")
        print(f"{Colors.GREEN}├{'─' * (width - 2)}┤{Colors.ENDC}")
        
        # Connection type
        if ip_info.get('proxy') is not None:
            proxy = "Yes" if ip_info['proxy'] else "No"
            print(f"{Colors.GREEN}│ {Colors.BOLD}Using Proxy:{Colors.ENDC} {proxy}{' ' * (width - 15 - len(proxy))} {Colors.GREEN}│{Colors.ENDC}")
        
        if ip_info.get('hosting') is not None:
            hosting = "Yes" if ip_info['hosting'] else "No"
            print(f"{Colors.GREEN}│ {Colors.BOLD}Hosting/DC:{Colors.ENDC} {hosting}{' ' * (width - 13 - len(hosting))} {Colors.GREEN}│{Colors.ENDC}")
        
        if ip_info.get('mobile') is not None:
            mobile = "Yes" if ip_info['mobile'] else "No"
            print(f"{Colors.GREEN}│ {Colors.BOLD}Mobile Network:{Colors.ENDC} {mobile}{' ' * (width - 17 - len(mobile))} {Colors.GREEN}│{Colors.ENDC}")
        
        # Country demographic info if available
        if additional_info and additional_info.get('population'):
            population = f"{additional_info['population']:,}"
            print(f"{Colors.GREEN}│ {Colors.BOLD}Country Population:{Colors.ENDC} {population}{' ' * (width - 21 - len(population))} {Colors.GREEN}│{Colors.ENDC}")
        
        if additional_info and additional_info.get('capital'):
            capital = additional_info['capital']
            print(f"{Colors.GREEN}│ {Colors.BOLD}Capital:{Colors.ENDC} {capital}{' ' * (width - 10 - len(capital))} {Colors.GREEN}│{Colors.ENDC}")
        
        if additional_info and additional_info.get('currencies'):
            currency_list = []
            for code, info in additional_info['currencies'].items():
                if isinstance(info, dict) and 'name' in info:
                    currency_list.append(f"{code} ({info['name']})")
                else:
                    currency_list.append(code)
            
            currencies = ", ".join(currency_list)
            curr_wrapped = textwrap.fill(currencies, width - 13)
            curr_lines = curr_wrapped.split('\n')
            
            print(f"{Colors.GREEN}│ {Colors.BOLD}Currencies:{Colors.ENDC} {curr_lines[0]}{' ' * (width - 13 - len(curr_lines[0]))} {Colors.GREEN}│{Colors.ENDC}")
            for line in curr_lines[1:]:
                print(f"{Colors.GREEN}│            {line}{' ' * (width - 12 - len(line))} {Colors.GREEN}│{Colors.ENDC}")
        
        if additional_info and additional_info.get('languages'):
            lang_list = []
            for code, name in additional_info['languages'].items():
                lang_list.append(f"{name} ({code})")
            
            languages = ", ".join(lang_list)
            lang_wrapped = textwrap.fill(languages, width - 13)
            lang_lines = lang_wrapped.split('\n')
            
            print(f"{Colors.GREEN}│ {Colors.BOLD}Languages:{Colors.ENDC} {lang_lines[0]}{' ' * (width - 12 - len(lang_lines[0]))} {Colors.GREEN}│{Colors.ENDC}")
            for line in lang_lines[1:]:
                print(f"{Colors.GREEN}│            {line}{' ' * (width - 12 - len(line))} {Colors.GREEN}│{Colors.ENDC}")
    
    # Network Information
    print(f"{Colors.GREEN}├{'─' * (width - 2)}┤{Colors.ENDC}")
    print(f"{Colors.GREEN}│ {Colors.BOLD}{Colors.YELLOW}Network Information{' ' * (width - 21)}{Colors.ENDC} {Colors.GREEN}│{Colors.ENDC}")
    print(f"{Colors.GREEN}├{'─' * (width - 2)}┤{Colors.ENDC}")
    
    # Reverse DNS if available
    if ip_info.get('reverse'):
        reverse = ip_info['reverse']
        rev_wrapped = textwrap.fill(reverse, width - 15)
        rev_lines = rev_wrapped.split('\n')
        
        print(f"{Colors.GREEN}│ {Colors.BOLD}Reverse DNS:{Colors.ENDC} {rev_lines[0]}{' ' * (width - 14 - len(rev_lines[0]))} {Colors.GREEN}│{Colors.ENDC}")
        for line in rev_lines[1:]:
            print(f"{Colors.GREEN}│              {line}{' ' * (width - 14 - len(line))} {Colors.GREEN}│{Colors.ENDC}")
    
    # ISP
    if ip_info.get('isp'):
        isp = ip_info['isp']
        isp_wrapped = textwrap.fill(isp, width - 8)
        isp_lines = isp_wrapped.split('\n')
        print(f"{Colors.GREEN}│ {Colors.BOLD}ISP:{Colors.ENDC} {isp_lines[0]}{' ' * (width - 6 - len(isp_lines[0]))} {Colors.GREEN}│{Colors.ENDC}")
        for line in isp_lines[1:]:
            print(f"{Colors.GREEN}│      {line}{' ' * (width - 6 - len(line))} {Colors.GREEN}│{Colors.ENDC}")
    
    # Organization
    if ip_info.get('org'):
        org = ip_info['org']
        org_wrapped = textwrap.fill(org, width - 8)
        org_lines = org_wrapped.split('\n')
        print(f"{Colors.GREEN}│ {Colors.BOLD}ORG:{Colors.ENDC} {org_lines[0]}{' ' * (width - 6 - len(org_lines[0]))} {Colors.GREEN}│{Colors.ENDC}")
        for line in org_lines[1:]:
            print(f"{Colors.GREEN}│      {line}{' ' * (width - 6 - len(line))} {Colors.GREEN}│{Colors.ENDC}")
    
    # AS Number/Name
    if ip_info.get('as'):
        as_info = ip_info['as']
        as_wrapped = textwrap.fill(as_info, width - 8)
        as_lines = as_wrapped.split('\n')
        print(f"{Colors.GREEN}│ {Colors.BOLD}AS:{Colors.ENDC}  {as_lines[0]}{' ' * (width - 6 - len(as_lines[0]))} {Colors.GREEN}│{Colors.ENDC}")
        for line in as_lines[1:]:
            print(f"{Colors.GREEN}│      {line}{' ' * (width - 6 - len(line))} {Colors.GREEN}│{Colors.ENDC}")
    
    # AS Name if available
    if ip_info.get('asname'):
        asname = ip_info['asname']
        asname_wrapped = textwrap.fill(asname, width - 14)
        asname_lines = asname_wrapped.split('\n')
        print(f"{Colors.GREEN}│ {Colors.BOLD}AS Name:{Colors.ENDC} {asname_lines[0]}{' ' * (width - 10 - len(asname_lines[0]))} {Colors.GREEN}│{Colors.ENDC}")
        for line in asname_lines[1:]:
            print(f"{Colors.GREEN}│          {line}{' ' * (width - 10 - len(line))} {Colors.GREEN}│{Colors.ENDC}")
    
    # Bottom border
    print(f"{Colors.GREEN}└{'─' * (width - 2)}┘{Colors.ENDC}")
    
    # Add map URL
    if 'lat' in ip_info and 'lon' in ip_info:
        map_url = f"https://www.openstreetmap.org/?mlat={ip_info['lat']}&mlon={ip_info['lon']}#map=12/{ip_info['lat']}/{ip_info['lon']}"
        print(f"\n{Colors.BLUE}View on map:{Colors.ENDC} {map_url}")
    
    # Add flag URL if available from additional info
    if additional_info and additional_info.get('flag'):
        print(f"{Colors.BLUE}Country flag:{Colors.ENDC} {additional_info['flag']}")

def export_to_json(ip_info, additional_info, filename):
    """Export IP information to a JSON file."""
    data = ip_info.copy()
    
    # Add additional info if available
    if additional_info:
        data['additional_info'] = additional_info
    
    # Add timestamp
    data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"{Colors.GREEN}Data exported to {filename}{Colors.ENDC}")

def export_to_csv(ip_info, additional_info, filename):
    """Export IP information to a CSV file."""
    # Flatten the additional info to make it CSV-friendly
    flat_data = ip_info.copy()
    
    if additional_info:
        for key, value in additional_info.items():
            if isinstance(value, dict):
                # For dictionaries like currencies, languages
                flat_value = ', '.join([f"{k}: {v}" if isinstance(v, str) else f"{k}" for k, v in value.items()])
                flat_data[f"additional_{key}"] = flat_value
            else:
                flat_data[f"additional_{key}"] = value
    
    # Add timestamp
    flat_data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=flat_data.keys())
        writer.writeheader()
        writer.writerow(flat_data)
    
    print(f"{Colors.GREEN}Data exported to {filename}{Colors.ENDC}")

def export_to_html(ip_info, additional_info, filename):
    """Export IP information to an HTML file with a map."""
    map_html = ""
    flag_html = ""
    additional_html = ""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Create map if coordinates are available
    if 'lat' in ip_info and 'lon' in ip_info:
        map_html = f"""
        <div class="map-container">
            <h2>Location Map</h2>
            <div id="map"></div>
            <script>
                var map = L.map('map').setView([{ip_info['lat']}, {ip_info['lon']}], 10);
                L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                }}).addTo(map);
                L.marker([{ip_info['lat']}, {ip_info['lon']}]).addTo(map)
                    .bindPopup("{ip_info.get('city', '')}, {ip_info.get('regionName', '')}, {ip_info.get('country', '')}")
                    .openPopup();
            </script>
        </div>
        """
    
    # Add flag if available
    if additional_info and additional_info.get('flag'):
        flag_html = f"""
        <div class="flag-container">
            <h2>Country Flag</h2>
            <img src="{additional_info['flag']}" alt="Country flag" class="flag">
        </div>
        """
    
    # Additional info section
    if additional_info:
        additional_rows = ""
        
        if additional_info.get('population'):
            additional_rows += f"""
            <tr>
                <td>Population</td>
                <td>{additional_info['population']:,}</td>
            </tr>
            """
        
        if additional_info.get('capital'):
            additional_rows += f"""
            <tr>
                <td>Capital</td>
                <td>{additional_info['capital']}</td>
            </tr>
            """
        
        if additional_info.get('currencies'):
            currencies = []
            for code, info in additional_info['currencies'].items():
                if isinstance(info, dict) and 'name' in info:
                    currencies.append(f"{code} ({info['name']})")
                else:
                    currencies.append(code)
            
            additional_rows += f"""
            <tr>
                <td>Currencies</td>
                <td>{', '.join(currencies)}</td>
            </tr>
            """
        
        if additional_info.get('languages'):
            languages = []
            for code, name in additional_info['languages'].items():
                languages.append(f"{name} ({code})")
            
            additional_rows += f"""
            <tr>
                <td>Languages</td>
                <td>{', '.join(languages)}</td>
            </tr>
            """
        
        if additional_rows:
            additional_html = f"""
            <div class="info-container">
                <h2>Additional Country Information</h2>
                <table class="info-table">
                    {additional_rows}
                </table>
            </div>
            """
    
    # Build the main info table
    info_rows = ""
    
    # Basic Location Info
    location_parts = []
    if ip_info.get('city'):
        location_parts.append(ip_info['city'])
    if ip_info.get('regionName'):
        location_parts.append(ip_info['regionName'])
    if ip_info.get('country'):
        if ip_info.get('countryCode'):
            location_parts.append(f"{ip_info['country']} ({ip_info['countryCode']})")
        else:
            location_parts.append(ip_info['country'])
    
    location = ", ".join(location_parts)
    
    info_rows += f"""
    <tr>
        <td>IP Address</td>
        <td>{ip_info.get('query', 'N/A')}</td>
    </tr>
    <tr>
        <td>Location</td>
        <td>{location}</td>
    </tr>
    """
    
    if ip_info.get('continent'):
        info_rows += f"""
        <tr>
            <td>Continent</td>
            <td>{ip_info['continent']} ({ip_info.get('continentCode', '')})</td>
        </tr>
        """
    
    if 'lat' in ip_info and 'lon' in ip_info:
        info_rows += f"""
        <tr>
            <td>Coordinates</td>
            <td>{ip_info['lat']}, {ip_info['lon']}</td>
        </tr>
        """
    
    if ip_info.get('timezone'):
        info_rows += f"""
        <tr>
            <td>Timezone</td>
            <td>{ip_info['timezone']}</td>
        </tr>
        """
    
    # Connection info
    if ip_info.get('proxy') is not None:
        info_rows += f"""
        <tr>
            <td>Using Proxy</td>
            <td>{"Yes" if ip_info['proxy'] else "No"}</td>
        </tr>
        """
    
    if ip_info.get('hosting') is not None:
        info_rows += f"""
        <tr>
            <td>Hosting/DC</td>
            <td>{"Yes" if ip_info['hosting'] else "No"}</td>
        </tr>
        """
    
    if ip_info.get('mobile') is not None:
        info_rows += f"""
        <tr>
            <td>Mobile Network</td>
            <td>{"Yes" if ip_info['mobile'] else "No"}</td>
        </tr>
        """
    
    # Network info
    if ip_info.get('isp'):
        info_rows += f"""
        <tr>
            <td>ISP</td>
            <td>{ip_info['isp']}</td>
        </tr>
        """
    
    if ip_info.get('org'):
        info_rows += f"""
        <tr>
            <td>Organization</td>
            <td>{ip_info['org']}</td>
        </tr>
        """
    
    if ip_info.get('as'):
        info_rows += f"""
        <tr>
            <td>AS</td>
            <td>{ip_info['as']}</td>
        </tr>
        """
    
    # Create the full HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IP Geolocation: {ip_info.get('query', 'Unknown IP')}</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css"
          integrity="sha512-xodZBNTC5n17Xt2atTPuE1HxjVMSvLVW9ocqUKLsCC5CXdbqCmblAshOMAS6/keqq/sMZMZ19scR4PsZChSR7A=="
          crossorigin=""/>
    <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"
            integrity="sha512-XQoYMqMTK8LvdxXYG3nZ448hOEQiglfqkJs1NOQV44cWnUrBc8PkAOcXy20w0vlaXaVUearIOBhiXZ5V3ynxwA=="
            crossorigin=""></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            color: #333;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }}
        header {{
            background-color: #3498db;
            color: white;
            padding: 20px;
            text-align: center;
            border-radius: 5px 5px 0 0;
            margin-bottom: 20px;
        }}
        h1, h2 {{
            margin-top: 0;
        }}
        .info-container {{
            margin-bottom: 20px;
        }}
        .info-table {{
            width: 100%;
            border-collapse: collapse;
        }}
        .info-table td, .info-table th {{
            padding: 12px 15px;
            border: 1px solid #ddd;
        }}
        .info-table tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
        .info-table tr:hover {{
            background-color: #ddd;
        }}
        .map-container {{
            margin-top: 20px;
        }}
        #map {{
            height: 400px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .flag {{
            max-width: 200px;
            border: 1px solid #ddd;
        }}
        footer {{
            text-align: center;
            margin-top: 20px;
            padding: 10px;
            background-color: #f2f2f2;
            border-radius: 0 0 5px 5px;
        }}
        .two-column {{
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
        }}
        .column {{
            flex: 1;
            min-width: 300px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>IP Geolocation Report</h1>
            <p>Generated on {timestamp}</p>
        </header>
        
        <div class="info-container">
            <h2>IP Information: {ip_info.get('query', 'Unknown IP')}</h2>
            <table class="info-table">
                {info_rows}
            </table>
        </div>
        
        <div class="two-column">
            <div class="column">
                {additional_html}
                {flag_html}
            </div>
            <div class="column">
                {map_html}
            </div>
        </div>
        
        <footer>
            <p>Generated by IP Geolocation Tool v1.1</p>
        </footer>
    </div>
</body>
</html>
"""
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"{Colors.GREEN}Data exported to {filename}{Colors.ENDC}")
    
    # Ask if user wants to open the HTML file in a browser
    open_browser = input(f"{Colors.YELLOW}Do you want to open the HTML report in your browser? (y/n): {Colors.ENDC}")
    if open_browser.lower() == 'y':
        try:
            webbrowser.open('file://' + os.path.abspath(filename))
        except Exception:
            print(f"{Colors.RED}Could not open browser automatically. Please open {filename} manually.{Colors.ENDC}")

def main():
    parser = argparse.ArgumentParser(description='IP Geolocation Tool - Find location details for any IP address')
    parser.add_argument('ip', nargs='?', help='IP address to lookup (if not provided, your public IP will be used)')
    parser.add_argument('-s', '--simple', action='store_true', help='Display output in simple mode (no colors or fancy formatting)')
    parser.add_argument('-d', '--detailed', action='store_true', help='Get more detailed information about the IP')
    parser.add_argument('-f', '--format', choices=['json', 'csv', 'html', 'terminal'], default='terminal', 
                        help='Output format (default: terminal)')
    parser.add_argument('-o', '--output', help='Output file name (for JSON, CSV, HTML formats)')
    args = parser.parse_args()

    # If simple mode is requested, disable colors
    if args.simple:
        for attr in dir(Colors):
            if not attr.startswith('__'):
                setattr(Colors, attr, '')
    
    # Check if output file is specified for non-terminal formats
    if args.format != 'terminal' and not args.output:
        print(f"{Colors.RED}Error: Output file must be specified with --output when using --format={args.format}{Colors.ENDC}")
        sys.exit(1)
    
    clear_screen()
    print_banner()
    
    ip = args.ip
    
    # If IP is not provided, get the user's public IP
    if not ip:
        print(f"{Colors.YELLOW}No IP provided. Looking up your public IP...{Colors.ENDC}")
        ip = get_public_ip()
        print(f"{Colors.GREEN}Your public IP: {ip}{Colors.ENDC}")
    elif not validate_ip(ip):
        print(f"{Colors.RED}Error: '{ip}' is not a valid IP address.{Colors.ENDC}")
        sys.exit(1)

    print(f"{Colors.YELLOW}Fetching geolocation data...{Colors.ENDC}")
    ip_info = get_ip_info(ip, detailed=args.detailed)
    
    additional_info = None
    if args.detailed:
        print(f"{Colors.YELLOW}Fetching additional demographic information...{Colors.ENDC}")
        additional_info = get_additional_info(ip_info)
    
    # Handle different output formats
    if args.format == 'terminal':
        display_ip_info(ip_info, additional_info)
    elif args.format == 'json':
        export_to_json(ip_info, additional_info, args.output)
    elif args.format == 'csv':
        export_to_csv(ip_info, additional_info, args.output)
    elif args.format == 'html':
        export_to_html(ip_info, additional_info, args.output)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Operation cancelled by user.{Colors.ENDC}")
        sys.exit(0)
