#!/usr/bin/env python3
"""
Seed script to preload sample events into DynamoDB EventsTable

"""

import boto3
import json
import argparse
import os
from decimal import Decimal
from botocore.exceptions import ClientError

# Sample events data
SAMPLE_EVENTS = [
    {
        "eventId": "e001",
        "name": "Summer Music Festival 2026",
        "description": "An outdoor summer festival featuring top international musicians.",
        "imageUrl": "https://images.unsplash.com/photo-1470229722913-7c0e2dbbafd3?w=800",
        "remainingTickets": 500,
        "performer": "Global Artists Lineup",
        "venue": "Central Park Open Grounds",
        "city": "New York, NY",
        "date": "2026-07-15",
        "price": 129,
        "category": "Music Festival"
    },
    {
        "eventId": "e002",
        "name": "Tech Conference 2026",
        "description": "Annual technology conference with AI, cloud computing, and software engineering sessions.",
        "imageUrl": "https://images.unsplash.com/photo-1505373877841-8d25f7d46678?w=800",
        "remainingTickets": 200,
        "performer": "Industry Leaders & Keynote Speakers",
        "venue": "San Jose Convention Center",
        "city": "San Jose, CA",
        "date": "2026-09-05",
        "price": 399,
        "category": "Technology"
    },
    {
        "eventId": "e003",
        "name": "Basketball Championship Finals",
        "description": "Watch the intense finals of the professional basketball league!",
        "imageUrl": "https://images.unsplash.com/photo-1546519638-68e109498ffc?w=800",
        "remainingTickets": 1000,
        "performer": "Pro League Finalists",
        "venue": "Staples Center",
        "city": "Los Angeles, CA",
        "date": "2026-06-12",
        "price": 250,
        "category": "Sports"
    },
    {
        "eventId": "e004",
        "name": "Comedy Night Stand-Up",
        "description": "Top comedians performing live stand-up comedy.",
        "imageUrl": "https://images.unsplash.com/photo-1508214751196-bcfd4ca60f91?w=800",
        "remainingTickets": 150,
        "performer": "Headliner Comedians",
        "venue": "Downtown Theater Hall",
        "city": "Boston, MA",
        "date": "2026-03-22",
        "price": 49,
        "category": "Comedy"
    },
    {
        "eventId": "e005",
        "name": "Art Exhibition: Modern Masters",
        "description": "Contemporary art collection with guided tours and artist meet-ups.",
        "imageUrl": "https://images.unsplash.com/photo-1541961017774-22349e4a1262?w=800",
        "remainingTickets": 80,
        "performer": "Featured Modern Artists",
        "venue": "Metropolitan Art Gallery",
        "city": "Chicago, IL",
        "date": "2026-04-10",
        "price": 35,
        "category": "Art"
    }
]


def convert_to_dynamodb_item(item):
    """Convert Python dict to DynamoDB format (numbers as Decimal)"""
    return json.loads(json.dumps(item), parse_float=Decimal)


def seed_events(table_name, region='us-east-1'):
    """Seed sample events into DynamoDB table"""
    dynamodb = boto3.resource('dynamodb', region_name=region)
    table = dynamodb.Table(table_name)

    print(f"Seeding events into table: {table_name}")
    print(f"Region: {region}\n")

    success_count = 0
    error_count = 0

    for event in SAMPLE_EVENTS:
        try:
            # Convert to DynamoDB format
            dynamodb_item = convert_to_dynamodb_item(event)

            # Put item into table
            table.put_item(Item=dynamodb_item)
            print(f"Added event: {event['name']} (ID: {event['eventId']})")
            success_count += 1

        except ClientError as e:
            print(f"Error adding event {event['eventId']}: {e}")
            error_count += 1
        except Exception as e:
            print(f"Unexpected error adding event {event['eventId']}: {e}")
            error_count += 1

    print(f"\n{'='*50}")
    print(
        f"Summary: {success_count} events added successfully, {error_count} errors")
    print(f"{'='*50}")


def main():
    parser = argparse.ArgumentParser(
        description='Seed sample events into DynamoDB')
    parser.add_argument('--table-name',
                        default=os.environ.get('EVENTS_TABLE'),
                        help='DynamoDB table name (or set EVENTS_TABLE env var)')
    parser.add_argument('--region',
                        default=os.environ.get('AWS_REGION', 'us-east-1'),
                        help='AWS region (default: us-east-1)')

    args = parser.parse_args()

    if not args.table_name:
        print("Error: Table name is required!")
        print("Usage: python seed_events.py --table-name <TABLE_NAME>")
        print("   or: export EVENTS_TABLE=<TABLE_NAME> && python seed_events.py")
        return

    seed_events(args.table_name, args.region)


if __name__ == '__main__':
    main()
