# pim_core.py

from gem5.components.processors.simple_processor import SimpleProcessor
from gem5.components.processors.cpu_types import CPUTypes
from gem5.isas import ISA
from gem5.resources.resource import obtain_resource
from gem5.components.memory.single_channel import SingleChannelDDR4_2400
from gem5.components.boards.simple_board import SimpleBoard
from gem5.simulate.simulator import Simulator
from gem5.components.cachehierarchies.classic.private_l1_cache_hierarchy import PrivateL1CacheHierarchy


class PIMCore:
    def __init__(self):
        # 创建 PIM Core 使用 AtomicSimpleCPU
        self.pim_cpu = SimpleProcessor(
            cpu_type=CPUTypes.ATOMIC,
            isa=ISA.ARM,
            num_cores=1,
            
        )

    

    def get_pim_cpu(self):
        return self.pim_cpu
processor=PIMCore().get_pim_cpu()

cache_hierarchy = PrivateL1CacheHierarchy(l1d_size="16KiB", l1i_size="16KiB")

memory = SingleChannelDDR4_2400()
    
board = SimpleBoard(
    clk_freq="1GHz",
    processor=processor,
    memory=memory,
    cache_hierarchy=cache_hierarchy,
)
# Set the workload to run the ARM NPB LU benchmark with size S.
board.set_workload(obtain_resource("arm-gapbs-bfs-run"))

# Create a simulator with the board and run it.
simulator = Simulator(board=board)
simulator.run()