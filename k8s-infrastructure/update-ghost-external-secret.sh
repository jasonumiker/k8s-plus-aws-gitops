cp ghost-externalsecret.yaml.orig ghost-externalsecret.yaml
EXTERNAL_SECRET_NAME=$(aws secretsmanager list-secrets | jq -r '.SecretList[] | . as $parent | .Tags[] | select(.Value == "GhostDBStack") | $parent.Name')
sed -i "s/EXTERNAL_SECRET_NAME/$EXTERNAL_SECRET_NAME/g" ghost-externalsecret.yaml