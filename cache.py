import math

class CacheSimulator:
    def __init__(self, address_space, block_size, num_blocks, association, replacement_policy):
        # Initialize the cache simulator with the given parameters
        self.address_space = address_space  # Total address space (in bits, e.g., 32 for 2^32 bytes)
        self.block_size = block_size  # Size of a block (in bytes)
        self.num_blocks = num_blocks  # Total number of blocks in the cache
        self.association = association  # Level of associativity (e.g., 2 for 2-way associative)
        self.replacement_policy = replacement_policy  # Replacement policy (LRU, MRU, LOOKAHEAD)
        
        # Create the cache as a list of dictionaries, one for each set
        # The number of sets is determined by num_blocks divided by associativity
        self.cache = [{} for _ in range(self.num_blocks // self.association)]
        
        # Create LRU trackers for each set to track access order
        self.lru_tracker = [{} for _ in range(self.num_blocks // self.association)]
        
        # Counter to track global access order
        self.access_counter = 0

    def parse_address(self, address):
        # Parse the hexadecimal address into tag, index, and block offset
        if address.startswith("x"):
            address = address[1:]  # Remove 'x' prefix if present
        address = int(address, 16)  # Convert the hexadecimal address to an integer

        # Calculate the number of bits for block offset, index, and tag
        block_offset_bits = int(math.log2(self.block_size))  # Number of bits for block offset
        index_bits = int(math.log2(len(self.cache)))  # Number of bits for the index
        tag_bits = self.address_space - index_bits - block_offset_bits  # Remaining bits for the tag

        # Extract block offset, index, and tag using bitwise operations
        block_offset = address & ((1 << block_offset_bits) - 1)
        index = (address >> block_offset_bits) & ((1 << index_bits) - 1)
        tag = (address >> (block_offset_bits + index_bits)) & ((1 << tag_bits) - 1)

        return tag, index, block_offset  # Return the parsed components

    def access_cache(self, tag, index):
        # Access the cache for a given tag and index
        set_cache = self.cache[index]  # Get the cache set for the given index
        set_tracker = self.lru_tracker[index]  # Get the LRU tracker for the set

        if tag in set_cache:
            # If the tag is already in the cache, it's a hit
            self.update_tracker(index, tag)  # Update access tracker
            return "H"  # Hit
        else:
            # If the tag is not in the cache, it's a miss
            if len(set_cache) < self.association:
                # If there is space in the set, add the tag
                set_cache[tag] = self.access_counter
            else:
                # If the set is full, replace an existing entry
                self.replace_entry(index, tag)
            self.update_tracker(index, tag)  # Update access tracker
            return "M"  # Miss

    def update_tracker(self, index, tag):
        # Update the access counter for the given tag in the LRU tracker
        self.access_counter += 1  # Increment global access counter
        self.lru_tracker[index][tag] = self.access_counter  # Update tracker with latest access

    def replace_entry(self, index, tag):
        # Replace a cache entry based on the replacement policy
        if self.replacement_policy == "LRU":
            # Least Recently Used: Replace the entry with the lowest access count
            least_used_tag = min(self.lru_tracker[index], key=self.lru_tracker[index].get)
        elif self.replacement_policy == "MRU":
            # Most Recently Used: Replace the entry with the highest access count
            least_used_tag = max(self.lru_tracker[index], key=self.lru_tracker[index].get)
        elif self.replacement_policy == "LOOKAHEAD":
            # LOOKAHEAD policy: Example placeholder, replace similar to LRU
            least_used_tag = min(self.lru_tracker[index], key=self.lru_tracker[index].get)
        else:
            raise ValueError("Invalid replacement policy")  # Handle invalid policies

        # Remove the least-used entry from the cache and tracker
        del self.cache[index][least_used_tag]
        del self.lru_tracker[index][least_used_tag]
        
        # Add the new tag to the cache and tracker
        self.cache[index][tag] = self.access_counter

    def simulate(self, filename):
        # Simulate cache accesses based on addresses from a file
        with open(filename, "r") as f:
            addresses = f.readlines()  # Read all addresses from the file

        results = []
        for address in addresses:
            address = address.strip()  # Remove any extra whitespace
            tag, index, _ = self.parse_address(address)  # Parse the address
            result = self.access_cache(tag, index)  # Access the cache
            results.append((f"x{index:X}", f"x{tag:X}", result))  # Store the result

        self.display_results(results)  # Display the results

    def display_results(self, results):
        # Display the simulation results in tabular format
        print("Index\tTag\tHit/Miss")
        for index, tag, result in results:
            print(f"{index}\t{tag}\t{result}")  # Print index, tag, and hit/miss result



if __name__ == "__main__":
    # Take user input
    address_space = int(input("Enter the total size of address space (in power of 2, e.g., '32' for 2^32 bytes): "))
    # Example: User sees the guidance in quotes while running the program.

    block_size = int(input("Enter the size of blocks (in power of 2, e.g., '16' for 16 bytes): "))
    # Example: User sees '16' as an example input.

    num_blocks = int(input("Enter the number of blocks (in power of 2, e.g., '64' for 64 blocks): "))
    # Example: '64' is visible to clarify the input format.

    association = int(input("Enter the level of association (e.g., '2' for 2-way associative): "))
    # Example: '2' explains how to specify associativity.

    replacement_policy = input("Enter the replacement policy (LRU/MRU/LOOKAHEAD, e.g., 'LRU'): ")
    # Example: 'LRU' hints at valid replacement policy options.

    filename = input("Enter the filename containing the addresses (e.g., 'addresses.txt'): ")
    # Example: 'addresses.txt' explains the expected format for the file.

    # Initialize and run the simulator
    simulator = CacheSimulator(address_space, block_size, num_blocks, association, replacement_policy)
    simulator.simulate(filename)

