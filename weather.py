import multiprocessing
import requests
import time
from datetime import datetime

def fetch_weather_data(queue, api_key, city, interval=300):
    """Fetch current weather data from WeatherAPI.com at regular intervals."""
    base_url = "http://api.weatherapi.com/v1/current.json"
   
    params = {
        "key": api_key,
        "q": city,
        "aqi": "yes"
    }
   
    while True:
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()  # Raise an exception for bad responses
            data = response.json()
            queue.put(data)
            time.sleep(interval)
        except Exception as e:
            print(f"Error fetching weather data: {e}")
            time.sleep(interval)

def log_weather_data(queue):
    """Receive weather data from the queue and log it to a file with timestamps."""
    with open("mumbai_weather_data_log.txt", "a") as log_file:
        while True:
            data = queue.get()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
           
            # Extract relevant information from the weather data
            if 'current' in data:
                current = data['current']
                temp_c = current.get('temp_c', 'N/A')
                humidity = current.get('humidity', 'N/A')
                condition = current.get('condition', {}).get('text', 'N/A')
                wind = current.get('wind_kph', 'N/A')
               
                # Air Quality Index (AQI)
                aqi = current.get('air_quality', {}).get('us-epa-index', 'N/A')
               
                log_entry = f"{timestamp} - Temperature: {temp_c}°C, Humidity: {humidity}%, Condition: {condition}, Wind: {wind} kph, AQI: {aqi}\n"
                log_file.write(log_entry)
                log_file.flush()
            else:
                log_file.write(f"{timestamp} - Error: No weather data available\n")
                log_file.flush()

if __name__ == "__main__":
    # API key from the provided URL
    api_key = "f4b13ecbe9fc4d188b860954240208"
   
    # City
    city = "Mumbai"
   
    # Create a multiprocessing Queue for inter-process communication
    data_queue = multiprocessing.Queue()

    # Create and start the fetcher process
    fetcher = multiprocessing.Process(target=fetch_weather_data, args=(data_queue, api_key, city))
    fetcher.start()

    # Create and start the logger process
    logger = multiprocessing.Process(target=log_weather_data, args=(data_queue,))
    logger.start()

    try:
        # Keep the main process running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping processes...")
        fetcher.terminate()
        logger.terminate()
        fetcher.join()
        logger.join()
        print("Processes stopped.")