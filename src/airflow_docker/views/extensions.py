import json

from airflow.plugins_manager import AirflowPlugin
from airflow_docker.operator import BaseDockerOperator
from airflow_docker.views import template_folder
from flask import Blueprint
from flask_admin import BaseView, expose
from flask_appbuilder import BaseView as AppBuilderBaseView


def render_extensions(self):
    extensions_classes = BaseDockerOperator._extensions

    extensions = [
        {"name": klass.__name__, "doc": getattr(klass, "__doc__")}
        for klass in extensions_classes
    ]
    return extensions


class ExtensionsView(BaseView):
    @expose("/")
    def config(self):
        rendered_extensions = render_extensions(self)
        return self.render("extensions.html", data=rendered_extensions)


class AppBuilderExtensionsView(AppBuilderBaseView):
    template_folder = template_folder

    @expose("/")
    def list(self):
        rendered_extensions = render_extensions(self)
        return self.render_template(
            "extensions.html", data=rendered_extensions, appbuilder=True
        )


view = ExtensionsView(category="Airflow Docker", name="Extensions")
blueprint = Blueprint("extensions", __name__, template_folder=template_folder)

appbuilder_view = AppBuilderExtensionsView()
appbuilder_package = {
    "name": "Extensions",
    "category": "Airflow Docker",
    "view": appbuilder_view,
}
