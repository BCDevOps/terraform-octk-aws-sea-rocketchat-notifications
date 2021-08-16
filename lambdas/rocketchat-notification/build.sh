#/bin/bash
pwd
mkdir ../../builds
chmod 777 ../../builds
cat ../../lambdas/rocketchat-notification/src/index.py  > index.py
pip3 install --target ./package requests
cp index.py ./package
cd package
zip -r securityhubfindings-to-rocketchat.zip .
cd ../../..
pwd
chmod -R 777 /Users/prabhu.manchineella/Desktop/python_deployment/terraform-octk-aws-sea-rocketchat-notifications
cd /Users/prabhu.manchineella/Desktop/python_deployment/terraform-octk-aws-sea-rocketchat-notifications/terraform/aws/package
cp -f securityhubfindings-to-rocketchat.zip /Users/prabhu.manchineella/Desktop/python_deployment/terraform-octk-aws-sea-rocketchat-notifications/builds/securityhubfindings-to-rocketchat.zip


