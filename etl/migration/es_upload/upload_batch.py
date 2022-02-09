import json
from pathlib import Path
from typing import Iterable

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
        es_host = es_dsl.get('host', 'localhost')
        es_port = es_dsl.get('port', '9200')
        connection_url = f'http://{es_host}:{es_port}'

        self.es = Elasticsearch(connection_url)
        self.current_index = index_name

        self.request_body = None

    def _create_index(self):
        current_path = Path('./migration/es_upload').absolute()
        try:
            with open(current_path / f'index_schemas/{self.current_index}.json') as json_file:
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

    def _generate_data(self, data: Iterable):
        for item in data:
            yield {
                "_index": self.current_index,
                "_id": item["id"],
                "_source": item
            }

    @backoff.on_exception(backoff.expo, ConnectionError, max_time=60)
    def es_push_batch(self, data: Iterable):
        self._push_index()
        try:
            bulk(self.es, self._generate_data(data=data))
            self.es.transport.close()
        except ElasticsearchException as es2:
            logger.exception(es2)
