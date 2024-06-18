from kafka import KafkaConsumer, KafkaProducer
import json
import avro.schema
import avro.io
from textblob import TextBlob
import logging
from io import BytesIO

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the expected Avro schema
avro_schema = {
    "connect.name": "tweets.input.value.schema",
    "fields": [
        {"name": "id", "type": "long"},
        {"default": None, "name": "link", "type": ["null", "string"]},
        {"name": "content", "type": "string"},
        {"default": None, "name": "date", "type": ["null", "string"]},
        {"default": None, "name": "retweets", "type": ["null", "long"]},
        {"default": None, "name": "favorites", "type": ["null", "long"]},
        {"default": None, "name": "mentions", "type": ["null", "string"]},
        {"default": None, "name": "hashtags", "type": ["null", "string"]},
        {"default": None, "name": "geo", "type": ["null", "string"]}
    ],
    "name": "schema",
    "namespace": "tweets.input.value",
    "type": "record"
}

# Parse schema
schema = avro.schema.parse(json.dumps(avro_schema))

log = logging.getLogger(__name__)

# Function to decode Avro message
def decode_avro_message(message_value, schema):
    bytes_reader = BytesIO(message_value)
    decoder = avro.io.BinaryDecoder(bytes_reader)
    reader = avro.io.DatumReader(schema)
    return reader.read(decoder)

# Function for successful production callback
def on_send_success(record_metadata):
    log.info(f"Message sent to topic {record_metadata.topic}, partition {record_metadata.partition}, offset {record_metadata.offset}")

# Function for error production callback
def on_send_error(ex):
    log.error('Failed to send message', exc_info=ex)

# Initialize Kafka consumer
consumer = KafkaConsumer(
    'file.content',
    bootstrap_servers=['broker:29092'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='tweet-sentiment-group'
)

# Initialize Kafka producer
producer = KafkaProducer(
    bootstrap_servers=['broker:29092'],
    value_serializer=lambda m: json.dumps(m).encode('utf-8')
)

# Function to analyze sentiment
def analyze_sentiment(tweet):
    analysis = TextBlob(tweet)
    polarity = analysis.sentiment.polarity
    if polarity > 0:
        label = 'positive'
    elif polarity == 0:
        label = 'neutral'
    else:
        label = 'negative'
    return {'label': label, 'polarity': polarity}

log.info("Consumer started...")

# Process messages from Kafka
try:
    for message in consumer:
        try:
            # Decode the message and construct the dictionary, removing the first 5 bytes (magic byte + schema ID)
            message_dict = decode_avro_message(message.value[5:], schema)

            # Analyze sentiment of the tweet content
            sentiment = analyze_sentiment(message_dict.get('content'))

            # Add sentiment data to the original dictionary
            message_dict['sentiment_label'] = sentiment['label']
            message_dict['sentiment_polarity'] = sentiment['polarity']

            log.info(f"Event analyzed: {message_dict}")

            # Send the event to the output topic
            producer.send(
                'tweets_with_sentiment',
                key=str(message_dict.get('id')).encode('utf-8'),
                value=message_dict
            ).add_callback(on_send_success).add_errback(on_send_error)
            producer.flush()
            log.info("Event sent.")
        except Exception as e:
            log.error(f"An error occurred while processing message: {e}")
finally:
    consumer.close()
    producer.close()
    log.info("Consumer and Producer closed.")
