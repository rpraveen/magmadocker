"""
Copyright (c) 2016-present, Facebook, Inc.
All rights reserved.

This source code is licensed under the BSD-style license found in the
LICENSE file in the root directory of this source tree. An additional grant
of patent rights can be found in the PATENTS file in the same directory.
"""
import asyncio
import time
import logging
from enum import Enum
from unittest.mock import MagicMock

from magma.common.service import MagmaService
from magma.common.service_registry import ServiceRegistry
from orc8r.protos.common_pb2 import Void
from orc8r.protos.service303_pb2_grpc import Service303Stub
from gpiozero import LED

try:
    red = LED(9)
    yellow = LED(10)
    green = LED(11)
except Exception:
    red = MagicMock()
    yellow = MagicMock()
    green = MagicMock()

def all_off():
    red.off()
    yellow.off()
    green.off()
    return


class State(Enum):
    UNKNOWN = 0
    STARTING = 1
    ALIVE = 2
    STOPPING = 3
    STOPPED = 4


def _show_pattern(pattern):
    for c in pattern:
        if c == 'r':
            red.on()
        elif c == 'y':
            yellow.on()
        elif c == 'g':
            green.on()
        time.sleep(1)
        all_off()


def main():
    """ main() for hello service """
    service = MagmaService('hello')
    logging.getLogger('').setLevel(logging.INFO)

    chan = ServiceRegistry.get_rpc_channel('magmad', ServiceRegistry.LOCAL)
    client = Service303Stub(chan)
    
    _show_pattern('rygryg')

    async def check_magmad_status(interval):
        while True:
            try:
                metrics = client.GetMetrics(Void())
                status = 0.0
                for family in metrics.family:
                    if family.name == "308":
                        status = family.metric[0].gauge.value
                logging.info("LED: checkin status: %s" % status)
                if status == 1.0:
                    all_off()
                    green.blink()
                else:
                    all_off()
                    red.blink()
            except Exception:
                pass
            await asyncio.sleep(interval)

    service.loop.create_task(check_magmad_status(1))

    # Run the service loop
    service.run()

    # Cleanup the service
    service.close()


if __name__ == "__main__":
    main()
