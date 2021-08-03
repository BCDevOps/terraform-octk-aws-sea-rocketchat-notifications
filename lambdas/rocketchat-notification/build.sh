#/bin/bash
pwd
mkdir ../../builds
chmod 777 ../../builds
cat src/index.py  > lambda_function.py
pip3 install --target ./package requests
cp lambda_function.py ./package
cd package
zip -r securityhubfindings-to-rocketchat.zip .
cd ../../..
pwd
chmod -R 777 /Users/prabhu.manchineella/Desktop/ROCKETCHAT-NOTIFICATIONS/terraform-octk-aws-sea-rocketchat-notifications
cd /Users/prabhu.manchineella/Desktop/ROCKETCHAT-NOTIFICATIONS/terraform-octk-aws-sea-rocketchat-notifications/lambdas/rocketchat-notification/package
pwd
cp -f securityhubfindings-to-rocketchat.zip /Users/prabhu.manchineella/Desktop/ROCKETCHAT-NOTIFICATIONS/terraform-octk-aws-sea-rocketchat-notifications/builds/securityhubfindings-to-rocketchat.zip


