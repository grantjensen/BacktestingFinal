from kafka import KafkaProducer
import requests
import time
import logging
import argparse 
import os
import json

def main(args):
    logging.info('brokers={}'.format(args.brokers))
    logging.info('topic={}'.format(args.topic))
    logging.info('creating kafka producer')    
    producer = KafkaProducer(bootstrap_servers=args.brokers,
                             value_serializer=lambda x: 
                             json.dumps(x).encode('utf-8'))
    old_time=int(time.time())-60
    while(True):
        new_time=int(time.time())
        if(new_time>=old_time+60):#Check for new minute candlestick data every 60 seconds
            data=requests.get('https://finnhub.io/api/v1/stock/candle?symbol=SPY&resolution=1&from='+str(new_time-480)+'&to='+str(new_time)+'&token='+args.token).json()
            old_time=new_time
            if (data['s']=='ok'):
                logging.info(data)#Print data
                producer.send(args.topic, value=data)#Send data to Kafka
            else:
                logging.info("No new data available")
            
            
def get_arg(env, default):
    return os.getenv(env) if os.getenv(env, "") != "" else default
            
def parse_args(parser):
    args = parser.parse_args()
    args.brokers = get_arg('KAFKA_BROKERS', args.brokers)
    args.topic = get_arg('KAFKA_TOPIC', args.topic)
    args.token=get_arg('TOKEN',args.token)
    return args
            
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logging.info('starting kafka-python producer')
    parser = argparse.ArgumentParser(description='parser for topic and broker')
    parser.add_argument(
            '--brokers',
            help='The bootstrap servers, env variable KAFKA_BROKERS',
            default='kafka:9092')
    parser.add_argument(
            '--topic',
            help='Topic to write to, env variable KAFKA_TOPIC',
            default='my_topic')
    parser.add_argument(
            '--token',
            help='20 digit alphanumeric token from Finnhub.io',
            default='')
    cmdline_args = parse_args(parser)
    main(cmdline_args)
    logging.info('exiting')