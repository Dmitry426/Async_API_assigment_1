import json

import backoff
from elasticsearch import (
    ConnectionError,
    Elasticsearch,
    ElasticsearchException
)
from elasticsearch.helpers import bulk

from etl.logger import logger


class UploadBatch:
    def __init__(self, es_dsl, index_name):
        connection_url = es_dsl.get('connection_url', 'http://localhost:9200')
        self.es = Elasticsearch(connection_url)
        self.current_index = index_name

        self.request_body = None

    def _create_index(self):
        try:
            with open(f'index_schemas/{self.current_index}.json') as json_file:
                self.request_body = json.load(json_file)
        except FileNotFoundError as e:
            logger.exception(e)

    def _push_index(self):
        """Method to keep index automatically updated"""
        if not self.es.indices.exists(index=self.current_index):
            try:
                self._create_index()
                self.es.indices.create(index=self.current_index, body=self.request_body)
            except ElasticsearchException as es1:
                logger.exception(es1)

    def _generate_data(self, data: list):
        for item in data:
            yield {
                "_index": self.current_index,
                "_id": item["id"],
                "_source": item
            }

    @backoff.on_exception(backoff.expo, ConnectionError, max_time=60)
    def es_push_batch(self, data: list):
        self._push_index()
        try:
            bulk(self.es, self._generate_data(data=data))
            self.es.transport.close()
        except ElasticsearchException as es2:
            logger.exception(es2)
