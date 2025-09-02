.PHONY: dev up worker ui api
dev:  ## run all dev services
\tuvicorn apps.api_fastapi.main:app --reload &
\tflask --app apps/ui_flask/app.py run --debug &
\tcelery -A core.queue.celery_app worker -l INFO

ui:
\tflask --app apps/ui_flask/app.py run --debug

api:
\tuvicorn apps.api_fastapi.main:app --reload

worker:
\tcelery -A core.queue.celery_app worker -l INFO
