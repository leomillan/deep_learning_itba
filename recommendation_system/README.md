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

#### Start databases
We use docker-compose for the database services. Inside the `recommendation_system` folder. Run:
```bash
make start-docker
```
