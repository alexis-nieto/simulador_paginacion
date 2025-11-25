from memory_manager import MemoryManager

def test_memory_manager():
    mm = MemoryManager(total_memory=4096, page_size=512, os_reserved=1024)
    
    # Check OS reservation
    # 1024 / 512 = 2 frames
    assert mm.frames[0] == "OS"
    assert mm.frames[1] == "OS"
    assert mm.frames[2] is None
    print("OS Reservation: OK")
    
    # Test Allocation
    # Process 1: 1200 KB -> 3 pages (512 * 3 = 1536)
    p1 = mm.allocate(1, 1200, "red")
    assert len(p1.pages) == 3
    assert mm.frames[2] == 1
    assert mm.frames[3] == 1
    assert mm.frames[4] == 1
    print("Allocation P1: OK")
    
    # Test Fragmentation
    # 1200 KB used. Last page has 1200 - 1024 = 176 KB used.
    # Wasted = 512 - 176 = 336 KB.
    frag = mm.get_fragmentation_info()
    assert frag["total_internal_fragmentation"] == 336
    print("Fragmentation Calculation: OK")
    
    # Test Deallocation
    mm.deallocate(1)
    assert mm.frames[2] is None
    assert 1 not in mm.processes
    print("Deallocation P1: OK")
    
    print("All tests passed!")

if __name__ == "__main__":
    test_memory_manager()
