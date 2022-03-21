.PHONY: test
test:
	docker-compose -f tests/docker-compose.yml down
	docker-compose -f tests/docker-compose.yml build
	docker-compose -f tests/docker-compose.yml up

.PHONY: test-cleanup
test-cleanup:
	docker-compose -f tests/docker-compose.yml down

