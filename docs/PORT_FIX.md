# Railway PORT Environment Variable Fix

## Problem ❌

Railway's `$PORT` environment variable was not being properly expanded in the start command:

```
Error: Invalid value for '--port': '$PORT' is not a valid integer.
```

## Root Cause

Railway's `startCommand` in `railway.json` was using shell variable expansion that wasn't working:
```json
"startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT"
```

## Solution ✅

### Option 1: Start Script (Recommended)

Created `start.sh` script that handles PORT environment variable:

```bash
#!/bin/bash
PORT=${PORT:-8000}
echo "🚀 Starting FastAPI server on port $PORT"
exec uvicorn main:app --host 0.0.0.0 --port $PORT
```

Updated `railway.json`:
```json
{
  "deploy": {
    "startCommand": "./start.sh"
  }
}
```

### Option 2: Python Code Handling

Updated `main.py` to handle PORT in Python:
```python
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
```

With `railway.json`:
```json
{
  "deploy": {
    "startCommand": "python main.py"
  }
}
```

## Files Changed

1. ✅ `start.sh` - New startup script
2. ✅ `Dockerfile` - Made start.sh executable
3. ✅ `railway.json` - Updated startCommand
4. ✅ `main.py` - Added PORT handling in Python

## Testing

After redeployment, the backend should:
1. ✅ Start successfully on Railway's assigned port
2. ✅ Pass health check at `/health`
3. ✅ Be accessible via the public Railway URL

## Verification

Check Railway logs for:
```
🚀 Starting FastAPI server on port [RAILWAY_PORT]
```

Test health endpoint:
```
curl https://stock-analyze-backend-production.up.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "backend"
}
```

## Why This Happened

Railway provides the `PORT` environment variable, but shell variable expansion in `startCommand` doesn't always work as expected. Using a bash script or handling it in Python code ensures proper port binding.

## Next Steps

1. Redeploy the backend service
2. Check that it starts successfully
3. Test the health endpoint
4. Get the backend URL for frontend configuration