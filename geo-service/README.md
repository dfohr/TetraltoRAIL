# TetraltoRail Geolocation Service

A FastAPI-based microservice for IP geolocation using MaxMind's web service.

## Environment Variables

The following environment variables are required:

- `MAXMIND_ACCOUNT_ID`: Your MaxMind account ID
- `MAXMIND_LICENSE_KEY`: Your MaxMind license key
- `PORT`: Port number for the service (defaults to 8080)

## API Endpoints

- `GET /`: Basic health check
- `GET /health`: Comprehensive health check including MaxMind API status
- `GET /geolocate?ip=<ip_address>`: Get geolocation data for an IP address

## Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set environment variables:
   ```bash
   export MAXMIND_ACCOUNT_ID=your_account_id
   export MAXMIND_LICENSE_KEY=your_license_key
   ```

3. Run the service:
   ```bash
   python app.py
   ```

## Deployment

The service is deployed on Railway. The start command is configured in the Railway dashboard. 