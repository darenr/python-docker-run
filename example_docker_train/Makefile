VERSION ?= latest
IMAGE_NAME ?= iris-model
CONTAINER_NAME ?= iris-model

.PHONY: build test clean

build: Dockerfile
	docker build -t $(IMAGE_NAME):$(VERSION)  -f Dockerfile .

test: build
	docker run -it $(IMAGE_NAME):$(VERSION)

clean:
	docker rmi $(IMAGE_NAME):$(VERSION)
