# Getting started

## 1. Easy installation with no external services (can run entirely offline)

### 1.1 Install the dependencies

- Install docker [https://docs.docker.com/get-docker/]
- Install Ollama [https://ollama.com/]
- Download at least 1 model from Ollama (phi3 or llama3.1 are good starting points)

### 1.1/2 Run this script in root directory

```bash
mv docker-compose.yaml.template_basic docker-compose.yaml
mv env_openweb.template .env_openweb
mkdir -p volume_data volume_images volume_pipelines
docker-compose -f docker-compose.yaml up
```

OR do it step by step:

### 1.2 Create docker-compose and env files

1. Remove the '.template' from the docker-compose.yaml.template_basic file
2. Remove the '.template' from the env_openweb.template file

```bash
mv docker-compose.yaml.template_basic docker-compose.yaml
mv env_openweb.template .env_openweb
```

3. Create the volumes folders

```bash
mkdir volume_data volume_images volume_pipelines
```

4. Run the docker compose up command to startup the server

```bash
docker-compose -f docker-compose.yaml up
```

4. Open the browser and navigate to `http://localhost:3000` to see the OpenWeb UI, select the model you want to use and start chatting!

## 2. Installation with external services

### 2.1 Install the dependencies

- Install docker [https://docs.docker.com/get-docker/]
- Install Ollama [https://ollama.com/] (optional)
- AWS account if you want to use bedrock models (optional)
- Perplexity API key if you want to use perplexity models (optional)
- OpenAI API key if you want to use OpenAI models (optional)
- Any other API key you want to use (optional)

### 2.2 Run this script in root directory

```bash
mv docker-compose.yaml.template docker-compose.yaml
mv env_openweb.template .env_openweb
mv env_pipelines.template .env_pipelines
mkdir -p volume_data volume_images volume_pipelines
```

### 2.3 Fill in the .env_pipelines file with the API keys

Open the .env_pipelines file and fill in the API keys for the models you want to use. If you don't have the API keys, you can leave the fields empty.

### 2.4 Run the docker compose up command to startup the server

```bash
docker-compose -f docker-compose.yaml up
```

### 3. Updating the OpenWebUI

To get the latest updates to the OpenWebUI, you can pull the latest changes from the repository and rebuild the docker image.

```bash
docker pull ghcr.io/open-webui/open-webui:main
docker pull ghcr.io/open-webui/pipelines:main
docker-compose -f docker-compose.yaml up
```
