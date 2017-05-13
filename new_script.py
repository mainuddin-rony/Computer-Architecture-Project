import m5
from m5.objects import *
from caches import *
from optparse import OptionParser


parser = OptionParser()
parser.add_option('--l1i_size', help="L1 instruction cache size")
parser.add_option('--l1i_type', help="L1 instruction cache type")
parser.add_option('--l1d_size', help="L1 data cache size")
parser.add_option('--l1d_type', help="L1 data cache type")
parser.add_option('--l2_size', help="Unified L2 cache size")
parser.add_option('--l2_type', help="Unified L2 cache Type")
parser.add_option('-c', help="Benchmark Program")
parser.add_option('-o', help="Benchmark Program Input")

(options, args) = parser.parse_args()

system = System()

system.clk_domain = SrcClockDomain()
system.clk_domain.clock ='1GHz'
system.clk_domain.voltage_domain = VoltageDomain()

system.mem_mode = 'timing'
system.mem_ranges = [AddrRange('512MB')]

system.cpu = TimingSimpleCPU()

system.cpu.icache = L1ICache(options)
system.cpu.dcache = L1DCache(options)

system.cpu.icache.connectCPU(system.cpu)
system.cpu.dcache.connectCPU(system.cpu)

system.l2bus = L2XBar()

system.cpu.icache.connectBus(system.l2bus)
system.cpu.dcache.connectBus(system.l2bus)

system.l2cache = L2Cache(options)
system.l2cache.connectCPUSideBus(system.l2bus)




system.membus = SystemXBar()


system.l2cache.connectMemSideBus(system.membus)

system.cpu.createInterruptController()
system.cpu.interrupts[0].pio = system.membus.master
system.cpu.interrupts[0].int_master = system.membus.slave
system.cpu.interrupts[0].int_slave = system.membus.master 

system.system_port = system.membus.slave

system.mem_ctrl = DDR3_1600_8x8()
system.mem_ctrl.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.master


process = Process()
# process.cmd = ['tests/benchmarks/blocked-matmul']
process.cmd = [options.c, options.o]
# process.outdir = ['tests/benchmarks/output']
system.cpu.workload = process
system.cpu.createThreads()

root = Root(full_system = False, system = system)
m5.instantiate()

print "Beginning Simulation!"
exit_event = m5.simulate()

print 'Exiting @ tick %i because %s' % (m5.curTick(), exit_event.getCause())

