The purpose of this repository is to give a use case of how OpenShift can ease the process of creation of a ML application in the finance world. The general pipeline is as follows:

dataRetrieval->dataWrangling->MLFLow->(Estimator & Acqusition). 

The Estimator and Acquisition directories are placed on OpenShift, and are not run locally. The remaining two files are CleanedSpy.csv which is an example output of dataWrangling, and is used as the input for MLFLow, which outputs a model: myModel.cpickle.
After running through MLFLow, one should obtain a .cpickle model file similar to the one in this directory. Place this model somewhere so that it has a url attatched to it. We now begin the OpenShift process.

1. Login to OpenShift, create a new project with a unique name.

2. Start the Kafka service. One way to accomplish this is with the following command line inputs: 

```
oc create -f https://raw.githubusercontent.com/EldritchJS/adversarial_pipeline/master/openshift_templates/strimzi-0.1.0.yaml  
```
```
oc new-app strimzi
```

3. Wait for the pods to spin up (can check progress on OpenShift UI).

4. Start Acquisition service with the following CLI. Make sure to replace *MY TOKEN HERE* with your token from a Finnhub.io account.

```
oc new-app centos/python-36-centos7~https://github.com/grantjensen/BacktestingFinal \
--context-dir=Acquisition \
-e KAFKA_BROKERS=kafka:9092 \
-e KAFKA_TOPIC=my_topic \
-e TOKEN=*MY TOKEN HERE* \
--name acquisition 
```

5. Start Estimator service with the following CLI:

```
oc new-app centos/python-36-centos7~https://github.com/grantjensen/BacktestingFinal \
--context-dir=Estimator \
-e KAFKA_BROKERS=kafka:9092 \
-e KAFKA_READ_TOPIC=my_topic \  
-e MODEL_URL=https://raw.githubusercontent.com/grantjensen/BacktestingFinal/master/myModel.cpickle \
--name estimator
```

6. Add a persistent volume to keep track of past predictions and make decisions on whether the model is performing well. This is accomplished by going to the OpenShift UI, go to the estimator application, and select "Add Storage". For the mount point choose "/data", as that's what is specified in Estimator/app.py. 
