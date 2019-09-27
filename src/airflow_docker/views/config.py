import json

from airflow.plugins_manager import AirflowPlugin
from airflow_docker.utils import get_config
from airflow_docker.views import template_folder
from flask import Blueprint
from flask_admin import BaseView, expose
from pygments import highlight, lexers
from pygments.formatters import HtmlFormatter


class ConfigView(BaseView):
    @expose("/")
    def config(self):
        config = get_config()
        data = json.dumps(config, indent=4, sort_keys=True)
        data = highlight(data, lexers.JsonLexer(), HtmlFormatter(linenos=True))
        return self.render("config.html", data=data)


view = ConfigView(category="Airflow Docker", name="Config")
blueprint = Blueprint("config", __name__, template_folder=template_folder)
