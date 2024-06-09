import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
import random
import math

class Process:
    def __init__(self, pid, size):
        self.pid = pid
        self.size = size

class MemoryBlock:
    def __init__(self, start, size):
        self.start = start
        self.size = size
        self.free = True
        self.process = None

class BuddyMemoryBlock:
    def __init__(self, start, size):
        self.start = start
        self.size = size
        self.free = True
        self.process = None
        self.buddy = None

class MemoryManagementSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Memory Management Simulator")
        self.root.geometry("800x600")
        self.memory_blocks = []
        self.buddy_memory_blocks = []
        self.processes = []
        self.total_memory = 0
        self.technique = tk.StringVar()
        self.process_size = 50
        self.strategy = tk.StringVar()
        self.process_id_counter = 1
        self.setup_ui()
    
    def setup_ui(self):
        frame = tk.Frame(self.root)
        frame.pack(pady=10)
        
        tk.Label(frame, text="Total Memory Size:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.memory_size_entry = tk.Entry(frame)
        self.memory_size_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(frame, text="Memory Management Technique:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        techniques = ["Fixed-sized Partitioning", "Unequal-sized Partitioning", "Dynamic Allocation", "Buddy System", "Paging"]
        self.technique.set(techniques[0])
        tk.OptionMenu(frame, self.technique, *techniques).grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(frame, text="Allocation Strategy:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        strategies = ["First Fit", "Best Fit", "Worst Fit"]
        self.strategy.set(strategies[0])
        tk.OptionMenu(frame, self.strategy, *strategies).grid(row=2, column=1, padx=5, pady=5)
        
        tk.Button(frame, text="Initialize Memory", command=self.initialize_memory).grid(row=3, column=0, columnspan=2, pady=10)
        
        tk.Label(frame, text="Process Size:").grid(row=4, column=0, padx=5, pady=5, sticky='e')
        self.process_size_entry = tk.Entry(frame)
        self.process_size_entry.grid(row=4, column=1, padx=5, pady=5)
        
        tk.Button(frame, text="Add Process", command=self.add_process).grid(row=5, column=0, padx=5, pady=5)
        
        self.remove_process_menu = tk.OptionMenu(frame, tk.StringVar(), "")
        self.remove_process_menu.grid(row=5, column=1, padx=5, pady=5)
        tk.Button(frame, text="Remove Process", command=self.remove_process).grid(row=5, column=2, padx=5, pady=5)
        self.compact_memory_button = tk.Button(frame, text="Compact Memory", command=self.compact_memory)
        self.compact_memory_button.grid(row=3, column=2, padx=5, pady=5)
        self.compact_memory_button.grid_remove()

        tk.Button(frame, text="Draw Memory Graph", command=self.draw_memory_graph).grid(row=4, column=2, columnspan=2, pady=10)
        self.status_text = tk.Text(self.root, height=50, width=90)
        self.status_text.pack(pady=10)
    
    def initialize_memory(self):
        try:
            self.total_memory = int(self.memory_size_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for total memory size.")
            return
        
        self.memory_blocks = []
        self.buddy_memory_blocks = []
        self.processes = []
        self.process_id_counter = 1
        
        technique = self.technique.get()
        
        if technique == "Fixed-sized Partitioning":
            self.fixed_size_partitioning()
        elif technique == "Unequal-sized Partitioning":
            self.unequal_size_partitioning()
        elif technique == "Dynamic Allocation":
            self.compact_memory_button.grid()
            self.dynamic_allocation()
        elif technique == "Buddy System":
            self.buddy_system()
        elif technique == "Paging":
            self.paging()
        
        self.update_status()
    
    def fixed_size_partitioning(self):
        num_partitions = 10
        block_size = int(self.total_memory / num_partitions)
        self.memory_blocks = [MemoryBlock(i * block_size, block_size) for i in range(num_partitions)]
    
    def unequal_size_partitioning(self):
        num_partitions = 10
        self.memory_blocks = []
        remaining_memory = self.total_memory
        start = 0
        
        # Generate random cut points and sort them
        cut_points = sorted(random.sample(range(1, remaining_memory), num_partitions - 1))
        
        # Calculate partition sizes based on cut points
        partition_sizes = [cut_points[0]] + [cut_points[i] - cut_points[i-1] for i in range(1, len(cut_points))] + [remaining_memory - cut_points[-1]]
        
        for size in partition_sizes:
            self.memory_blocks.append(MemoryBlock(start, size))
            start += size

    def dynamic_allocation(self):
        self.memory_blocks = [MemoryBlock(0, self.total_memory)]
    
    def buddy_system(self):
        self.buddy_memory_blocks = [BuddyMemoryBlock(0, self.total_memory)]
    
    def paging(self):
        self.page_size = 100  # Example page size
        self.pages = [None] * (self.total_memory // self.page_size)
        self.page_table = {}
    
    def add_process(self):
        try:
            process_size = int(self.process_size_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for process size.")
            return
        
        new_process = Process(self.process_id_counter, process_size)
        
        allocated = False
        technique = self.technique.get()
        strategy = self.strategy.get()
        
        if technique in ["Fixed-sized Partitioning", "Unequal-sized Partitioning"]:
            allocated = self.allocate_partitioned_memory(new_process, strategy)
        elif technique == "Dynamic Allocation":
            allocated = self.allocate_dynamic_memory(new_process, strategy)
        elif technique == "Buddy System":
            allocated = self.allocate_buddy_memory(new_process)
        elif technique == "Paging":
            allocated = self.allocate_paging_memory(new_process)
        
        if allocated:
            self.processes.append(new_process)
            self.process_id_counter += 1
        else:
            messagebox.showinfo("Info", f"Process {new_process.pid} could not be allocated memory.")
        
        self.update_status()
    
    def allocate_partitioned_memory(self, new_process, strategy="First Fit"):
        if strategy == "First Fit":
            for block in self.memory_blocks:
                if block.free and block.size >= new_process.size:
                    block.process = new_process
                    block.free = False
                    return True
        elif strategy == "Best Fit":
            best_block = None
            for block in self.memory_blocks:
                if block.free and block.size >= new_process.size:
                    if best_block is None or block.size < best_block.size:
                        best_block = block
            if best_block:
                best_block.process = new_process
                best_block.free = False
                return True
        elif strategy == "Worst Fit":
            worst_block = None
            for block in self.memory_blocks:
                if block.free and block.size >= new_process.size:
                    if worst_block is None or block.size > worst_block.size:
                        worst_block = block
            if worst_block:
                worst_block.process = new_process
                worst_block.free = False
                return True
        return False
    
    def allocate_dynamic_memory(self, new_process, strategy="First Fit"):
        if strategy == "First Fit":
            for block in self.memory_blocks:
                if block.free and block.size >= new_process.size:
                    if block.size > new_process.size:
                        new_block = MemoryBlock(block.start + new_process.size, block.size - new_process.size)
                        self.memory_blocks.append(new_block)
                        block.size = new_process.size
                    block.process = new_process
                    block.free = False
                    self.merge_free_blocks()
                    return True
        elif strategy == "Best Fit":
            best_block = None
            for block in self.memory_blocks:
                if block.free and block.size >= new_process.size:
                    if best_block is None or block.size < best_block.size:
                        best_block = block
            if best_block:
                if best_block.size > new_process.size:
                    new_block = MemoryBlock(best_block.start + new_process.size, best_block.size - new_process.size)
                    self.memory_blocks.append(new_block)
                    best_block.size = new_process.size
                best_block.process = new_process
                best_block.free = False
                self.merge_free_blocks()
                return True
        elif strategy == "Worst Fit":
            worst_block = None
            for block in self.memory_blocks:
                if block.free and block.size >= new_process.size:
                    if worst_block is None or block.size > worst_block.size:
                        worst_block = block
            if worst_block:
                if worst_block.size > new_process.size:
                    new_block = MemoryBlock(worst_block.start + new_process.size, worst_block.size - new_process.size)
                    self.memory_blocks.append(new_block)
                    worst_block.size = new_process.size
                worst_block.process = new_process
                worst_block.free = False
                self.merge_free_blocks()
                return True
        return False
    
    def allocate_buddy_memory(self, new_process):
        block = self.find_buddy_block(new_process.size)
        if block:
            self.split_block(block, new_process.size)
            block.process = new_process
            block.free = False
            return True
        return False
    
    def find_buddy_block(self, size):
        suitable_blocks = [block for block in self.buddy_memory_blocks if block.free and block.size >= size]
        if not suitable_blocks:
            return None
        best_block = min(suitable_blocks, key=lambda block: block.size)
        while best_block.size // 2 >= size:
            best_block = self.split_block(best_block, size)
        return best_block
    
    def split_block(self, block, size):
        while block.size // 2 >= size:
            half_size = block.size // 2
            buddy = BuddyMemoryBlock(block.start + half_size, half_size)
            block.size = half_size
            block.buddy = buddy
            buddy.buddy = block
            self.buddy_memory_blocks.append(buddy)
        return block
     
    def deallocate_buddy_memory(self, process_id):
        for block in self.buddy_memory_blocks:
            if not block.free and block.process and block.process.pid == process_id:
                block.free = True
                block.process = None
                self.merge_block(block)
        # Check if all remaining blocks are free
        free_blocks = [block for block in self.buddy_memory_blocks if block.free]
        if len(free_blocks) == len(self.buddy_memory_blocks):
            self.buddy_memory_blocks = [BuddyMemoryBlock(0, self.total_memory)]

    def merge_block(self, block):
        while block.buddy and block.buddy.free:
            if block.buddy.start < block.start:
                left_block = block.buddy
                right_block = block
            else:
                left_block = block
                right_block = block.buddy

            # Ensure blocks exist in the list before attempting to remove them
            if left_block in self.buddy_memory_blocks and right_block in self.buddy_memory_blocks:
                self.buddy_memory_blocks.remove(left_block)
                self.buddy_memory_blocks.remove(right_block)

                merged_block = BuddyMemoryBlock(left_block.start, left_block.size * 2)
                merged_block.buddy = block.buddy.buddy  # Update buddy reference
                self.buddy_memory_blocks.append(merged_block)

                block = merged_block
            else:
                # If blocks are not found, break the loop
                break

    def allocate_paging_memory(self, new_process):
        pages_needed = math.ceil(new_process.size / self.page_size)
        free_frames = [i for i, frame in enumerate(self.pages) if frame is None]
        
        if len(free_frames) >= pages_needed:
            self.page_table[new_process.pid] = free_frames[:pages_needed]
            for frame in self.page_table[new_process.pid]:
                self.pages[frame] = new_process.pid
            return True
        return False
    
    def compact_memory(self):
        free_blocks = [block for block in self.memory_blocks if block.free]
        if len(free_blocks) < len(self.memory_blocks):
            # Sort memory blocks by start position
            self.memory_blocks.sort(key=lambda block: block.start)
            # Compact memory by moving all allocated blocks to the beginning
            start_position = 0
            new_memory_blocks = []
            for block in self.memory_blocks:
                if not block.free:
                    block.start = start_position
                    start_position += block.size
                    new_memory_blocks.append(block)
            # Calculate accumulated memory left
            accumulated_memory = self.total_memory - sum(block.size for block in new_memory_blocks)
            if accumulated_memory > 0:
                remaining_block = MemoryBlock(start_position, accumulated_memory)
                new_memory_blocks.append(remaining_block)
            self.memory_blocks = new_memory_blocks
            self.update_status()
            messagebox.showinfo("Info", "Memory compacted successfully.")
        else:
            messagebox.showinfo("Info", "No need to compact memory.")

    def remove_process(self):
        process_id = self.selected_process_id.get()
        
        if process_id:
            process_id = int(process_id)
        else:
            messagebox.showerror("Error", "Please select a process ID to remove.")
            return
        
        technique = self.technique.get()
        
        if technique in ["Fixed-sized Partitioning", "Unequal-sized Partitioning", "Dynamic Allocation"]:
            for block in self.memory_blocks:
                if not block.free and block.process.pid == process_id:
                    block.free = True
                    block.process = None
                    if technique == "Dynamic Allocation": 
                        self.merge_free_blocks()
                    break

        elif technique == "Buddy System":
            self.deallocate_buddy_memory(process_id)

        elif technique == "Paging":
            for frame in self.page_table.get(process_id, []):
                self.pages[frame] = None
            if process_id in self.page_table:
                del self.page_table[process_id]
        
        self.processes = [process for process in self.processes if process.pid != process_id]
        self.update_status()
    
    def merge_free_blocks(self):
        self.memory_blocks.sort(key=lambda block: block.start)
        i = 0
        while i < len(self.memory_blocks) - 1:
            current_block = self.memory_blocks[i]
            next_block = self.memory_blocks[i + 1]
            if current_block.free and next_block.free and current_block.start + current_block.size == next_block.start:
                current_block.size += next_block.size
                self.memory_blocks.remove(next_block)
            else:
                i += 1
    
    def update_status(self):
        self.status_text.delete(1.0, tk.END)
        self.status_text.insert(tk.END, "Memory Allocation Status:\n")
        technique = self.technique.get()
        
        if technique == "Paging":
            self.status_text.insert(tk.END, f"Page Table: Page size({self.page_size})\n")
            for pid, frames in self.page_table.items():
                self.status_text.insert(tk.END, f"Process {pid}: Frames {frames}\n")
            self.status_text.insert(tk.END, "\nFrames:\n")
            for i, frame in enumerate(self.pages):
                status = "Free" if frame is None else f"Process {frame}"
                self.status_text.insert(tk.END, f"Frame {i}: {status}\n")

        elif technique == "Buddy System":
            for block in self.buddy_memory_blocks:
                status = "Free" if block.free else f"Process {block.process.pid}, P-size: {block.process.size}"
                self.status_text.insert(tk.END, f"Block: Start: {block.start}, Size: {block.size}, Status: {status}\n")

        else:
            for block in self.memory_blocks:
                status = "Free" if block.free else f"Process {block.process.pid}, P-size: {block.process.size}, Internal-Fragmentation: {block.size - block.process.size}"
                self.status_text.insert(tk.END, f"Block: Start: {block.start}, Size: {block.size}, Status: {status}\n")
        
            self.status_text.insert(tk.END, "\nFragmentation:\n")
            total_internal_fragmentation = 0
            for block in self.memory_blocks:
                if not block.free:
                    internal_fragmentation = block.size - block.process.size
                    total_internal_fragmentation += internal_fragmentation
            
            total_external_fragmentation = sum(block.size for block in self.memory_blocks if block.free)
            self.status_text.insert(tk.END, f"\nTotal external fragmentation: {total_external_fragmentation}\n")
            self.status_text.insert(tk.END, f"Total internal fragmentation: {total_internal_fragmentation}\n")
        
        self.update_process_list()
    
    def update_process_list(self):
        process_ids = [str(process.pid) for process in self.processes]
        self.selected_process_id = tk.StringVar()
        self.remove_process_menu["menu"].delete(0, "end")
        for pid in process_ids:
            self.remove_process_menu["menu"].add_command(label=pid, command=tk._setit(self.selected_process_id, pid))

    def draw_buddy_memory_graph(self):
        plt.figure(figsize=(10, 5))
        plt.title("Buddy System Memory Allocation")
        plt.xlabel("Memory")
        plt.ylabel("")

        # Plotting buddy memory blocks
        for block in self.buddy_memory_blocks:
            if block.free:
                plt.barh(0, block.size, left=block.start, color='black', edgecolor='black')
                plt.text(block.start + block.size / 2, 0, f'Free\nSize: {block.size}', ha='center', va='center', color='white', fontsize=8)
            else:
                process_size = block.process.size
                remaining_size = block.size - process_size
                plt.barh(0, process_size, left=block.start, color='lightgrey', edgecolor='black')
                if remaining_size > 0:
                    plt.barh(0, remaining_size, left=block.start + process_size, color='grey')
                plt.text(block.start + process_size / 2, 0, f'P{block.process.pid}\n({block.process.size})', ha='center', va='center', color='black', fontsize=8)

        # Adding legend
        legend_labels = ['Free Block', 'Process', 'Hole']
        legend_colors = ['black', 'lightgrey', 'grey']
        handles = [plt.Rectangle((0, 0), 1, 1, color=color) for color in legend_colors]
        plt.legend(handles, legend_labels, loc='upper right')

        plt.yticks([])
        plt.xlim(0, self.total_memory)
        plt.ylim(-1, 1)
        plt.show()

    def draw_paging_memory_graph(self):
        plt.figure(figsize=(10, 5))
        plt.title("Paging Memory Allocation")
        plt.xlabel("Memory")
        plt.ylabel("")

        # Plotting pages
        for i, frame in enumerate(self.pages):
            if frame is None:
                plt.barh(0, self.page_size, left=i * self.page_size, color='black', edgecolor='black')
                plt.text(i * self.page_size + self.page_size / 2, 0, 'Free', ha='center', va='center', color='white', fontsize=8)
            else:
                plt.barh(0, self.page_size, left=i * self.page_size, color='lightgrey', edgecolor='black')
                plt.text(i * self.page_size + self.page_size / 2, 0, f'P{frame}', ha='center', va='center', color='black', fontsize=8)

        # Adding legend
        legend_labels = ['Free Frame', 'Process']
        legend_colors = ['black', 'lightgrey']
        handles = [plt.Rectangle((0, 0), 1, 1, color=color) for color in legend_colors]
        plt.legend(handles, legend_labels, loc='upper right')

        plt.yticks([])
        plt.xlim(0, self.total_memory)
        plt.ylim(-1, 1)
        plt.show()

    def draw_memory_graph(self):
        technique = self.technique.get()
        if technique == "Buddy System":
            self.draw_buddy_memory_graph()
        elif technique == "Paging":
            self.draw_paging_memory_graph()
        else:
            # Existing graph code for other techniques
            plt.figure(figsize=(10, 5))
            plt.title("Memory Allocation")
            plt.xlabel("Memory")
            plt.ylabel("")

            # Plotting memory blocks
            for block in self.memory_blocks:
                if block.free:
                    plt.barh(0, block.size, left=block.start, color='black', edgecolor='black')
                    plt.text(block.start + block.size / 2, 0, f'Free\nSize: {block.size}', ha='center', va='center', color='white', fontsize=8)
                else:
                    process_size = block.process.size
                    remaining_size = block.size - process_size
                    plt.barh(0, process_size, left=block.start, color='lightgrey', edgecolor='black')
                    if remaining_size > 0:
                        plt.barh(0, remaining_size, left=block.start + process_size, color='grey')
                    plt.text(block.start + process_size / 2, 0, f'P{block.process.pid}\n({block.process.size})', ha='center', va='center', color='black', fontsize=8)

            # Adding legend
            legend_labels = ['Free Block', 'Process', 'Hole']
            legend_colors = ['black', 'lightgrey', 'grey']
            handles = [plt.Rectangle((0, 0), 1, 1, color=color) for color in legend_colors]
            plt.legend(handles, legend_labels, loc='upper right')

            plt.yticks([])
            plt.xlim(0, self.total_memory)
            plt.ylim(-1, 1)
            plt.show()

if __name__ == "__main__":
    root = tk.Tk()
    app = MemoryManagementSimulator(root)
    root.mainloop()