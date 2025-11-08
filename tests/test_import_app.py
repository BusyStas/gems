import importlib


def test_import_app_and_flask_instance():
    """Smoke test: importing app module and ensuring the Flask app instance exists.

    This test is intentionally minimal so CI or a local dev environment can
    quickly validate that application imports and the `app` Flask instance
    are present. If the environment is missing packages (Flask/PyYAML), the
    import will fail and CI will report missing dependencies.
    """
    mod = importlib.import_module('app')
    # The Flask application object in this project is exposed as `app` on the
    # top-level module (app.app). Sanity check that it's present.
    assert hasattr(mod, 'app'), "module 'app' does not expose 'app' (Flask instance)"
    flask_app = getattr(mod, 'app')
    # Basic type check (avoid importing Flask types here to keep the test light)
    assert flask_app is not None
