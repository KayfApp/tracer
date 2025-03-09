# Tracer/Retriever README

## Overview

The **Tracer/Retriever** is a tool designed to fetch data from various "providers" (data sources), clean and translate the data into English, and then push the processed text into a PostgreSQL database and a message queue. The data pushed into the queue is intended for the **Tracer engine**, which generates embeddings and indices to facilitate efficient searching.

## Features
- **Data Retrieval**: Fetches data from different data providers.
- **Data Cleaning & Translation**: Cleans and translates the data into English.
- **Storage**: Pushes cleaned data into a PostgreSQL database.
- **Queueing**: Sends data into a queue for the Tracer engine to generate embeddings and indices.
- **Efficient Searching**: The Tracer engine uses the embeddings and indices to enable efficient searching without links.

## Prerequisites

- A **PostgreSQL** database with the correct configuration is mandatory for the application to function. If the database is not set up properly, the application will crash.

## Building the Docker Image

Before running the application, you need to build the Docker image. To do so:

1. **Navigate to the project directory** where the `Dockerfile` is located.
2. **Run the following command** to build the Docker image:

```bash
docker build -t retriever .
```

This will create a Docker image with the tag `retriever`.

## Starting the Application

Once the image is built, you can run the Retriever using the following Docker command:

```bash
docker run --add-host=host.docker.internal:host-gateway -p 8080:8080 -e PSQL_URL="host.docker.internal" -e PSQL_PORT="5432" -e PSQL_USERNAME="postgres" -e PSQL_PASSWORD="admin" -e PSQL_DB="tracer" retriever:latest
```

This command runs the **Retriever** Docker container, mapping port `8080` for API access and configuring the PostgreSQL connection parameters.

## API Access

Once the application is running, you can access the FastAPI auto-generated documentation at the following endpoint:

```
http://url:8080/docs
```
