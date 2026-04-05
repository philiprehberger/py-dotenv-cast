import os
import tempfile

import pytest
from philiprehberger_dotenv_cast import Env, MissingEnvError, env, load_dotenv


@pytest.fixture(autouse=True)
def _clean_env():
    """Remove test keys from os.environ after each test."""
    yield
    for key in list(os.environ):
        if key.startswith("TEST_DC_"):
            del os.environ[key]


def test_str_returns_value():
    os.environ["TEST_DC_HOST"] = "localhost"
    assert env.str("TEST_DC_HOST") == "localhost"


def test_int_casting():
    os.environ["TEST_DC_PORT"] = "8080"
    assert env.int("TEST_DC_PORT") == 8080


def test_float_casting():
    os.environ["TEST_DC_RATE"] = "3.14"
    assert env.float("TEST_DC_RATE") == pytest.approx(3.14)


def test_bool_true_variants():
    for value in ("true", "True", "TRUE", "1", "yes", "Yes", "on", "ON"):
        os.environ["TEST_DC_FLAG"] = value
        assert env.bool("TEST_DC_FLAG") is True, f"Expected True for {value!r}"


def test_bool_false_variants():
    for value in ("false", "False", "FALSE", "0", "no", "No", "off", "OFF"):
        os.environ["TEST_DC_FLAG"] = value
        assert env.bool("TEST_DC_FLAG") is False, f"Expected False for {value!r}"


def test_bool_invalid_raises():
    os.environ["TEST_DC_FLAG"] = "maybe"
    with pytest.raises(ValueError, match="Cannot cast"):
        env.bool("TEST_DC_FLAG")


def test_missing_raises_error():
    with pytest.raises(MissingEnvError):
        env.str("TEST_DC_NONEXISTENT")


def test_missing_int_raises_error():
    with pytest.raises(MissingEnvError):
        env.int("TEST_DC_NONEXISTENT")


def test_default_str():
    assert env.str("TEST_DC_MISSING", "fallback") == "fallback"


def test_default_int():
    assert env.int("TEST_DC_MISSING", 42) == 42


def test_default_bool():
    assert env.bool("TEST_DC_MISSING", True) is True


def test_default_list():
    assert env.list("TEST_DC_MISSING", default=["a", "b"]) == ["a", "b"]


def test_list_splitting():
    os.environ["TEST_DC_TAGS"] = "a, b, c"
    assert env.list("TEST_DC_TAGS") == ["a", "b", "c"]


def test_list_custom_separator():
    os.environ["TEST_DC_ITEMS"] = "x|y|z"
    assert env.list("TEST_DC_ITEMS", separator="|") == ["x", "y", "z"]


def test_json_parsing():
    os.environ["TEST_DC_DATA"] = '{"key": "value"}'
    result = env.json("TEST_DC_DATA")
    assert result == {"key": "value"}


def test_json_default():
    assert env.json("TEST_DC_MISSING", default=None) is None


def test_load_dotenv():
    f = tempfile.NamedTemporaryFile(
        mode="w", suffix=".env", delete=False, prefix="test_dc_"
    )
    f.write("TEST_DC_LOADED=hello\nTEST_DC_NUM=42\n")
    f.close()
    try:
        result = load_dotenv(f.name)
        assert result == {"TEST_DC_LOADED": "hello", "TEST_DC_NUM": "42"}
        assert os.environ["TEST_DC_LOADED"] == "hello"
    finally:
        os.unlink(f.name)


def test_load_dotenv_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_dotenv("/nonexistent/.env")


def test_env_instance_is_env_class():
    assert isinstance(env, Env)


def test_url_returns_valid_url():
    os.environ["API_URL"] = "https://example.com/api"
    assert env.url("API_URL") == "https://example.com/api"


def test_url_rejects_invalid_url():
    os.environ["BAD_URL"] = "ftp://example.com"
    with pytest.raises(ValueError, match="Invalid URL"):
        env.url("BAD_URL")


def test_url_missing_raises():
    with pytest.raises(MissingEnvError):
        env.url("MISSING_URL")


def test_path_returns_path_object():
    from pathlib import Path

    os.environ["DATA_DIR"] = "/tmp/data"
    result = env.path("DATA_DIR")
    assert isinstance(result, Path)
    assert str(result) == "/tmp/data"


def test_path_missing_raises():
    with pytest.raises(MissingEnvError):
        env.path("MISSING_PATH")
