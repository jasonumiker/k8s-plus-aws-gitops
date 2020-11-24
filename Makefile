
init:
	cd aws-infrastructure; \
	npm install -g aws-cdk; \
	pip3 install --upgrade aws-cdk.core; \
	pip3 install --upgrade -r requirements.txt

list:
	cd aws-infrastructure; \
	cdk list

diff:
	cd aws-infrastructure; \
	cdk diff --all

deploy:
	cd aws-infrastructure; \
	cdk deploy --all --approve

destroy:
	cd aws-infrastructure; \
	cdk destroy --all
	