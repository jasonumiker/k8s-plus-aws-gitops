#!/bin/bash
helm repo add external-secrets https://godaddy.github.io/kubernetes-external-secrets/
helm install --wait --timeout 120 --set env.AWS_REGION=$AWS_DEFAULT_REGION --set serviceAccount.name=kubernetes-external-secrets \
--set serviceAccount.create=false --set securityContext.fsGroup=65534 \
external-secrets/kubernetes-external-secrets --generate-name