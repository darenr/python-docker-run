VERSION ?= latest
IMAGE_NAME ?= autosklearn_automl
CONTAINER_NAME ?= autosklearn_automl

.PHONY: build test clean

build: Dockerfile
	docker build -t $(IMAGE_NAME):$(VERSION)  -f Dockerfile .

test: build
	docker run -it $(IMAGE_NAME):$(VERSION)

clean:
	docker rmi $(IMAGE_NAME):$(VERSION)
