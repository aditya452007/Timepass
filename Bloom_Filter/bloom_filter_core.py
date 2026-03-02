import hashlib

class BloomFilter:
    def __init__(self, bucket_size, hash_count):
        """
        Initializes the Bloom Filter Engine.
        :param bucket_size: The total number of bits (the 'switches') in the filter.
        :param hash_count: The number of hash functions to apply per item.
        """
        self.bucket_size = bucket_size
        self.hash_count = hash_count
        # The bit array containing 0s initially (all switches turned OFF)
        self.bit_array = [0] * bucket_size
        
        # Analytics tracking for the simulation
        self.actual_insertions = 0
        self.hash_collisions = 0

    def _get_hash_indices(self, item):
        """Generates 'hash_count' pseudo-random, deterministic indices for a given item using MD5."""
        indices = []
        for i in range(self.hash_count):
            # We salt the hash with the index 'i' to simulate multiple unique hash functions!
            salt = str(i)
            # Create a non-cryptographic fast hash
            hash_val = hashlib.md5((salt + item).encode('utf-8')).hexdigest()
            # Modulo ensures the resulting number fits within our bit array bounds (0 to bucket_size - 1)
            index = int(hash_val, 16) % self.bucket_size
            indices.append(index)
        return indices

    def add_username(self, username):
        """
        Hashes the username and flips the corresponding bits to 1.
        """
        indices = self._get_hash_indices(username)
        for idx in indices:
            # Track collision if a bit is already flipped to 1 by another user/hash
            if self.bit_array[idx] == 1:
                self.hash_collisions += 1
            # Flip the switch to ON
            self.bit_array[idx] = 1
            
        self.actual_insertions += 1

    def check_username(self, username):
        """
        Checks the bit array to verify if a username might be taken.
        - Returns False: 100% definitively NOT taken.
        - Returns True: Might be taken (could be a False Positive).
        """
        indices = self._get_hash_indices(username)
        for idx in indices:
            # If even a single bit is 0, this username was NEVER added
            if self.bit_array[idx] == 0:
                return False
        # If all bits are 1, it's either in the system, or it's a hash collision (False Positive)
        return True
