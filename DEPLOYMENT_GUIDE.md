# Deploy to Render.com - Step by Step

## Prerequisites
- GitHub account
- Render.com account (free)

## Step 1: Push Code to GitHub

1. Create a new repository on GitHub
2. In your terminal, run:
```bash
git init
git add .
git commit -m "Initial commit - School Management System"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git push -u origin main
```

## Step 2: Deploy on Render.com

1. Go to https://render.com and sign up (free)
2. Click "New +" → "Blueprint"
3. Connect your GitHub repository
4. Render will automatically detect `render.yaml` and create:
   - PostgreSQL database
   - Web service

5. Click "Apply" to start deployment

## Step 3: Set Environment Variables

After deployment starts, go to your web service and add these environment variables:

```
ALLOWED_HOSTS=your-app-name.onrender.com
EMAIL_HOST=mail.privateemail.com
EMAIL_PORT=465
EMAIL_USE_SSL=True
EMAIL_HOST_USER=cranictech@elincorporatedlimited.com
EMAIL_HOST_PASSWORD=Happylife227.#
DEFAULT_FROM_EMAIL=cranictech@elincorporatedlimited.com
```

## Step 4: Create Superuser

Once deployed, go to Shell tab in Render dashboard and run:
```bash
python manage.py createsuperuser
```

## Step 5: Access Your Site

Your site will be available at:
```
https://your-app-name.onrender.com
```

## Important Notes

- First deployment takes 5-10 minutes
- Free tier sleeps after 15 minutes of inactivity
- Upgrade to paid plan ($7/month) for always-on service
- Database backups are automatic on paid plans

## Troubleshooting

If deployment fails:
1. Check build logs in Render dashboard
2. Verify all environment variables are set
3. Make sure `build.sh` has execute permissions

## Custom Domain (Optional)

To use your own domain:
1. Go to Settings → Custom Domain
2. Add your domain
3. Update DNS records as instructed
