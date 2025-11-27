# Event Ticketing System (Serverless Ticketmaster Clone)

## Overview

This is a cloud-native, serverless ticketing platform inspired by Ticketmaster.
Users can browse events, view event details, reserve/purchase tickets, and view order history.

The system is built with AWS managed services and a microservices architecture.
Frontend is static HTML/JS hosted on S3 + CloudFront.
Backend is API Gateway + Lambda + DynamoDB + SQS.

## Tech Stack

### Frontend
- HTML + CSS + JavaScript (static)
- ted on AWS S3 + CloudFront

### Backend
- AWS Lambda (business logic)
- Amazon API Gateway (REST API)
- Amazon DynamoDB (events & orders)
- Amazon SQS (order event queue)
- AWS IAM (permissions)
- AWS CloudWatch (logs)

###  Infrastructure
- AWS CDK (Python)

### API Summary
- POST /register – create new user 
- POST /login – login and return token (simple mock token)
- GET /events – list all events 
- GET /events/{eventId} – event detail 
- POST /purchase – purchase tickets 
- GET /orders?userId=xxx – get user orders 
- GET /orders/{orderId} – get order detail

## Team Members
- Bo Pang(DynamoDB + SQS + Lambda business logic)
- Peixin Yuan (API Gateway + Lambda business logic)
- Yuxin Qin (Frontend + S3 + CloudFront + Infra Skeleton)

## Deployment (CDK)
```
cd backend/cdk
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cdk bootstrap
cdk deploy
```
This deploys all backend resources.

Frontend can be deployed with:

```
aws s3 sync frontend/ s3://your-frontend-bucket/
```

CloudFront updates automatically.