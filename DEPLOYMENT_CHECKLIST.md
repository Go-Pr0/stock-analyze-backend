# Backend Deployment Checklist

## Pre-Deployment Verification

### Required Files
- [ ] `Dockerfile` exists and is properly configured
- [ ] `railway.json` exists with correct configuration
- [ ] `requirements.txt` contains all dependencies
- [ ] `main.py` is the correct entry point
- [ ] `.env` file exists (for local development)
- [ ] All API modules exist (`api/`, `models/`, `services/`)

### Code Structure
- [ ] `main.py` imports all necessary modules
- [ ] Database models are properly defined
- [ ] API routes are correctly configured
- [ ] Authentication system is implemented
- [ ] CORS is properly configured

### Railway Configuration
- [ ] `railway.json` uses correct Dockerfile path
- [ ] Health check endpoint is `/health`
- [ ] Start command uses `$PORT` variable
- [ ] Build configuration is set to DOCKERFILE

## Railway Setup Checklist

### Service Creation
- [ ] Railway project created
- [ ] PostgreSQL database service added
- [ ] Backend service created
- [ ] Repository connected to backend service
- [ ] Root directory set to `backend`

### Environment Variables
- [ ] `GEMINI_API_KEY` set with valid API key
- [ ] `JWT_SECRET_KEY` set with secure 64+ character string
- [ ] `JWT_ALGORITHM` set to `HS256`
- [ ] `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` set to `30`
- [ ] `DATABASE_URL` set to `${{Postgres.DATABASE_URL}}`

### Optional Variables (after frontend deployment)
- [ ] `FRONTEND_URL` set to frontend Railway URL
- [ ] `ALLOWED_ORIGINS` includes frontend URL

## Post-Deployment Verification

### Health Checks
- [ ] `/health` endpoint returns 200 status
- [ ] Database connection is confirmed
- [ ] API documentation accessible at `/docs`

### API Testing
- [ ] Root endpoint `/` returns API info
- [ ] Authentication endpoints work
- [ ] Research endpoints are accessible
- [ ] CORS headers are present

### Database
- [ ] Tables are created automatically
- [ ] User registration works
- [ ] Data persistence is confirmed

## Troubleshooting

### Build Issues
- [ ] Check Railway build logs
- [ ] Verify all dependencies in requirements.txt
- [ ] Confirm Dockerfile syntax

### Runtime Issues
- [ ] Check Railway deploy logs
- [ ] Verify environment variables
- [ ] Test database connectivity

### API Issues
- [ ] Check HTTP logs in Railway
- [ ] Verify CORS configuration
- [ ] Test authentication flow

## Security Verification

- [ ] JWT secret is secure and not default value
- [ ] Database credentials are not hardcoded
- [ ] API keys are in environment variables
- [ ] CORS origins are properly restricted

## Performance Checks

- [ ] Health check responds quickly
- [ ] API endpoints have reasonable response times
- [ ] Database queries are optimized
- [ ] Error handling is implemented

## Final Verification

- [ ] Backend URL is accessible publicly
- [ ] All API endpoints work as expected
- [ ] Authentication flow is complete
- [ ] Ready for frontend integration