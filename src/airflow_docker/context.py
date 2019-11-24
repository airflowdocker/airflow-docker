def serialize_context(context):
    return {
        "dag": serialize_dag(context["dag"]),
        "ds": context["ds"],
        "next_ds": context["next_ds"],
        "next_ds_nodash": context["next_ds_nodash"],
        "prev_ds": context["prev_ds"],
        "prev_ds_nodash": context["prev_ds_nodash"],
        "ds_nodash": context["ds_nodash"],
        "ts": context["ts"],
        "ts_nodash": context["ts_nodash"],
        "ts_nodash_with_tz": context["ts_nodash_with_tz"],
        "yesterday_ds": context["yesterday_ds"],
        "yesterday_ds_nodash": context["yesterday_ds_nodash"],
        "tomorrow_ds": context["tomorrow_ds"],
        "tomorrow_ds_nodash": context["tomorrow_ds_nodash"],
        "END_DATE": context["END_DATE"],
        "end_date": context["end_date"],
        "dag_run": serialize_dag_run(context["dag_run"]),
        "run_id": context["run_id"],
        "execution_date": context["execution_date"].isoformat(),
        "prev_execution_date": context["prev_execution_date"].isoformat(),
        "next_execution_date": context["next_execution_date"].isoformat(),
        "latest_date": context["latest_date"],
        "params": context["params"],
        "task": serialize_task(context["task"]),
        "task_instance": serialize_task_instance(context["task_instance"]),
        "ti": serialize_task_instance(context["ti"]),
        "task_instance_key_str": context["task_instance_key_str"],
        "test_mode": context["test_mode"],
    }


def serialize_dag(dag):
    return {}


def serialize_dag_run(dag_run):
    return {}


def serialize_task(task):
    return {}


def serialize_task_instance(task_instance):
    return {}
