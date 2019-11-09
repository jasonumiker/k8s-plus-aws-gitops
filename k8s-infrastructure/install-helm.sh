#!/bin/bash
kubectl apply -f tiller-serviceaccount.yaml
helm init --service-account tiller