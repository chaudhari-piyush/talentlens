# TalentLens Deployment Guide for Render

This guide will walk you through deploying the TalentLens API on Render.

## Prerequisites

1. A [Render](https://render.com) account
2. A GitHub repository with your code
3. Firebase project credentials
4. Gemini API key

## Deployment Steps

### 1. Prepare Your Repository

Ensure your repository includes all the necessary files:
- `render.yaml` - Render configuration (already included)
- `build.sh` - Build script (already included)
- `requirements-render.txt` - Python dependencies (already included)
- `runtime.txt` - Python version specification (already included)

### 2. Set Up Firebase Credentials

Since we can't commit the Firebase credentials file, you have two options:

**Option A: Use Firebase Project ID (Limited functionality)**
- Set the `FIREBASE_PROJECT_ID` environment variable in Render

**Option B: Use Base64 Encoded Credentials (Full functionality)**
1. Encode your Firebase credentials:
   ```bash
   base64 -i app/config/ServiceAccountKey.json -o firebase-creds-base64.txt
   ```
2. Copy the content of `firebase-creds-base64.txt`
3. In Render, set an environment variable `FIREBASE_CREDENTIALS_BASE64` with this value
4. Update `app/core/auth.py` to decode and use these credentials

### 3. Deploy on Render

1. **Fork/Push to GitHub**
   - Ensure your code is in a GitHub repository

2. **Create New Web Service on Render**
   - Go to your Render dashboard
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select your repository

3. **Configure the Service**
   - **Name**: talentlens-api
   - **Environment**: Python
   - **Build Command**: `./build.sh`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

4. **Set Environment Variables**
   
   In the Render dashboard, add these environment variables:
   
   ```
   ENVIRONMENT=production
   SECRET_KEY=<generate-a-secure-key>
   FIREBASE_PROJECT_ID=<your-firebase-project-id>
   GEMINI_API_KEY=<your-gemini-api-key>
   ```

   Optional (if using encoded credentials):
   ```
   FIREBASE_CREDENTIALS_BASE64=<base64-encoded-credentials>
   ```

5. **Create PostgreSQL Database**
   - The `render.yaml` will automatically create a PostgreSQL database
   - Render will automatically set the `DATABASE_URL` environment variable

6. **Deploy**
   - Click "Create Web Service"
   - Render will automatically build and deploy your application

### 4. Post-Deployment

1. **Run Migrations**
   - Migrations will run automatically during the build process
   - Check the logs to ensure they completed successfully

2. **Verify Deployment**
   - Visit `https://your-app-name.onrender.com/health`
   - You should see: `{"status": "healthy"}`

3. **Test API**
   - Use the Postman collection to test your deployed API
   - Update the `base_url` variable to your Render URL

## Environment Variables Reference

| Variable | Description | Required |
|----------|-------------|----------|
| `ENVIRONMENT` | Set to "production" for Render | Yes |
| `SECRET_KEY` | Secret key for JWT tokens | Yes |
| `DATABASE_URL` | PostgreSQL connection string (auto-set by Render) | Yes |
| `GEMINI_API_KEY` | Google Gemini API key | Yes |
| `FIREBASE_PROJECT_ID` | Firebase project ID | Yes* |
| `FIREBASE_CREDENTIALS_PATH` | Path to Firebase credentials file | No |
| `FIREBASE_CREDENTIALS_BASE64` | Base64 encoded Firebase credentials | No |

*Either `FIREBASE_PROJECT_ID` or credentials are required

## Monitoring and Logs

1. **View Logs**
   - In Render dashboard, click on your service
   - Go to "Logs" tab
   - Monitor for any errors

2. **Performance**
   - Check "Metrics" tab for CPU and memory usage
   - Upgrade plan if needed

## Troubleshooting

### Common Issues

1. **Build Fails**
   - Check `requirements-render.txt` for syntax errors
   - Ensure Python version in `runtime.txt` is supported

2. **Database Connection Issues**
   - Verify `DATABASE_URL` is set correctly
   - Check PostgreSQL service is running

3. **Firebase Authentication Errors**
   - Ensure Firebase credentials or project ID are set
   - Verify credentials are valid

4. **Gemini API Errors**
   - Check API key is valid
   - Verify you haven't exceeded rate limits

### Updating the Application

1. Push changes to your GitHub repository
2. Render will automatically detect changes and redeploy
3. Monitor logs during deployment

## Security Considerations

1. **Never commit sensitive data**
   - Firebase credentials
   - API keys
   - Database passwords

2. **Use environment variables** for all sensitive configuration

3. **Enable HTTPS** (Render provides this automatically)

4. **Restrict CORS** in production
   - Update `allowed_origins` in `main.py` with your frontend URLs

## Scaling

If you need to scale:

1. **Upgrade Render Plan**
   - Go to service settings
   - Choose a higher tier plan

2. **Database Scaling**
   - Upgrade PostgreSQL plan as needed

3. **Add Redis** (optional)
   - For caching and session management
   - Add via Render dashboard

## Support

- [Render Documentation](https://render.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [TalentLens GitHub Issues](https://github.com/yourusername/talentlens/issues)