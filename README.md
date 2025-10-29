# Chest Volume Optimizer

Recommends optimal weekly set volume for chest training.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```python
from src.volume_calculator import recommend_volume

result = recommend_volume(
    current_sets=12,
    progress="yes",
    experience="intermediate",
    recovery="yes"
)
print(result)  # Output: "No change needed"
```

## Testing

```bash
pytest tests/
```
