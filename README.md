## FastAPI project async .

- As for now project can't be run from the container,

## Minimum Requirements
This project supports Ubuntu Linux 18.04  It is not tested or supported for the Windows OS.

- [Docker 20.10 +](https://docs.docker.com/)
- [docker-compose  1.29.2 + ](https://docs.docker.com/compose/)

 # You can start Fast api server by runing . 

```bash
$ docker-compose up -d  --bulid 
```

# Notes 
- Python:slim imagein docker  course uvicorn using specific dependencies
- In order to run Alpine version all orjson dependecies must be in reqirements.txt 
- Uvicorn is run from main.py in order to use custom logger  .
