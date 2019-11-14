#!/bin/bash

curl https://raw.githubusercontent.com/aws-samples/amazon-cloudwatch-container-insights/master/k8s-yaml-templates/quickstart/cwagent-fluentd-quickstart.yaml | sed "s/{{cluster_name}}/cluster/;s/{{region_name}}/$AWS_DEFAULT_REGION/" | kubectl apply -f -