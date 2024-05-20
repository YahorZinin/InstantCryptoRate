start-dependencies:
	docker-compose -f docker-compose.dependencies.yml up -d


start-web-server:
	export PYTHONPATH=$PWD
	python src/api/app.py