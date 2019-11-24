# -*- coding: utf-8 -*-
#
#     Copyright 2019 Contributing Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import json

from airflow.plugins_manager import AirflowPlugin
from flask import Blueprint
from flask_admin import BaseView, expose
from flask_appbuilder import BaseView as AppBuilderBaseView

from airflow_docker.operator import BaseDockerOperator
from airflow_docker.views import template_folder


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
