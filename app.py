import boto3
import time
import os
from botocore.exceptions import ClientError

# DynamoDB 設置
dynamodb = boto3.resource('dynamodb',
                          endpoint_url=os.environ.get('DYNAMODB_ENDPOINT', 'http://localhost:8000'),
                          region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-west-2'),
                          aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID', 'fakeMyKeyId'),
                          aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY', 'fakeSecretAccessKey'))

# 創建表（如果不存在）
def create_table():
    try:
        table = dynamodb.create_table(
            TableName='UserMessages',
            KeySchema=[
                {'AttributeName': 'uid', 'KeyType': 'HASH'},
                {'AttributeName': 't', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'uid', 'AttributeType': 'N'},
                {'AttributeName': 't', 'AttributeType': 'N'},
                {'AttributeName': 'cid_t', 'AttributeType': 'S'}
            ],
            LocalSecondaryIndexes=[
                {
                    'IndexName': 'CidTimeIndex',
                    'KeySchema': [
                        {'AttributeName': 'uid', 'KeyType': 'HASH'},
                        {'AttributeName': 'cid_t', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'}
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        table.wait_until_exists()
        print("Table created successfully.")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print("Table already exists.")
        else:
            raise

# 發送消息
def send_message(sender_id, receiver_id, content, timestamp):
    table = dynamodb.Table('UserMessages')
    
    items = [
        {
            'uid': sender_id,
            't': timestamp,
            'cid_t': f"{receiver_id}#{timestamp}",
            'message': content,
            'is_sender': True
        },
        {
            'uid': receiver_id,
            't': timestamp,
            'cid_t': f"{sender_id}#{timestamp}",
            'message': content,
            'is_sender': False
        }
    ]
    
    for item in items:
        try:
            table.put_item(
                Item=item,
                ConditionExpression='attribute_not_exists(uid) AND attribute_not_exists(t)'
            )
            print(f"Message sent: {item}")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                print(f"Item already exists: {item}")
            else:
                print(f"Error sending message: {e}")
                raise

# 獲取對話
def get_conversation(user_id, other_user_id, start_time, end_time):
    table = dynamodb.Table('UserMessages')
    
    response = table.query(
        IndexName='CidTimeIndex',
        KeyConditionExpression='uid = :uid AND cid_t BETWEEN :start AND :end',
        ExpressionAttributeValues={
            ':uid': user_id,
            ':start': f"{other_user_id}#{start_time}",
            ':end': f"{other_user_id}#{end_time}"
        }
    )
    
    return response['Items']

if __name__ == "__main__":
    create_table()
    
    # 示例：發送消息
    send_message(123, 456, "Hello, how are you?", 100)
    send_message(456, 123, "I'm fine, thank you!", 101)
    
    # 示例：獲取對話
    start_time = 0
    end_time = 105
    conversation = get_conversation(123, 456, start_time, end_time)
    
    print("Conversation:")
    for msg in conversation:
        print(f"{'Sent' if msg['is_sender'] else 'Received'}: {msg['message']} at {msg['t']}")
