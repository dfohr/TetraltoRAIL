from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import time
import os
from typing import Dict, Any
import geoip2.webservice
import geoip2.errors

app = FastAPI(
    title="TetraltoRail Geolocation Service",
    description="Microservice for IP geolocation using MaxMind",
    version="1.0.0"
)

# MaxMind client configuration
MAXMIND_ACCOUNT_ID = int(os.getenv("MAXMIND_ACCOUNT_ID"))
MAXMIND_LICENSE_KEY = os.getenv("MAXMIND_LICENSE_KEY")
client = geoip2.webservice.Client(MAXMIND_ACCOUNT_ID, MAXMIND_LICENSE_KEY)

@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint for Railway health checks."""
    return {"status": "ok"}

@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Comprehensive health check endpoint."""
    start_time = time.time()
    
    # Check MaxMind API connection
    maxmind_status = "healthy"
    try:
        # Test MaxMind API with a known IP (Google's DNS)
        client.city("8.8.8.8")
    except Exception as e:
        maxmind_status = f"error: {str(e)}"
    
    response_time = time.time() - start_time
    
    return {
        "status": "up",
        "version": "1.0.0",
        "maxmind_api": maxmind_status,
        "response_time_ms": round(response_time * 1000, 2),
        "environment": os.getenv("RAILWAY_ENVIRONMENT_NAME", "development")
    }

@app.get("/geolocate")
async def geolocate(ip: str) -> Dict[str, Any]:
    """Geolocate an IP address using MaxMind web service."""
    try:
        response = client.city(ip)
        
        return {
            "ip": ip,
            "status": "success",
            "location": {
                "country": {
                    "name": response.country.name,
                    "iso_code": response.country.iso_code
                },
                "city": response.city.name if response.city.name else None,
                "postal_code": response.postal.code if response.postal.code else None,
                "latitude": response.location.latitude,
                "longitude": response.location.longitude,
                "time_zone": response.location.time_zone if response.location.time_zone else None
            },
            "network": {
                "isp": response.traits.isp if response.traits.isp else None,
                "organization": response.traits.organization if response.traits.organization else None,
                "autonomous_system_number": response.traits.autonomous_system_number if response.traits.autonomous_system_number else None,
                "autonomous_system_organization": response.traits.autonomous_system_organization if response.traits.autonomous_system_organization else None
            }
        }
    except geoip2.errors.AddressNotFoundError:
        raise HTTPException(status_code=404, detail="IP address not found in database")
    except geoip2.errors.AuthenticationError:
        raise HTTPException(status_code=401, detail="Invalid MaxMind credentials")
    except geoip2.errors.OutOfQueriesError:
        raise HTTPException(status_code=429, detail="MaxMind query limit reached")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Geolocation error: {str(e)}") 