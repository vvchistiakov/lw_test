#!/usr/bin/sh
set -x

sed -e "s;%BUILD_NUMBER%;${BUILD_NUMBER};g" task_definition.json > "task_definition.${BUILD_NUMBER}.json"

aws ecs register-task-definition --family LWTestTask --cli-input-json "file://task_definition.${BUILD_NUMBER}.json"

TASK=$(aws ecs list-tasks --cluster lwtest --family LWTestTask --desired-status RUNNING --output text --query taskArns[0])
if [[ "${TASK}" != "None" ]]
then
  aws ecs stop-task --cluster lwtest --task "${TASK}"
fi
aws ecs run-task --cli-input-json "file://task_run.json"
