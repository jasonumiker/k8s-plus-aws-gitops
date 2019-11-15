#!/bin/bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes-sigs/aws-alb-ingress-controller/v1.0.0/docs/examples/rbac-role.yaml
curl https://raw.githubusercontent.com/kubernetes-sigs/aws-alb-ingress-controller/v1.0.0/docs/examples/alb-ingress-controller.yaml | sed "s/devCluster/cluster/;s/us-west-1/$AWS_DEFAULT_REGION/" | kubectl apply -f -