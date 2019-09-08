#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
from hermes_python.hermes import Hermes
from hermes_python.ffi.utils import MqttOptions
from hermes_python.ontology import *
import io
import os

CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"

class SnipsConfigParser(configparser.SafeConfigParser):
    def to_dict(self):
        return {section : {option_name : option for option_name, option in self.items(section)} for section in self.sections()}


def read_configuration_file(configuration_file):
    try:
        with io.open(configuration_file, encoding=CONFIGURATION_ENCODING_FORMAT) as f:
            conf_parser = SnipsConfigParser()
            conf_parser.readfp(f)
            return conf_parser.to_dict()
    except (IOError, configparser.Error) as e:
        return dict()

def subscribe_intent_callback(hermes, intentMessage):
    conf = read_configuration_file(CONFIG_INI)
    action_wrapper(hermes, intentMessage, conf)


def action_wrapper(hermes, intentMessage, conf):
    Ort=str(intentMessage.slots.Ort.first().value)
    Geraet=str(intentMessage.slots.Geraet.first().value)
    if Ort == "Wohnzimmer":
       if Geraet == "Lampe":
            command = "pilight-control -d Switch3 -s on"
            os.system(command)
            result_sentence = "Lampe im Wohnzimmer eingeschaltet"
       elif Geraet == "Fernseher":
            command = "pilight-control -d Switch1 -s on"
            os.system(command)
            result_sentence = "Fernseher im Wohnzimmer eingeschaltet"
       else:
            result_sentence = "Dieses Gerät im Wohnzimmer kenne ich nicht"
    elif Ort == "Schlafzimmer":
       if Geraet == "Lampe":
            result_sentence = "Ich kann keine Lampe im Schlafzimmer schalten"
       elif Geraet == "Fernseher":
            command = "pilight-control -d Sonoff1 -s running"
            os.system(command)
            result_sentence = "Fernseher im Schlafzimmer eingeschaltet"
       else:
           result_sentence = "Dieses Gerät im Schlafzimmer kenne ich nicht"
    elif Ort == "Julies Zimmer":
       if Geraet == "Lampe":
           command = "pilight-control -d Switch2 -s on"
           os.system(command)
           result_sentence = "Lampe bei Julie ausgeschaltet"
       elif Geraet == "Fernseher":
           result_sentence = "Ich kann keinen Fernseher bei Julie schalten"
       else:
           result_sentence = "Dieses Gerät in Julies kenne ich nicht"
    else:
       result_sentence = "Dieses Zimmer kenne ich nicht"
    current_session_id = intentMessage.session_id
    hermes.publish_end_session(current_session_id, result_sentence)


if __name__ == "__main__":
    mqtt_opts = MqttOptions()
    with Hermes(mqtt_options=mqtt_opts) as h:
        h.subscribe_intent("elektra:in_Schalteein", subscribe_intent_callback) \
         .start()
