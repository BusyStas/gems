# Deployment Guide for Gems Hub

## Prerequisites

- Google Cloud Platform account
- Google Cloud SDK installed (`gcloud` command)
- Docker installed (for local testing)

## Option 1: Deploy to Google Cloud Run (Recommended)

Cloud Run is serverless, scales automatically, and only charges for actual usage.

### Step 1: Set up Google Cloud

```bash
# Login to Google Cloud
gcloud auth login

# Set your project ID
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### Step 2: Deploy

```bash
# Deploy directly from source
gcloud run deploy gems-hub \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars "SECRET_KEY=your-secret-key-here,SITE_URL=https://your-app-url.run.app"
```

Or use Cloud Build:

```bash
# Submit build
gcloud builds submit --config cloudbuild.yaml

# The service will be automatically deployed
```

### Step 3: Set up Custom Domain (Optional)

```bash
# Map your domain
gcloud run domain-mappings create \
  --service gems-hub \
  --domain preciousstone.info \
  --region us-central1
```

## Option 2: Deploy to Google App Engine

App Engine provides a fully managed platform with automatic scaling.

### Step 1: Initialize App Engine

```bash
# Create App Engine application (one-time setup)
gcloud app create --region=us-central
```

### Step 2: Deploy

```bash
# Deploy the application
gcloud app deploy

# View in browser
gcloud app browse
```

## Option 3: Docker Container (Any Platform)

### Build Docker Image

```bash
# Build the image
docker build -t gems-hub .

# Test locally
docker run -p 8080:8080 \
  -e SECRET_KEY=your-secret-key \
  -e SITE_URL=http://localhost:8080 \
  gems-hub

# Open http://localhost:8080
```

### Deploy to Container Registry

```bash
# Tag image for Google Container Registry
docker tag gems-hub gcr.io/YOUR_PROJECT_ID/gems-hub

# Push to registry
docker push gcr.io/YOUR_PROJECT_ID/gems-hub
```

## Environment Variables

Set these environment variables in your deployment:

- `SECRET_KEY`: Generate with `python -c "import secrets; print(secrets.token_hex(32))"`
- `SITE_URL`: Your production URL (e.g., https://preciousstone.info)
- `GOOGLE_ANALYTICS_ID`: (Optional) Your GA tracking ID
- `GOOGLE_SEARCH_CONSOLE_VERIFICATION`: (Optional) Verification code

### Setting Environment Variables in Cloud Run

```bash
gcloud run services update gems-hub \
  --region us-central1 \
  --set-env-vars "SECRET_KEY=xxx,SITE_URL=https://preciousstone.info"
```

## Post-Deployment

### 1. Update Sitemap URL

If using a custom domain, update `/static/sitemap.xml` with your actual URL.

### 2. Submit to Search Engines

- Google Search Console: https://search.google.com/search-console
- Submit sitemap: https://your-domain.com/sitemap.xml

### 3. Set up Google Analytics (Optional)

1. Create GA4 property
2. Get Measurement ID
3. Set `GOOGLE_ANALYTICS_ID` environment variable

### 4. Configure Custom Domain

Follow Google Cloud documentation to:
- Verify domain ownership
- Map domain to your service
- Set up SSL certificate (automatic with Cloud Run)

## Monitoring

### View Logs

```bash
# Cloud Run logs
gcloud run logs read gems-hub --region us-central1 --limit 50

# App Engine logs
gcloud app logs tail
```

### View Metrics

```bash
# Open Cloud Console
gcloud run services describe gems-hub --region us-central1
```

## Troubleshooting

### Build Fails

- Check Dockerfile syntax
- Verify requirements.txt has all dependencies
- Check Python version compatibility

### App Won't Start

- Check logs: `gcloud run logs read`
- Verify environment variables are set
- Test Docker image locally first

### 502/503 Errors

- Check memory limits (increase if needed)
- Verify cold start timeout
- Check application logs for errors

## Cost Optimization

### Cloud Run Tips

- Set max instances to control costs
- Use minimum instances only if needed for performance
- Configure CPU throttling for cost savings

```bash
gcloud run services update gems-hub \
  --region us-central1 \
  --max-instances 10 \
  --cpu-throttling \
  --memory 512Mi
```

## Security

### Best Practices

1. Use strong `SECRET_KEY`
2. Keep dependencies updated
3. Use HTTPS only (automatic with Cloud Run)
4. Set appropriate CORS headers if needed
5. Review and update security headers

## Continuous Deployment

### Set up GitHub Actions (Optional)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Cloud Run

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - uses: google-github-actions/setup-gcloud@v0
        with:
          project_id: ${{ secrets.GCP_PROJECT_ID }}
          service_account_key: ${{ secrets.GCP_SA_KEY }}
          
      - run: |
          gcloud builds submit --config cloudbuild.yaml
```

## Support

For issues or questions:
- Check logs first
- Review Google Cloud documentation
- Open an issue on GitHub
