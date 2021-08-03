#!/bin/bash
cd ../../lambdas/rocketchat-notification
sam build --use-container -b ../../builds
zip -r ../../builds/securityhubfindings-to-rocketchat.zip * -x auto.sh
