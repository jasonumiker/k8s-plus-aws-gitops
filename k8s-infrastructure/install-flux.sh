#!/bin/bash
kubectl create ns flux
export GHUSER="jasonumiker"
fluxctl install \
--git-user=${GHUSER} \
--git-email=${GHUSER}@users.noreply.github.com \
--git-url=git@github.com:${GHUSER}/k8s-plus-aws-gitops \
--git-path=k8s-app-resources \
--git-readonly=true \
--namespace=default | kubectl apply -f -