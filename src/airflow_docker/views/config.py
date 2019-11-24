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
from pygments import highlight, lexers
from pygments.formatters import HtmlFormatter

from airflow_docker.utils import get_config
from airflow_docker.views import template_folder


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
