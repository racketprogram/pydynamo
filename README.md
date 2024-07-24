# DynamoDB Chat Application Demo

## Introduction
This project demonstrates how to design and implement a simple chat application backend using Amazon DynamoDB. It showcases an efficient data model design to support fast message storage and retrieval.

## Table Design

### Table Name: UserMessages

#### Primary Key Structure:
- Partition Key: `uid` (Number) - User ID
- Sort Key: `t` (Number) - Timestamp in milliseconds

#### Local Secondary Index:
- Name: CidTimeIndex
- Partition Key: `uid` (Number) - User ID
- Sort Key: `cid_t` (String) - Composite key of Conversation ID and Timestamp

#### Attributes:
- `message` (String) - Message content
- `is_sender` (Boolean) - Indicates if the user is the sender

## Design Rationale

1. **Efficient Message Retrieval**: The primary key structure allows quick retrieval of all messages for a specific user, sorted by time.

2. **Conversation Queries**: The Local Secondary Index (CidTimeIndex) enables efficient querying of conversations between two users within a specific time range.

3. **Dual Write Approach**: Each message is stored twice (for sender and receiver), allowing fast access from both users' perspectives without additional queries.

4. **Scalability**: The design supports high write throughput and efficient read operations, crucial for chat applications.

5. **Time-Based Queries**: Using timestamp as the sort key facilitates easy implementation of time-range queries and message ordering.

6. **Flexible Conversation Handling**: The `cid_t` attribute combines conversation ID and timestamp, allowing for efficient filtering and sorting within conversations.

This design optimizes for the most common chat application operations: sending messages, retrieving recent messages, and querying specific conversations, all while maintaining DynamoDB's scalability benefits.