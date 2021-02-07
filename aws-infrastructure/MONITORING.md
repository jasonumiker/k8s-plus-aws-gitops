# Monitoring tooling that has been set up for you

## How to use the provided Prometheus/Grafana

The AWSInfrastructureStack provisions the [kube-prometheus-stack](https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack) Helm chart to the cluster for you.

To connect to the Grafana dashboard:
1. Run `kubectl get services --namespace=monitoring` to find the name of your grafana service.
1. Run `kubectl port-forward svc/awsinfrastructurestackclusterchartmonitoringXXXXXXXX-grafana 3000:80 --namespace=monitoring` Replacing the service name with your service name (the 8 X's unique to it).
1. Open http://localhost:3000 and use the default login/password of admin/prom-operator
1. If you go to http://localhost:3000/dashboards you'll see this Grafana has been pre-loaded with various dashboards to get you started.

To connect to the Prometheus dashhboard:
1. Run `kubectl port-forward svc/prometheus-operated 9090 --namespace=monitoring`
1. Open http://localhost:9090

To connect to the alertmanager dashboard:
1. Run `kubectl port-forward svc/alertmanager-operated 9093 --namespace=monitoring`
1. Open http://localhost:9093

TODO: Replace this with the new AWS Managed Prometheus/Grafana when GA

## How to use the provided ElasticSearch for container logs

Fluent-bit is configured as a DaemonSet to scrape all the host and container logs and ship them to a new Elasticsearch Domain/Cluster that has been provisioned as part of the AWSInfrastructureStack.

For the purposes of this test/demo environment I both used an Internet-facing Elastic just limit access to my IP address (https://docs.aws.amazon.com/elasticsearch-service/latest/developerguide/es-kibana.html#es-kibana-access) but in a production environment you'd likely want to implement SAML or Cognito.