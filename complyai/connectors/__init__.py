"""Connectors package exposing all regional and international legal source connectors.
"""
from complyai.connectors.base import BaseRegulatoryConnector
from complyai.connectors.india import IndiaConnector
from complyai.connectors.eu import EUConnector
from complyai.connectors.us_federal import USFederalConnector, USStateConnector
from complyai.connectors.international import (
    UKConnector,
    SingaporeConnector,
    AustraliaConnector,
    CanadaConnector,
    UAEConnector,
    ILOConnector,
    OECDConnector,
)

__all__ = [
    "BaseRegulatoryConnector",
    "IndiaConnector",
    "EUConnector",
    "USFederalConnector",
    "USStateConnector",
    "UKConnector",
    "SingaporeConnector",
    "AustraliaConnector",
    "CanadaConnector",
    "UAEConnector",
    "ILOConnector",
    "OECDConnector",
]

