import sys
import time
import psutil
from cirron import Collector

def pytest_runtest_call(item):
    print(f"Running test: {item.nodeid}")
    sys.stdout.flush()  # 强制输出
    item.collector = Collector()
    item.collector.__enter__()  # 启动收集器

    item._start_time = time.perf_counter()  # 记录开始时间
    item._memory_start = psutil.Process().memory_info().rss  # 记录内存使用

def pytest_runtest_teardown(item, nextitem):
    print(f"Tearing down test: {item.nodeid}")
    sys.stdout.flush()  # 强制输出
    try:
        item.collector.__exit__(None, None, None)

        elapsed_time = time.perf_counter() - item._start_time
        memory_end = psutil.Process().memory_info().rss
        memory_used = (memory_end - item._memory_start) / (1024 * 1024)
        counters = item.collector.counters

        print(f"\nPerformance metrics for {item.nodeid}:")
        print(f"Elapsed time: {elapsed_time:.6f} seconds")
        print(f"Memory usage (MB): {memory_used:.6f}")
        print(f"CPU instruction_count={counters.instruction_count}")
        print(f"Branch misses: {counters.branch_misses}")
        print(f"Page faults: {counters.page_faults}")
    except Exception as e:
        print(f"Error during teardown of {item.nodeid}: {e}")



import pytest

#def pytest_collection_modifyitems(session, config, items):
    # 创建基准测试项
    #class BenchmarkTest(pytest.Item):
        #def __init__(self, name, parent):
            #super().__init__(name, parent)

        #def runtest(self):
            #assert 1  # 这里是基准测试内容

        #def reportinfo(self):
            #return self.parent.nodeid, self.name, "Benchmark test"

    # 使用 from_parent 创建基准测试项
    #benchmark_item = BenchmarkTest.from_parent(session, name="benchmark_test")
    #items.insert(0, benchmark_item)





