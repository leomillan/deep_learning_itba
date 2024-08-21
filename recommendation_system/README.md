## Recommendation System Practical Work

This folder contains all the files for the Recommendation System practical work.

It consists in a Flask API to recommend movies base on user preference.

### How To

#### Create Virtual Environment
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

#### Set up environment variables
Inside the dev folder create a `.env` file with the passwords for the postgrade and opensearch databases.
```bash
OPENSEARCH_INITIAL_ADMIN_PASSWORD=<you_password>
POSTGRES_INITIAL_ADMIN_PASSWORD=<you_password>
```

#### Run the app
First you need to build the app docker image. Inside the `recommendation_system` folder. Run:
```bash
make build-docker
```
Once the image is build you can run the app with:
```bash
make run
```

You can check the app logs by running:
```bash
make logs
```

#### Try the app
You can add registries to the opensearch database by running the [opensearch_conn](../notebooks/opensearch_conn.ipynb) notebook.

Once the data is loaded try querying for some vector:
```bash
curl --location 'http://127.0.0.1:5000/movie' \
--header 'Content-Type: application/json' \
--data '{"query" : {
    "size": 5,
    "query": {
        "knn": {
            "vector": {
                "vector": [-0.20773935,  0.24350324,  0.25524828,  0.24542136, -0.2526607 ],
                "k" : 20
                }
            }
        }
    }
}'
```
