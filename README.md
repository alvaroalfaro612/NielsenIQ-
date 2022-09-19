# NielsenIQ test Álvaro Alfaro- Machine Learning & Hexagonal Architecture

The goal of this repo is demonstrate how to apply Hexagonal Architecture in a ML based system 

The model used in this example has been taken from 
[IntelAI](https://github.com/IntelAI/models/blob/master/docs/object_detection/tensorflow_serving/Tutorial.md)

**The deployment is based on the use of docker compose to make it easier and faster.**

## Download the model
Download the model from the following link, extract it and save the file **saved_model.pb** in the folder **deployment\tf-model\1**
https://storage.googleapis.com/intel-optimized-tensorflow/models/v1_8/rfcn_resnet101_fp32_coco_pretrained_model.tar.gz

## Deploy the solution
Use the following command from **\deployment** directory to deploy the solution:

```
docker-compose up
```

## Call the service

```
 curl -F "threshold=0.9" -F "file=@resources/images/boy.jpg" http://0.0.0.0:610/object-count
 curl -F "threshold=0.9" -F "file=@resources/images/cat.jpg" http://0.0.0.0:6010/object-count
 curl -F "threshold=0.9" -F "file=@resources/images/food.jpg" http://0.0.0.0:6010/object-count
```
------------
## Assignment tasks:
### 1. Add a new service endpoint to receive the image and the desired threshold and return the list of predictions.
Endpoint **/detection-list** is added. This endpoint return a list of strings with the class names of every object detected above the threshold. It is waiting for a POST request with the same values than the** /object-count** endpoint (image file and threshold).

```
 curl -F "threshold=0.9" -F "file=@resources/images/boy.jpg" http://0.0.0.0:6010/detection-list
```
### 2. Write a new adapter for ObjectCountRepo to persist data using a relational (MySQL or PostgreSQL) database.1. Add a new service endpoint to receive the image and the desired threshold and return the list of predictions.

Class CountPostgreRepo implementing ObjectCountRepo interface is added. To use the PostgreSQl db you should put the environment variable **ENV=postgre** (line 44)  in the docker-compose.yml file. On the other hand, if you prefer to use MongoDB, change this value to **mongo**.
### 3. Review the rest of the source code and propose some improvements that you would make in the code, the setup instructions, the tests,...
- I miss comments in the code to help understanding.
- The deployment of the solution is a bit complex (especially if you deploy it from Windows as in my case).
- Create a GET endpoint that returns a message to check if the flask API is running correctly.
- Implement Swagger to have a platform that documents the use of the api and allows the execution of tests from it.
- Use Waitress instead of the Flask development server.
- Control possible exceptions, especially those related to request with incorrect parameters. Also provide response with the correct http code (in this example 400 - Bad Request). For problems in the communication with inference servers code 500.
### 4. Implement at least one of the proposed improvements.
I have chosen to improve the deployment process by allowing it to be done in one step through docker-compose. The instructions detailed above are summarised as: downloading the model and putting it in the correct folder and running the docker-compose up file to deploy at the same time: the inference server, the two databases and the Flask API.
### 5. If we want to use multiple models trained internally (not public), what would you change in the setup of the project?
Assuming these models were also generated with Tensorflow to continue using the Tensorflow inference server. 
Each model shall be stored in the directory: **deployment/tf-models/**
Within this directory the structure of each model shall be the same as the existing **rfcn** model: **model_name/version_model/saved_model.pb**
The next step is to create a TF-Serving configuration file with the following structure (this file will be name "models.config" and will be placed also in **deployment/tf-models/** )
```
model_config_list {
  config {
    name: 'rfcn'
    base_path: '/models/rfcn/'
    model_platform: 'tensorflow'
  }
  config {
    name: 'second_model'
    base_path: '/models/second_model/'
    model_platform: 'tensorflow'
  }
}
```
And also the section correspondig to TF-serving service in the docker-compose.yml file should be updated:
```
  tfserving:
    image: 'intel/intel-optimized-tensorflow-serving:2.3.0'
    restart: 'no'
    volumes:
      - './tf-models/:/models/' #updated line
	command:
      - '--model_config_file=/tf-models/models.config' #updated line
    environment:
      - OMP_NUM_THREADS=4
      - TENSORFLOW_INTER_OP_PARALLELISM=2
      - TENSORFLOW_INTRA_OP_PARALLELISM=4
    ports:
      - '8500:8500'
      - '8501:8501'
```
### 6b. Support models for object detection using different deep learning frameworks. If the task seems too big, just lay out the main key points of the proposed solution.

- The first step would be to replace the TF-serving inference server with one that allows the use of different Deep Learning frameworks. In this case, I would prefer to use Nvidia's Triton inference server, which allows the use of models trained with different frameworks (TensorFlow, TensorR, PyTorch, MXNet, Python, ONNX...). Also this inference server has the capabily of sharing the GPU among different requests even using different model, which is specially interesting in this scenario that we are using Object detection models that will run faster in a GPU cluster.
- The second step would be to deploy this server (compatible also with docker/kubernetes) to serve the models, in a similar way as detailed in section 5 on TF-Serving.
- Finally, we will need to create a class similar to TFSObjectDetector which implementents ObjectDetector interface to make the requests to the new Triton Inference server.
