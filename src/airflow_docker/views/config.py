import json

from airflow.plugins_manager import AirflowPlugin
from airflow_docker.utils import get_config
from airflow_docker.views import template_folder
from flask import Blueprint
from flask_admin import BaseView, expose
from flask_appbuilder import BaseView as AppBuilderBaseView
from pygments import highlight, lexers
from pygments.formatters import HtmlFormatter


def render_config(self):
    config = get_config()
    data = json.dumps(config, indent=4, sort_keys=True)
    return highlight(data, lexers.JsonLexer(), HtmlFormatter(linenos=True))


class ConfigView(BaseView):
    @expose("/")
    def config(self):
        rendered_config = render_config(self)
        return self.render("config.html", data=rendered_config)


class AppBuilderConfigView(AppBuilderBaseView):
    template_folder = template_folder

    @expose("/")
    def list(self):
        rendered_config = render_config(self)
        return self.render_template(
            "config.html", data=rendered_config, appbuilder=True
        )


view = ConfigView(category="Airflow Docker", name="Config")
blueprint = Blueprint("config", __name__, template_folder=template_folder)

appbuilder_view = AppBuilderConfigView()
appbuilder_package = {
    "name": "Config",
    "category": "Airflow Docker",
    "view": appbuilder_view,
}
