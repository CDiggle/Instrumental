# -*- coding: utf-8  -*-
"""
Driver for iTech
"""

from . import PowerSupply
from .. import VisaMixin, Facet, SCPI_Facet
from ... import u, Q_
from .. import ParamSet
from enum import Enum
from visa import ResourceManager
import pyvisa
import re

class OnOffState(Enum):
    ON = True
    OFF = False

class IT6000C(PowerSupply, VisaMixin):
    _INST_PARAMS_ = ['visa_address']
    _INST_VISA_INFO_ = ('ITech', ['IT6015C-80-450'])
    voltage = SCPI_Facet('SOURce:VOLTage:LEVel:IMMediate:AMPLitude', convert=float, units='V')
    current = SCPI_Facet('SOURce:CURRent:LEVel:IMMediate:AMPLitude', convert=float, units='A')
    local_voltage = SCPI_Facet('MEASure:SCALar:LOCAL:VOLTage?', convert=float, units='V')
    remote_voltage = SCPI_Facet('MEASure:SCALar:REMOte:VOLTage?', convert=float, units='V')
    current_protection = SCPI_Facet('SOURce:CURRent:PROTection', convert=float, units='A')
    current_protection_state = SCPI_Facet('SOURce:CURRent:PROTection:STATe', convert=OnOffState)
    output = SCPI_Facet('OUTPut:STATe', convert=OnOffState)
    beeper = SCPI_Facet('SYSTem:BEEPer', convert=OnOffState)
    def _initialize(self):
        self._rsrc.write_termination = '\n'
        self._rsrc.read_termination = '\n'

    @property
    def manufacturer(self):
        manufacturer, _, _, _ = self.query('*IDN?').rstrip().split(',', 4)
        return manufacturer

    @property
    def model(self):
        _, model, _, _ = self.query('*IDN?').rstrip().split(',', 4)
        return model

    @property
    def serial(self):
        _, _, serial, _ = self.query('*IDN?').rstrip().split(',', 4)
        return serial

    @property
    def version(self):
        _, _, _, version = self.query('*IDN?').rstrip().split(',', 4)
        return version

    # MEASure:VOLTage? + SENSe:VOLTage:RESet if reset=True
    def get_Ah(self, reset=False):
        """
        Get the number of Ampere-hours passed through the power supply.
        """
        amp_hours = self.query('MEASure:AHOur?')
        if reset:
            self.write('SENSe:AHOur:RESet')
        return Q_(amp_hours, u.Ah)
    
    # MEASure:WHOur? + SENSe:WHOur:RESet if reset=True
    def get_Wh(self, reset=False):
        """
        Get the number of Watt-hours passed through the power supply.
        """
        watt_hours = self.query('MEASure:WHOur?')
        if reset:
            self.write('SENSe:WHOur:RESet')
        return Q_(watt_hours, u.Wh)
    
    # [SOURce:]REMote:SENSe[:STATe]<Bool>
    def remote_sense(self, state=None):
        """
        Get or set the remote sense state.
        """
        if state is None:
            return self.query('SOURce:REMote:SENSe:STATe?')
        else:
            self.write('SOURce:REMote:SENSe:STATe {}'.format(int(state)))