# Building Our Modern Data Platform: PostgreSQL Schema and Guide for the Team

Hello Team!

Welcome to our project aimed at implementing a modern data platform to enhance our business operations using Bonzo CRM. This guide provides a comprehensive PostgreSQL database schema and explains how it aligns with our goals. It's designed to help you understand the key concepts, how they benefit our business, and what steps we need to take to achieve them.

## Table of Contents
- [Introduction](#introduction)
- [Database Schema Overview](#database-schema-overview)
- [Table Definitions and Relationships](#table-definitions-and-relationships)
  - [Qualification Stages](#qualification-stages)
  - [Lead Sources](#lead-sources)
  - [Users (Team Members)](#users-team-members)
  - [Prospects](#prospects)
  - [Campaigns](#campaigns)
  - [Touches](#touches)
  - [Prospect Campaign Assignments](#prospect-campaign-assignments)
  - [Touch Engagements](#touch-engagements)
  - [Loans](#loans)
- [Indexes for Performance](#indexes-for-performance)
- [Sample Data Insertion](#sample-data-insertion)
- [Next Steps](#next-steps)
- [Conclusion](#conclusion)
- [Additional Resources](#additional-resources)

## Introduction

We're implementing a modern data stack that leverages an opinionated, standardized configuration of Bonzo CRM to enhance our managed services offering. This platform will enable us to:

- **Standardize Processes**: Implement proven qualification stages and workflows.
- **Enhance Client Success**: Provide actionable insights into sales pipelines, campaigns, and team performance.
- **Measure Lead Source Profitability**: Attribute leads to their sources and assess the effectiveness of paid lead sources.
- **Collaborate Effectively**: Share this project on GitHub to enable team collaboration and collective understanding.

## Database Schema Overview

Our database schema is designed to accurately reflect Bonzo's terminology and functionalities. The core entities include:

- **Qualification Stages**: Standardized stages a prospect moves through.
- **Lead Sources**: Origins of our prospects.
- **Users**: Team members interacting with prospects.
- **Prospects**: Potential clients or leads.
- **Campaigns**: Sequences of personalized touches sent to prospects.
- **Touches**: Individual messages within a campaign.
- **Prospect Campaign Assignments**: Tracks which prospects are enrolled in which campaigns.
- **Touch Engagements**: Logs interactions between prospects and touches.
- **Loans**: Mortgage-related information linked to prospects.

The schema ensures that we store raw data in the database and perform calculations and aggregations in our Business Intelligence (BI) layer using tools like Rill.

## Table Definitions and Relationships

### Qualification Stages

**Purpose**: Stores the standardized qualification stages used in Bonzo CRM.

```sql
CREATE TABLE qualification_stages (
    stage_id SERIAL PRIMARY KEY,
    stage_name VARCHAR(50) NOT NULL,
    stage_order INT NOT NULL,
    is_disqualify BOOLEAN DEFAULT FALSE
);
```

**Insert Data**:

```sql
INSERT INTO qualification_stages (stage_name, stage_order, is_disqualify)
VALUES
    ('Staging', 1, FALSE),
    ('Sending', 2, FALSE),
    ('Working', 3, FALSE),
    ('Pre-Qual', 4, FALSE),
    ('Pre-Approved', 5, FALSE),
    ('Hot PAL', 6, FALSE),
    ('O/I PAL', 7, FALSE),
    ('SPA/REFI', 8, FALSE),
    ('Re-Marketing', 9, TRUE);
```

### Lead Sources

**Purpose**: Stores information about different lead sources.

```sql
CREATE TABLE lead_sources (
    lead_source_id SERIAL PRIMARY KEY,
    source_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Users (Team Members)

**Purpose**: Stores information about team members.

```sql
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    bonzo_user_id UUID UNIQUE NOT NULL,
    role VARCHAR(20), -- e.g., 'admin', 'user'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Prospects

**Purpose**: Stores information about prospects, including their qualification stage and lead source.

```sql
CREATE TABLE prospects (
    prospect_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100),
    phone VARCHAR(20),
    lead_source_id INT REFERENCES lead_sources(lead_source_id),
    qualification_stage_id INT REFERENCES qualification_stages(stage_id),
    assigned_to INT REFERENCES users(user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    stage_entered_at TIMESTAMP WITH TIME ZONE,
    stage_exited_at TIMESTAMP WITH TIME ZONE,
    do_not_call BOOLEAN DEFAULT FALSE
);
```

### Campaigns

**Purpose**: Stores information about campaigns (sequences of touches).

```sql
CREATE TABLE campaigns (
    campaign_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Touches

**Purpose**: Represents individual touches within a campaign.

```sql
CREATE TABLE touches (
    touch_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID REFERENCES campaigns(campaign_id),
    touch_order INT NOT NULL,
    touch_type VARCHAR(20) NOT NULL, -- 'SMS', 'Email', 'Voicemail'
    content TEXT NOT NULL,
    scheduled_delay INT NOT NULL, -- Delay in minutes from the previous touch
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Prospect Campaign Assignments

**Purpose**: Tracks which prospects are enrolled in which campaigns.

```sql
CREATE TABLE prospect_campaign_assignments (
    assignment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prospect_id INT REFERENCES prospects(prospect_id),
    campaign_id UUID REFERENCES campaigns(campaign_id),
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) DEFAULT 'Active' -- 'Active', 'Completed', 'Opted Out'
);
```

### Touch Engagements

**Purpose**: Logs interactions between prospects and touches.

```sql
CREATE TABLE touch_engagements (
    engagement_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prospect_id INT REFERENCES prospects(prospect_id),
    touch_id UUID REFERENCES touches(touch_id),
    engagement_type VARCHAR(20), -- 'Sent', 'Delivered', 'Opened', 'Clicked', 'Responded'
    engagement_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    content TEXT, -- Content of the response, if applicable
    campaign_id UUID REFERENCES campaigns(campaign_id) -- Redundant but useful
);
```

### Loans

**Purpose**: Stores mortgage-related information linked to prospects.

```sql
CREATE TABLE loans (
    loan_id SERIAL PRIMARY KEY,
    prospect_id INT REFERENCES prospects(prospect_id),
    loan_amount NUMERIC,
    property_value NUMERIC,
    loan_type VARCHAR(50), -- e.g., 'Purchase', 'Refinance'
    interest_rate NUMERIC,
    status VARCHAR(20), -- e.g., 'Pending', 'Approved', 'Closed'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## Indexes for Performance

To optimize query performance, we've added indexes to frequently queried columns.

**Prospects Table**:

```sql
CREATE INDEX idx_prospects_lead_source_id ON prospects(lead_source_id);
CREATE INDEX idx_prospects_qualification_stage_id ON prospects(qualification_stage_id);
CREATE INDEX idx_prospects_assigned_to ON prospects(assigned_to);
```

**Touch Engagements Table**:

```sql
CREATE INDEX idx_te_prospect_id ON touch_engagements(prospect_id);
CREATE INDEX idx_te_touch_id ON touch_engagements(touch_id);
CREATE INDEX idx_te_campaign_id ON touch_engagements(campaign_id);
```

**Additional Indexes**:

```sql
CREATE INDEX idx_campaigns_campaign_name ON campaigns(campaign_name);
CREATE INDEX idx_loans_prospect_id ON loans(prospect_id);
```

## Sample Data Insertion

Here's how you can insert sample data to test the setup.

**Insert Qualification Stages**:

```sql
-- Already provided in the table definitions
```

**Insert Lead Sources**:

```sql
INSERT INTO lead_sources (source_name)
VALUES ('Google Ads'), ('Facebook Ads'), ('Organic Search');
```

**Insert Users (Team Members)**:

```sql
INSERT INTO users (first_name, last_name, email, bonzo_user_id, role)
VALUES
    ('Alice', 'Smith', 'alice@example.com', gen_random_uuid(), 'user'),
    ('Bob', 'Johnson', 'bob@example.com', gen_random_uuid(), 'user');
```

**Insert Prospects**:

```sql
INSERT INTO prospects (first_name, last_name, email, phone, lead_source_id, qualification_stage_id, assigned_to)
VALUES
    ('John', 'Doe', 'john@example.com', '555-1234', 1, 1, 1),
    ('Jane', 'Smith', 'jane@example.com', '555-5678', 2, 1, 2);
```

**Insert Campaigns**:

```sql
INSERT INTO campaigns (campaign_name, description)
VALUES ('Opener Campaign', 'Initial engagement sequence.');
```

**Insert Touches**:

```sql
INSERT INTO touches (campaign_id, touch_order, touch_type, content, scheduled_delay)
VALUES
    ('c1', 1, 'SMS', 'Hi {{first_name}}, this is {{sender_name}}.', 0),
    ('c1', 2, 'Email', 'Subject: Checking In\nHi {{first_name}}...', 1440);
```

**Assign Prospects to Campaign**:

```sql
INSERT INTO prospect_campaign_assignments (prospect_id, campaign_id)
VALUES (1, 'c1'), (2, 'c1');
```

**Log Touch Engagements**:

```sql
-- Prospect 1 responds to first touch
INSERT INTO touch_engagements (prospect_id, touch_id, engagement_type, content, campaign_id)
VALUES (1, 'touch_id_1', 'Responded', 'Thanks for reaching out!', 'c1');
```

## Next Steps

1. **Set Up the Database**:
   - Install PostgreSQL if you haven't already.
   - Run the SQL scripts provided to create the database schema and insert sample data.

2. **Implement Data Ingestion**:
   - Develop scripts or use tools to ingest data from Bonzo's OpenAPI into our database.
   - Ensure that data mappings align with our schema.

3. **Develop BI Models and Dashboards**:
   - Use BI tools like Rill to create data models based on our tables.
   - Write SQL queries to calculate key metrics (e.g., response rates, conversion rates).
   - Build dashboards to visualize insights.

4. **Collaborate on GitHub**:
   - Share this project repository with the team.
   - Use version control to manage changes and collaborate effectively.

5. **Documentation**:
   - Document any scripts or processes you develop.
   - Keep the README updated with instructions and guidelines.

## Conclusion

By following this guide, you now have a comprehensive understanding of our PostgreSQL database schema and how it supports our modern data platform. This setup allows us to:

- **Standardize Data Storage**: Align our data with Bonzo's terminology and structures.
- **Perform Advanced Analytics**: Enable detailed analysis in our BI layer without altering the database schema.
- **Enhance Collaboration**: Share the project on GitHub to work together seamlessly.
- **Drive Business Success**: Provide actionable insights to improve our managed services and client outcomes.

Your next action is to set up the database, start exploring the data, and begin developing the BI models and dashboards. If you have any questions or need assistance, feel free to reach out!

Happy collaborating!

## Additional Resources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [GitHub Guides](https://guides.github.com/)
- [Rill Data Documentation](https://rilldata.com/docs/)
```

This version uses headers, bullet points, and code blocks to improve readability and organization. Let me know if you need further adjustments!