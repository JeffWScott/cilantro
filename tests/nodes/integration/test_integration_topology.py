import unittest
from cilantro.utils.test import MPMasternode, MPTestCase, vmnet_test
from cilantro.constants.testnet import masternodes
from unittest.mock import call
from cilantro.utils.test.god import *
from cilantro.nodes.masternode.masternode import *
import time
from cilantro.protocol import wallet

"""
Here we do integration tests on our network topology. We spin up nodes on the VM, and ensure that they can talk
to each other how we expect them to.
"""

sk1, vk1 = wallet.new()
sk2, vk2 = wallet.new()
sk3, vk3 = wallet.new()
sk4, vk4 = wallet.new()
FILTERS = ['FILTER_' + str(i) for i in range(100)]
URLS = ['tcp://127.0.0.1:' + str(i) for i in range(9000, 9999, 10)]

log = get_logger("TopologyIntegrationTest")


class TopologyIntegrationTest(MPTestCase):

    @vmnet_test
    def test_masternode_receives_std_tx(self):
        """
        Tests that a Masternode properly receives a standard TXs from clients via its POST endpoint
        """
        def config_mn(mn: Masternode):
            assert mn.state == MNRunState, "wtf current state is {}".format(mn.state)

            run_state = mn.states[MNRunState]
            run_state.handle_tx = MagicMock()

            return mn

        def assert_mn(mn: Masternode):
            run_state = mn.states[MNRunState]
            run_state.handle_tx.assert_has_calls([call(tx1), call(tx2)], any_order=True)

        mn_sk = masternodes[0]['sk']

        tx1 = God.create_std_tx(FALCON, DAVIS, 210)
        tx2 = God.create_std_tx(STU, FALCON, 150)

        masternode = MPMasternode(name='Masternode', config_fn=config_mn, assert_fn=assert_mn, sk=mn_sk)
        from cilantro.utils.test import MPComposer
        # comp = MPComposer(sk=mn_sk)

        time.sleep(0.25)  # give masternode a quick sec to get his web server ready

        God.send_tx(tx1)
        God.send_tx(tx2)

        log.critical("STARTING TEST")
        self.start()

    # def test_masternode_witness_pubsub(self):
    #     """
    #     Tests that a Masternode publishes transactions to the witnesses
    #     """
    #     pass


if __name__ == '__main__':
    unittest.main()
