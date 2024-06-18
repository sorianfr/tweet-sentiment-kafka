# tweet_sentiment_analysis_real_time


## Flujo de la aplicación:

Desde el frontend se cargan los ficheros de tweets con esquema (id,link,content,date,retweets,favorites,mentions,hashtags,geo), y con el uso del conector SpoolDirCsvSourceConnector cada tweet se guarda en el topic de Kafka file.content. 

Los tweets de file.content son consumidos con un flujo de decodificación y clasificados con el uso de la librería TextBlob, en positivos, neutros o negativos, en función del valor de polaridad.

A través de un productor, los tweets con la información adicional de sentimiento se suben al topic tweets_with_sentiment, donde sucede lo siguiente:

1. Un conector sink de MongoDB, se encarga de guardar los tweets en la base de datos: tweet_analysis
2. Utilizando la el servicio KSQL Cli y KSQL Server, se crea un stream de datos y y vistas materializada de los datos que se sirve al front end como estadísticas en real time con una comunicación WebSocket gracias a la librería SocketIO y 
Fuente de Datos:

https://www.kaggle.com/datasets/austinreese/trump-tweets?select=trumptweets.csv

## Manual de Operaciones:

Desde la terminal ejecutando el fichero run.sh se levanta toda la aplicación y se ejecutan los queries de stream en KSQL 

Descripción de la operativa de run.sh

1.- Se baja e instala los conectores Spooldir y Kafka Mongo Connect 
2.- Levanta los servicios de zookeeper broker schema-registry connect control-center ksqldb-server ksqldb-cli mongo1 mongo2 mongo3 
3.- Configura MongoDB como un replicaset para poder utilizar el conector de Kafka Connect
4.- Reinicializa Kafka Connect cuando los conectores han sido instalados en el contenedor.
5.- Configura los conectores de Spooldir CSV Source y MongoDB Sink
6.- Inicia el resto de contenedores que se encargar de la aplicación frontend, flask-backend y analyzer
7.- Crea el STREAM y la TABLA de KSQL desde el script ksql-setup.sql
8.- Reinicia la aplicación de flask-backend ya que necesita que las consultas de ksql estén creadas primero.

Podemos acceder al frontend: http://localhost:80 y podemos ir cargando ficheros y viendo debajo la actualización en tiempo real de la query en KSQL.

## Consultas KSQLDB:

El código para la creación de streams y tablas están en el fichero ksql-setup.sql. y la consulta para recibir el stream de los datos está definida en app.py utilizando la API de KSQL Server y SocketIO para hacer push en real time al front end.


## Diagrama de arquitectura de componentes
