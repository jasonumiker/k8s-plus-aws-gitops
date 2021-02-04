# Deploying Ghost onto the cluster

## Deployment steps

1. Run `update-ghost-external-secret.sh` to populate ghost-externalsecret.yaml with the details on the secret in SecretsManager that CDK created for the MySQL RDS
1. Edit `ghost-ingress.yaml` and:
    1. Put in the ARN of your certificate for either *.[yourdomainname] or ghost.[yourdomainname]
    1. Update `external-dns.alpha.kubernetes.io/hostname` to your fully qualified domain name (FQDN)
1. Run `git add *`
1. Run `git commit` and put in an appropriate commit message and save
1. Run `git push` to send the changes upstream
1. (Optional) force flux to do an immediate sync (by default flux checks every 5 minutes) with our newly merged changes by running `fluxctl sync --k8s-fwd-ns kube-system`

This will trigger flux to commit the changed ghost-externalsecret.yaml and ghost-ingress.yaml and then the Ghost service should come up.

Once the service is running you can go to the FQDN/ghost (e.g. ghost.jasonumiker.com/ghost) and then create the initial admin user that can edit the site (before a random person on the Internet does!)