from pipelineproof.catalog import families, task_catalog


def test_catalog_has_six_distinct_families():
    tasks = task_catalog()
    assert len(tasks) == 6
    assert {task.family for task in tasks} == set(families())
    assert all(task.split == "development" for task in tasks)
