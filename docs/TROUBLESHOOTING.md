# ARGUS Troubleshooting Guide

## Common Issues

### Service Won't Start
```bash
# Check if port is already in use
lsof -i :8540  # For SAGE
lsof -i :8509  # For XSCRAPER

# Kill existing process
kill -9 <PID>
```

### API Key Errors
- Verify keys in .env file
- Check key permissions
- Ensure quotes around keys

### Database Connection Issues
```bash
# Test S3 connection
aws s3 ls s3://your-bucket/

# Check AWS credentials
aws configure list
```

### No Data Showing
1. Check cron jobs: `crontab -l`
2. View logs: `tail -f logs/*.log`
3. Test API: `curl http://localhost:8540/api/feed`

### AI Enrichment Not Working
- Check Anthropic API key
- Monitor usage/limits
- Review enrichment logs

### Email Fetch Failing
- Verify Gmail app password
- Check IMAP enabled
- Test connection manually

## Log Locations
- SAGE: `logs/sage4_cron.log`
- XSCRAPER: `logs/xscraper_30min.log`
- Enrichment: `logs/smart_enrichment.log`

## Support
Open an issue on GitHub with:
- Error messages
- Log excerpts
- System configuration
