# Configuration for AWS Deployment

## Prerequisites

1. **AWS EC2 Instance** (t3.medium or larger recommended)
   - Ubuntu 20.04 LTS
   - At least 4GB RAM
   - 20GB storage

2. **Domain Name** (optional but recommended)
   - Configure DNS to point to your EC2 instance
   - SSL certificate for HTTPS

## Environment Variables

Create a `.env` file with the following variables:

```bash
# Basic Configuration
DEBUG=False
SECRET_KEY=your-super-secret-key-here

# Database (use RDS for production)
DATABASE_URL=postgresql://username:password@your-rds-endpoint:5432/healthcare_db

# WhatsApp Business API
WHATSAPP_TOKEN=your-whatsapp-access-token
WHATSAPP_PHONE_NUMBER_ID=your-phone-number-id
WHATSAPP_BUSINESS_ACCOUNT_ID=your-business-account-id

# Twilio SMS
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=+1234567890

# Government Health API (when available)
GOVERNMENT_HEALTH_API_URL=https://api.gov.health.in
GOVERNMENT_HEALTH_API_KEY=your-government-api-key

# Redis (use ElastiCache for production)
REDIS_URL=redis://your-redis-cluster-endpoint:6379

# Cloud Storage
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=ap-south-1
AWS_S3_BUCKET=healthcare-chatbot-data

# Allowed Hosts
ALLOWED_HOSTS=your-domain.com,your-ec2-ip,localhost
```

## Deployment Steps

1. **Launch EC2 Instance**
   ```bash
   # Choose Ubuntu 20.04 LTS
   # Instance type: t3.medium or larger
   # Security Group: Allow ports 22, 80, 443
   ```

2. **Run Deployment Script**
   ```bash
   chmod +x deployment/aws/deploy.sh
   ./deployment/aws/deploy.sh
   ```

3. **Configure Environment**
   ```bash
   cd SIH_Demo
   nano .env
   # Add your actual configuration values
   ```

4. **Restart Services**
   ```bash
   docker-compose down
   docker-compose up --build -d
   ```

## Production Considerations

1. **Database**: Use Amazon RDS PostgreSQL for production
2. **Cache**: Use Amazon ElastiCache Redis
3. **Load Balancer**: Use Application Load Balancer
4. **SSL**: Use AWS Certificate Manager
5. **Monitoring**: CloudWatch and application logs
6. **Backup**: Regular database backups
7. **Security**: VPC, security groups, IAM roles

## Scaling

- Use Auto Scaling Groups for multiple instances
- Consider ECS or EKS for container orchestration
- Use CloudFront for global distribution
- Implement database read replicas

## Monitoring and Logs

```bash
# Check application logs
docker-compose logs healthcare-chatbot

# Monitor system resources
htop

# Check API health
curl http://localhost:8000/api/v1/status
```