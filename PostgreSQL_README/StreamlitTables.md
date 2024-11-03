# PostgreSQL Database Guide
Professional Services ETL System Database Documentation

## Database Tables

### 1. webhook_responses
Stores all webhook interaction details with Bonzo API.

```sql
CREATE TABLE webhook_responses (
    id SERIAL PRIMARY KEY,
    lead_id VARCHAR(255),
    payload JSONB,
    response_code INTEGER,
    response_body TEXT,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_webhook_responses_lead_id ON webhook_responses(lead_id);
CREATE INDEX idx_webhook_responses_sent_at ON webhook_responses(sent_at);
```

### 2. processing_logs
Tracks file processing statistics and outcomes.

```sql
CREATE TABLE processing_logs (
    id SERIAL PRIMARY KEY,
    source_type VARCHAR(50),
    file_name VARCHAR(255),
    records_processed INTEGER,
    success_count INTEGER,
    failure_count INTEGER,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_processing_logs_source_type ON processing_logs(source_type);
CREATE INDEX idx_processing_logs_processed_at ON processing_logs(processed_at);
```

## Common Analytics Queries

### Success Rate by Source Type
```sql
SELECT 
    source_type,
    SUM(success_count) as total_successes,
    SUM(failure_count) as total_failures,
    ROUND(100.0 * SUM(success_count) / NULLIF(SUM(success_count + failure_count), 0), 2) as success_rate
FROM processing_logs
GROUP BY source_type
ORDER BY success_rate DESC;
```

### Daily Processing Volume
```sql
SELECT 
    DATE_TRUNC('day', sent_at) as day,
    COUNT(*) as total_requests,
    COUNT(*) FILTER (WHERE response_code = 200) as successful_requests
FROM webhook_responses
GROUP BY day
ORDER BY day DESC;
```

### Recent Errors Analysis
```sql
SELECT 
    lead_id,
    response_code,
    response_body,
    sent_at
FROM webhook_responses
WHERE response_code != 200
ORDER BY sent_at DESC
LIMIT 100;
```

### Processing Volume Analytics
```sql
-- Hourly processing volume
SELECT 
    DATE_TRUNC('hour', sent_at) as hour,
    COUNT(*) as leads_processed
FROM webhook_responses
WHERE sent_at >= NOW() - INTERVAL '30 days'
GROUP BY hour
ORDER BY hour;

-- Success rate by hour
SELECT 
    DATE_TRUNC('hour', sent_at) as hour,
    COUNT(*) as total_requests,
    COUNT(*) FILTER (WHERE response_code = 200) as successful_requests,
    ROUND(100.0 * COUNT(*) FILTER (WHERE response_code = 200) / COUNT(*), 2) as success_rate
FROM webhook_responses
WHERE sent_at >= NOW() - INTERVAL '24 hours'
GROUP BY hour
ORDER BY hour;
```

### Payload Field Analysis
```sql
-- Credit score distribution
SELECT 
    CASE 
        WHEN (payload->>'credit_score')::int < 580 THEN 'Poor (<580)'
        WHEN (payload->>'credit_score')::int < 670 THEN 'Fair (580-669)'
        WHEN (payload->>'credit_score')::int < 740 THEN 'Good (670-739)'
        WHEN (payload->>'credit_score')::int < 800 THEN 'Very Good (740-799)'
        ELSE 'Excellent (800+)'
    END as credit_range,
    COUNT(*) as count
FROM webhook_responses
WHERE payload->>'credit_score' IS NOT NULL
GROUP BY credit_range
ORDER BY credit_range;

-- Loan amount ranges
SELECT 
    CASE 
        WHEN (payload->>'current_balance')::numeric < 100000 THEN '<$100k'
        WHEN (payload->>'current_balance')::numeric < 250000 THEN '$100k-$250k'
        WHEN (payload->>'current_balance')::numeric < 500000 THEN '$250k-$500k'
        ELSE '$500k+'
    END as loan_range,
    COUNT(*) as count,
    AVG((payload->>'current_balance')::numeric) as avg_loan_amount
FROM webhook_responses
WHERE payload->>'current_balance' IS NOT NULL
GROUP BY loan_range
ORDER BY loan_range;
```

### Error Analysis
```sql
-- Error distribution by type
SELECT 
    response_code,
    COUNT(*) as error_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) as error_percentage
FROM webhook_responses
WHERE response_code != 200
    AND sent_at >= NOW() - INTERVAL '30 days'
GROUP BY response_code
ORDER BY error_count DESC;

-- Recent errors with details
SELECT 
    lead_id,
    response_code,
    response_body,
    sent_at,
    payload
FROM webhook_responses
WHERE response_code != 200
    AND sent_at >= NOW() - INTERVAL '24 hours'
ORDER BY sent_at DESC;
```

## Maintenance Procedures

### Cleanup Old Records
```sql
-- Remove webhook responses older than 90 days
DELETE FROM webhook_responses
WHERE sent_at < NOW() - INTERVAL '90 days';

-- Remove processing logs older than 90 days
DELETE FROM processing_logs
WHERE processed_at < NOW() - INTERVAL '90 days';
```

### Vacuum and Analyze
Regular maintenance to optimize performance:
```sql
VACUUM ANALYZE webhook_responses;
VACUUM ANALYZE processing_logs;
```

### Performance Optimization
```sql
-- Add indexes for analytics queries
CREATE INDEX idx_webhook_responses_payload_credit ON webhook_responses ((payload->>'credit_score'));
CREATE INDEX idx_webhook_responses_payload_balance ON webhook_responses ((payload->>'current_balance'));
```

## Example Usage

### Track Processing Results
```python
db.log_processing(
    source_type='transunion',
    file_name='leads_batch_001.csv',
    records_processed=100,
    success_count=95,
    failure_count=5
)
```

### Log Webhook Response
```python
db.log_webhook_response(
    lead_id='TU123456',
    payload=json.dumps(webhook_data),
    response_code=200,
    response_body='{"status": "success"}'
)
```
