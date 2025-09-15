import uvicorn
from fastapi import FastAPI
import sys
import logging

from chat2db.apps.routers import sql

logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')


app = FastAPI()

app.include_router(sql.router)

if __name__ == "__main__":
    try:
        uvicorn.run(app, host="127.0.0.1", port=9015, log_level="info")

    except Exception as e:
        exit(1)
