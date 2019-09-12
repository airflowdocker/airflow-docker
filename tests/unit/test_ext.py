import contextlib
import textwrap
from unittest.mock import Mock, patch

from airflow.configuration import AirflowConfigParser
from airflow_docker.ext import (
    delegate_to_extensions,
    environment_preset,
    load_extensions,
    register_extensions,
)

import pytest


class FakeExtension:
    pass


class Test_delegate_to_extensions:
    def setup(self):
        class Ext:
            post_bar = Mock()

        class Foo:
            _extensions = [Ext]

            def bar(self):
                delegate_to_extensions(self, "post_bar")

            def baz(self):
                delegate_to_extensions(self, "post_baz")

        self.Ext = Ext
        self.Foo = Foo

    def test_delegate(self):
        register_extensions(self.Foo)

        self.Foo().bar()
        assert self.Ext.post_bar.called_once()

    def test_delegate_method_extension_doesnt_have(self):
        register_extensions(self.Foo)
        self.Foo().baz()


@contextlib.contextmanager
def patch_config(config):
    parser = AirflowConfigParser()
    parser.read_string(textwrap.dedent(config))

    with patch("airflow_docker.conf.conf.get", new=parser.get):
        yield


class Test_load_extensions:
    def setup(self):
        load_extensions.cache_clear()

    def test_empty_config(self):
        with patch_config(""):
            result = load_extensions()
        assert result == []

    def test_has_section_no_paths(self):
        with patch_config("[extensions]"):
            result = load_extensions()
        assert result == []

    def test_has_section_empty_paths(self):
        with patch_config(
            """
            [airflowdocker]
            extension_paths =
            """
        ):
            result = load_extensions()
        assert result == []

    def test_has_section_with_path_no_extension(self):
        with patch_config(
            """
            [airflowdocker]
            extension_paths = airflow_docker.ext.environment_preset
            """
        ):
            with pytest.raises(ValueError) as e:
                load_extensions()

        assert "module.submodule:Extension" in str(e.value)

    def test_has_section_with_path_with_extension(self):
        with patch_config(
            """
            [airflowdocker]
            extension_paths = airflow_docker.ext.environment_preset:EnvironmentPresetExtension
            """
        ):
            result = load_extensions()
        assert result == [environment_preset.EnvironmentPresetExtension]

    def test_has_section_with_path_with_two_extensions(self):
        with patch_config(
            """
            [airflowdocker]
            extension_paths =
              airflow_docker.ext.environment_preset:EnvironmentPresetExtension
              tests.unit.test_ext:FakeExtension
            """
        ):
            result = load_extensions()
        assert result == [environment_preset.EnvironmentPresetExtension, FakeExtension]


class Test_register_extensions:
    def test_only_loads_once(self):
        class Foo:
            pass

        class Bar:
            pass

        with patch("airflow_docker.ext.load_extensions", Mock()) as m:
            register_extensions(Foo)
            register_extensions(Bar)

        assert m.called_once()

    def test_sets_attribute_only_once(self):
        class Foo:
            pass

        with patch("airflow_docker.ext.load_extensions", Mock()) as m:
            register_extensions(Foo)
            register_extensions(Foo)

        assert m.called_once()
