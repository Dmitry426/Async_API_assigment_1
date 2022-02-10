## FastAPI project async .

- As for now project can run from the container,

## Minimum Requirements
This project supports Ubuntu Linux 18.04  It is not tested or supported for the Windows OS.

- [Docker 20.10 +](https://docs.docker.com/)
- [docker-compose  1.29.2 + ](https://docs.docker.com/compose/)

 # You can start Fast api server by runing . 

```bash
$ docker-compose up -d  --bulid 
```

# Notes 
- Python:slim image in docker  course uvicorn using specific dependencies
- In order to run Alpine version all orjson dependencies must be in requirements.txt 
- Uvicorn is run from main.py in order to use custom logger  .
