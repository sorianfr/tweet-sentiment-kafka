-- Create the stream from the Kafka topic
CREATE STREAM tweets_with_sentiment_stream (
    id BIGINT,
    link STRING,
    content STRING,
    date STRING,
    retweets BIGINT,
    favorites BIGINT,
    mentions STRING,
    hashtags STRING,
    geo STRING,
    sentiment_label STRING,
    sentiment_polarity DOUBLE
) WITH (
    KAFKA_TOPIC='tweets_with_sentiment',
    VALUE_FORMAT='JSON'
);

-- Create the table to aggregate sentiment statistics
CREATE TABLE sentiment_stats AS
SELECT
    sentiment_label,
    COUNT(*) AS count,
    AVG(sentiment_polarity) AS avg_polarity
FROM
    tweets_with_sentiment_stream
GROUP BY
    sentiment_label;

-- Create a table to track total tweet count by sentiment label
CREATE TABLE total_tweet_counts AS
SELECT
    sentiment_label,
    COUNT(*) AS total_count
FROM
    tweets_with_sentiment_stream
GROUP BY
    sentiment_label;

