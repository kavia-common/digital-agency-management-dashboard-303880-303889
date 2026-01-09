#!/bin/bash
cd /home/kavia/workspace/code-generation/digital-agency-management-dashboard-303880-303889/project_management_backend
source venv/bin/activate
flake8 .
LINT_EXIT_CODE=$?
if [ $LINT_EXIT_CODE -ne 0 ]; then
  exit 1
fi

