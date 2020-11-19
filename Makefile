
init:
	cd aws-infrastructure; \
	npm install -g aws-cdk; \
	pip3 install --upgrade aws-cdk.core; \
	pip3 install --upgrade -r requirements.txt

deploy:
	cd aws-infrastructure; \
	cdk deploy
	