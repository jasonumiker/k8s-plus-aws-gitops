#!/bin/bash
helm repo add external-secrets https://godaddy.github.io/kubernetes-external-secrets/
helm install --set env.AWS_REGION=$AWS_DEFAULT_REGION external-secrets/kubernetes-external-secrets