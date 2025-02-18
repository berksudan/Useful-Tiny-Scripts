 # Make sure you have installed mypy and ruff
git add .
for file in $(git diff --name-only --cached -- '*.py'); do
    echo "$file"
    ruff check --fix "$file"
    ruff check --config pyproject.toml
    ruff format "$file"
    echo "Mypy running.." && mypy "$file" && echo "Mypy finished.."
done
git add .
