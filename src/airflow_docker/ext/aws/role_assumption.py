import os
import textwrap

import boto3

MAX_ROLE_DURATION_SECONDS = 60 * 60 * 12  # 12 hours in seconds
MAX_ROLE_SESSION_NAME_LENGTH = 64
ROLE_SESSION_NAME_TEMPLATE = "{dag_run_id}__{task_instance_try}__{task_id}"

credential_key_map = {
    "aws_access_key_id": "AccessKeyId",
    "aws_secret_access_key": "SecretAccessKey",
    "aws_session_token": "SessionToken",
}


def generate_role_credentials(
    role_arn, session_name, role_session_duration=MAX_ROLE_DURATION_SECONDS
):
    client = boto3.client("sts")

    response = client.assume_role(
        RoleArn=role_arn,
        RoleSessionName=session_name,
        DurationSeconds=role_session_duration,
    )

    return response


def format_credentials_data(raw_credentials):
    credentials = {
        key: raw_credentials["Credentials"][mapped_key]
        for key, mapped_key in credential_key_map.items()
    }
    return credentials


def aws_credentials_file_format(
    aws_access_key_id, aws_secret_access_key, aws_session_token, profile="default"
):
    credentials = textwrap.dedent(
        f"""\
        [{profile}]
        aws_access_key_id={aws_access_key_id}
        aws_secret_access_key={aws_secret_access_key}
        aws_session_token={aws_session_token}
        """
    )
    return credentials


def generate_role_session_name(context):
    return ROLE_SESSION_NAME_TEMPLATE.format(
        dag_run_id=context["dag_run"].id,
        task_instance_try=context["task_instance"].try_number,
        task_id=context["task_instance"].task_id,
    )[:MAX_ROLE_SESSION_NAME_LENGTH]


def get_credentials(context, role_arn, role_session_duration=MAX_ROLE_DURATION_SECONDS):
    raw_credentials = generate_role_credentials(
        role_arn=role_arn,
        session_name=generate_role_session_name(context),
        role_session_duration=role_session_duration,
    )
    return raw_credentials


def write_credentials(credentials, credentials_path):
    credentials_file_contents = aws_credentials_file_format(**credentials)
    os.makedirs(os.path.dirname(credentials_path), exist_ok=True)
    with open(credentials_path, "wb") as f:
        f.write(credentials_file_contents.encode("utf-8"))


def find_role_session_duration(role_arn):
    iam = boto3.client("iam")
    response = iam.get_role(RoleName=parse_role_name_from_arn(role_arn))
    return response["Role"]["MaxSessionDuration"]


def log_credentials(operator, raw_credentials):
    access_key_id = raw_credentials["Credentials"]["AccessKeyId"]
    expiration = raw_credentials["Credentials"]["Expiration"]
    user_arn = raw_credentials["AssumedRoleUser"]["AssumedRoleId"]

    operator.log.info("Assumed Role:")
    operator.log.info("  Access Key ID = {}".format(access_key_id))
    operator.log.info("  Expiration    = {}".format(expiration.isoformat()))
    operator.log.info("  Arn           = {}".format(user_arn))


def parse_role_name_from_arn(role_arn):
    role_name_start = role_arn.index("role") + 5
    return role_arn[role_name_start:]


class AWSRoleAssumptionExtension:
    """Assume a role for your task.

    Session will have a session name of the following template:

        {dag_run_id}__{task_instance_try}__{task_id}

    Operator Keyword Arguments:
        role_arn: The role arn you want to assume
        role_session_duration: The number of seconds to assume the role for.
            Min: 900, Max: 43200 secs
            Defaults to Max of 43200 seconds (12 hours).
    """

    kwargs = {"role_arn", "role_session_duration"}

    @classmethod
    def post_prepare_environment(
        cls, operator, config, context, host_tmp_dir, session=None
    ):
        if "role_arn" in operator.extra_kwargs:
            role_arn = operator.extra_kwargs["role_arn"]

            if "role_session_duration" in operator.extra_kwargs:
                role_session_duration = int(
                    operator.extra_kwargs["role_session_duration"]
                )
            else:
                try:
                    role_session_duration = find_role_session_duration(role_arn)
                except Exception:
                    operator.log.exception(
                        "Something when wrong with finding the max role session duration."
                    )
                    role_session_duration = MAX_ROLE_DURATION_SECONDS

            operator.log.info("Assuming role: {}".format(role_arn))

            host_credentials_path = os.path.join(host_tmp_dir, ".aws", "credentials")
            container_credentials_path = os.path.join(
                operator.tmp_dir, ".aws", "credentials"
            )

            raw_credentials = get_credentials(
                context=context,
                role_arn=role_arn,
                role_session_duration=role_session_duration,
            )
            log_credentials(operator, raw_credentials)
            credentials = format_credentials_data(raw_credentials)
            write_credentials(
                credentials=credentials, credentials_path=host_credentials_path
            )

            operator.environment[
                "AWS_SHARED_CREDENTIALS_FILE"
            ] = container_credentials_path
        else:
            operator.log.info("Not assuming role")
