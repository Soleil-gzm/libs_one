import pytest
import json
from pathlib import Path
from deduplicator_assistant import process, find_adjacent_duplicates

@pytest.fixture
def dialogue_data():
    data_path = Path(__file__).parent / "data" / "sample_dialogue.json"
    with open(data_path) as f:
        return json.load(f)

def test_process(dialogue_data):
    processed, stats = process(dialogue_data, threshold=0.85, return_stats=True)
    assert len(processed[0]["messages"]) == 3
    assert stats["removed_pairs"] == 1

def test_analysis(dialogue_data):
    results = find_adjacent_duplicates(dialogue_data, threshold=0.85)
    assert len(results) == 1