# Recommendation System Practical Work

This folder contains all the files for the Recommendation System practical work.

It consists in a Flask API to recommend movies base on user preference.

## How To

### Create Virtual Environment
Create the virtual environment using conda.
```bash
conda env create -f conda-environment.yml
```
Activate the environment
```bash
conda activate deeplearning
```

We use poetry to manage the project dependencies.
```bash
poetry install
```

### Set up environment variables
Inside the dev folder create a `.env` file with the passwords for the postgrade and opensearch databases.
```bash
OPENSEARCH_INITIAL_ADMIN_PASSWORD=<you_password>
POSTGRES_INITIAL_ADMIN_PASSWORD=<you_password>
```

### Run the app
First you need to build the app docker image. Inside the `recommendation_system` folder. Run:
```bash
make build
```
There are a list of useful make commands that you can execute:
```bash
make run  # Start the docker containers
make logs  # Log containers messages
make shell  # Access web container shell
make stop  # Stop all containers
```

### Load data
There are a series of scripts to train and load the data in the Databases.

#### Load data into Postgres Database
To load the data into the database you can run:
```bash
make load_sql
```
for the command to work you'll need the copy to the [data](data/) folder the csv files that
are in the [files](../tp_integrador_de_python/files) folder of the `tp_integrador_de_python` project.

#### Generate Embeddings
You'll need to generate the Movie and User embeddings. You can run the train script with:
```bash
make train
```
If you want, you can change the train parameters declare in the [model_config.yaml](model/model_config.yaml) file.
If you change the `latent_factor` parameter, you'll need to also change the `KNN_VECTOR_DIMENSION` constant in the
[models.py](core/services/database/models.py) file.

#### Load embeddings in the Postgres and OpenSearch databases
Finally, you can load the embeddings created in the train step by running:
```bash
make load_embeddings
```

### Try the app
There are 2 available endpoint you can try:

#### Movies recommendations
Endpoint to recommend movies to a user given a user ID
```
curl --location 'http://127.0.0.1:5000/user/<user_id>?n=<number_of_movies_to_recommend>'
```

Sample response
```json
{
    "user_id": 1,
    "name": "Robert Stanley",
    "recommendations": [
        {
            "movie_id": 216,
            "name": "When Harry Met Sally... (1989)",
            "url": "http://us.imdb.com/M/title-exact?When%20Harry%20Met%20Sally...%20(1989)",
            "year": 1989,
            "genres": [
                "Comedy",
                "Romance"
            ]
        },
        {
            "movie_id": 425,
            "name": "Bob Roberts (1992)",
            "url": "http://us.imdb.com/M/title-exact?Bob%20Roberts%20(1992)",
            "year": 1992,
            "genres": [
                "Comedy"
            ]
        }
    ]
}
```


#### Similar movies
Endpoint to get similar movies given a movie ID
```bash
curl --location 'http://127.0.0.1:5000/movie/<movie_id>?neighbors=<number_of_movies_to_retrieve>'
```

Sample response
```json
{
    "movie_id": 4,
    "name": "Get Shorty (1995)",
    "year": 1995,
    "genres": [
        "Action",
        "Comedy",
        "Drama"
    ],
    "recommendations": [
        {
            "movie_id": 1183,
            "name": "Cowboy Way, The (1994)",
            "url": "http://us.imdb.com/M/title-exact?Cowboy%20Way,%20The%20(1994)",
            "score": 0.99516004,
            "year": 1994,
            "genres": [
                "Action",
                "Comedy"
            ]
        },
        {
            "movie_id": 677,
            "name": "Fire on the Mountain (1996)",
            "url": "http://us.imdb.com/M/title-exact?Fire%20on%20the%20Mountain%20(1996)",
            "score": 0.9926865,
            "year": 1997,
            "genres": [
                "Documentary"
            ]
        }
    ]
}
```
