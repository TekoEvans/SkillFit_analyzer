import os
from email_collector.paths import create_output_paths, normalize_job_title

def test_create_output_paths(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    cv_folder, json_file = create_output_paths("Statisticien Senior")

    assert os.path.isdir(cv_folder)
    assert os.path.isfile(json_file) or not os.path.exists(json_file)
    assert "statisticien_senior" in cv_folder
    assert "statisticien_senior" in json_file
