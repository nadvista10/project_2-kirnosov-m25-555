install:
	poetry install

project:
	poetry run project

build:
	poetry build

publish:
	poetry publish --dry-run

package-install:
	python3 -m pip install dist/*.whl

package-install-windows:
	python3 -m pip install dist/project_2_kirnosov_m25_555-0.1.0-py3-none-any.whl
	
lint:
	poetry run ruff check .