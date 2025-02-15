"""Configuration loading and validation using Pydantic for YAML and TOML files."""

from pathlib import Path

import toml
import yaml
from pydantic import BaseModel, ValidationError


# ✅ Pydantic Models for YAML Validation
class RequiredPhrasesModel(BaseModel):
    """Represents the required phrases model."""

    greetings: list[str]
    disclaimers: list[str]


class YAMLConfigModel(BaseModel):
    """Represents the YAML model."""

    required_phrases: RequiredPhrasesModel
    prohibited_phrases: list[str]


# ✅ Pydantic Model for TOML Validation
class LoggingConfigModel(BaseModel):
    """Represents the LOGGING CONFIG model."""

    log_file_name: str
    log_rotation: str
    log_compression: str
    min_log_level: str
    logging_server_port_no: int


class ServerConfigModel(BaseModel):
    """Represents the SERVER CONFIG model."""

    port_no: int
    number_of_workers: int
    timeout_keep_alive: int


class TOMLConfigModel(BaseModel):
    """Represents the TOML CONFIG model."""

    logging: LoggingConfigModel
    server: ServerConfigModel


def load_yaml_config(yaml_path: str = "config/config.yaml") -> YAMLConfigModel:
    """Load and validate YAML configuration."""
    with Path(yaml_path).open(encoding="utf-8") as yaml_file:
        yaml_data = yaml.safe_load(yaml_file)

    try:
        return YAMLConfigModel(**yaml_data)


    except ValidationError as e:
        error_msg = f"Invalid YAML format:\n{e}"
        raise ValueError(error_msg) from e


def load_toml_config(toml_path: str = "config/config.toml") -> TOMLConfigModel:
    """Load and validate TOML configuration.

    Args:
        toml_path (str): Path to the TOML file.

    Returns:
        TOMLConfigModel: Validated configuration.

    Raises:
        ValueError: If TOML data is invalid.

    """
    with Path(toml_path).open(encoding="utf-8") as toml_file:
        toml_data = toml.load(toml_file)

    try:
        return TOMLConfigModel(**toml_data)
    except ValidationError as e:
        error_msg = f"Invalid TOML format:\n{e}"
        raise ValueError(error_msg) from e
