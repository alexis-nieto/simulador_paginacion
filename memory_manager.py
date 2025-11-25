import math
import random

class Process:
    def __init__(self, pid, size, color):
        self.pid = pid
        self.size = size  # in KB
        self.color = color
        self.pages = []  # List of frame indices

    def __repr__(self):
        return f"Process(pid={self.pid}, size={self.size}, color={self.color})"

class MemoryManager:
    def __init__(self, total_memory=4096, page_size=512, os_reserved=1024):
        self.total_memory = total_memory
        self.page_size = page_size
        self.os_reserved = os_reserved
        
        self.num_frames = self.total_memory // self.page_size
        self.frames = [None] * self.num_frames  # None = Free, Process ID = Occupied
        
        # Reserve OS memory
        self.os_frames = math.ceil(self.os_reserved / self.page_size)
        for i in range(self.os_frames):
            self.frames[i] = "OS"
            
        self.processes = {}  # pid -> Process object

    def allocate(self, pid, size, color):
        if pid in self.processes:
            raise ValueError(f"Process {pid} already exists.")
            
        num_pages = math.ceil(size / self.page_size)
        free_indices = [i for i, f in enumerate(self.frames) if f is None]
        
        if len(free_indices) < num_pages:
            raise MemoryError("Not enough memory available.")
            
        # Allocate frames
        selected_frames = free_indices[:num_pages]
        new_process = Process(pid, size, color)
        new_process.pages = selected_frames
        
        for frame_index in selected_frames:
            self.frames[frame_index] = pid
            
        self.processes[pid] = new_process
        return new_process

    def deallocate(self, pid):
        if pid not in self.processes:
            raise ValueError(f"Process {pid} not found.")
            
        process = self.processes[pid]
        for frame_index in process.pages:
            self.frames[frame_index] = None
            
        del self.processes[pid]

    def get_fragmentation_info(self):
        """
        Returns a dictionary with fragmentation details.
        Internal fragmentation is the wasted space in the last page of each process.
        """
        total_internal_fragmentation = 0
        details = {}
        
        for pid, process in self.processes.items():
            # Last page usage
            used_in_last_page = process.size % self.page_size
            if used_in_last_page == 0:
                wasted = 0
            else:
                wasted = self.page_size - used_in_last_page
            
            total_internal_fragmentation += wasted
            details[pid] = wasted
            
        return {
            "total_internal_fragmentation": total_internal_fragmentation,
            "details": details
        }

    def get_memory_status(self):
        return self.frames
