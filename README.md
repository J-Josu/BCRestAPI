# BCRestAPI

This is a simple REST API in [FastAPI](https://fastapi.tiangolo.com/) for consuming Bing Chat with [EdgeGPT](https://github.com/acheong08/EdgeGPT) python library.


## Installation

```bash
git clone https://github.com/J-Josu/BCRestAPI.git
cd BCRestAPI
pip install -r requirements.txt
```

## Usage

Configure the .env file with your Bing Chat credentials

```bash
BING_COOKIES_1=<your cookies>
BING_COOKIES_2=<your cookies>
BING_COOKIES_3=<your cookies>
```

> **Note:** At least 2 cookies are required

Launch the API

```bash
uvicorn src.main:app --reload
```

## Endpoints

### /api/ask

The endpoint to ask a question to Bing Chat

The request method is `POST` and the body must be a JSON with the following format:

```json
{
    "prompt": "Question to ask, must be less than 1800 characters",
    "style": "creative" | "balanced" | "precise"
}
```
