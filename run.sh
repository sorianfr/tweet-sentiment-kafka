
#!/bin/bash

mkdir -p ./kafka-connect/plugins/kafka-connect-spooldir
mkdir -p ./kafka-connect/plugins/kafka-connect-mongodb

# Create the main directory
mkdir -p data

# Create the subdirectories
mkdir -p data/uploads
mkdir -p data/finok
mkdir -p data/finerr

# Set the permissions
chmod 777 data/uploads
chmod 777 data/finok
chmod 777 data/finerr



# Set the URL for the SpoolDir connector
# Set the URL for the SpoolDir connector
SPOOLDIR_URL='https://d2p6pa21dvn84.cloudfront.net/api/plugins/jcustenborder/kafka-connect-spooldir/versions/2.0.65/jcustenborder-kafka-connect-spooldir-2.0.65.zip'
echo "Downloading the SpoolDir connector..."
wget "$SPOOLDIR_URL" -O ./kafka-connect/plugins/kafka-connect-spooldir/jcustenborder-kafka-connect-spooldir-2.0.65.zip

# URL del conector de MongoDB
CONNECTOR_URL="https://repo1.maven.org/maven2/org/mongodb/kafka/mongo-kafka-connect/1.13.0/mongo-kafka-connect-1.13.0-confluent.jar"

# Descargar el conector de MongoDB
echo "Descargando el conector de MongoDB..."
wget "$CONNECTOR_URL" -O ./kafka-connect/plugins/kafka-connect-mongodb/mongo-kafka-connect-1.13.0-confluent.jar
 
# Verificar si la descarga fue exitosa
if [ $? -eq 0 ]; then
    echo "Descarga completada correctamente."
else
    echo "Error al descargar el conector de MongoDB."
    exit 1
fi

# Unzip the downloaded connector
unzip ./kafka-connect/plugins/kafka-connect-spooldir/jcustenborder-kafka-connect-spooldir-2.0.65.zip -d ./kafka-connect/plugins/kafka-connect-spooldir/

# Verify the contents of the directories
echo "Verifying the contents of the directories..."
ls -l ./kafka-connect/plugins/kafka-connect-spooldir
ls -l ./kafka-connect/plugins/kafka-connect-mongodb 

echo "Starting some docker services."
docker compose up -d zookeeper broker schema-registry connect control-center ksqldb-server ksqldb-cli mongo1 mongo2 mongo3 




echo -e "\nConfiguring the MongoDB ReplicaSet.\n"
docker compose exec mongo1 /usr/bin/mongo --eval '''if (rs.status()["ok"] == 0) {
    rsconf = {
      _id : "rs0",
      members: [
        { _id : 0, host : "mongo1:27017", priority: 1.0 },
        { _id : 1, host : "mongo2:27017", priority: 0.5 },
        { _id : 2, host : "mongo3:27017", priority: 0.5 }
      ]
    };
    rs.initiate(rsconf);
}

rs.conf();'''


# Wait until Kafka Connect is ready
echo "Waiting for Kafka Connect to be ready..."
while ! curl -s http://localhost:8083/; do
    echo -n '.'; sleep 1
done
echo "Kafka Connect is ready."

docker restart connect

# Wait until Kafka Connect is ready
echo "Waiting for Kafka Connect to be ready..."
while ! curl -s http://localhost:8083/; do
    echo -n '.'; sleep 1
done
echo "Kafka Connect is ready."




sleep 2



sleep 2
echo -e "\nAdding SpoolDir Kafka Source Connector collection:"
curl -d @"connect-file-source.json" -H "Content-Type: application/json" -X POST http://localhost:8083/connectors 

sleep 2
echo -e "\nKafka Connectors: \n"
curl -X GET "http://localhost:8083/connectors/" -w "\n"


sleep 2
echo -e "\nAdding MongoDB Kafka Sink Connector collection:"
curl -d @"connect-mongo-sink.json" -H "Content-Type: application/json" -X POST http://localhost:8083/connectors 




echo "Starting docker remainer services."
docker compose up -d frontend flask-backend analyzer --build 


echo "Running ksqlDB setup script..."
docker exec -i ksqldb-cli ksql http://ksqldb-server:8088 < ./ksql-setup.sql

docker restart flask-backend
