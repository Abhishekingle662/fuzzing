#include "afl-fuzz.h" // Include this first if possible
#include "alloc-inl.h"
#include <zlib.h>   // For CRC32 calculation
#include <stdlib.h>
#include <string.h>
#include <stdint.h> // For uint32_t

// Function to compute CRC32
uint32_t compute_crc32(unsigned char *data, size_t len) {
    return crc32(0L, data, len); // Use 0L for initial value consistency
}

// Custom fuzzing function
size_t afl_custom_fuzz(
    void *data, unsigned char *buf, size_t buf_size,
    unsigned char **out_buf, unsigned char *add_buf,
    size_t add_buf_size, size_t max_size) {

    // Determine a new size (can grow, shrink, or stay the same)
    // This is a simple example: grow by 1-3 bytes like before,
    // but now respecting max_size.
    // A more robust mutator would have more varied strategies.

    size_t mutation_size = (rand() % 3) + 1;
    size_t current_payload_size = (buf_size >= 4) ? buf_size - 4 : 0;
    size_t new_payload_size = current_payload_size + mutation_size;
    size_t new_size = new_payload_size + 4; // +4 for checksum

    // *** FIX: Respect max_size ***
    if (new_size > max_size) {
        // If the intended mutation exceeds max size, fail this attempt.
        // AFL++ will try a different mutation.
        return 0;
    }

    // *** FIX: Use afl_realloc consistently ***
    // Use afl_realloc for ALL allocations/reallocations of *out_buf
    unsigned char *new_buf = afl_realloc((void **)out_buf, new_size);
    if (!new_buf) {
        // Allocation failed, return 0 to indicate failure
        perror("afl_realloc"); // Log error for debugging
        return 0;
    }
    *out_buf = new_buf; // Update the pointer via the double pointer

    // Handle original input size cases
    unsigned char *payload_out = *out_buf + 4;
    uint32_t new_crc32;

    if (buf_size < 4) {
        // If original input was too small, create a minimal valid output.
        // We already allocated new_size (which might be > 4),
        // but we'll treat the payload as empty for CRC calculation.
        memset(payload_out, 0, new_payload_size); // Zero out the payload area
        new_crc32 = compute_crc32(payload_out, new_payload_size); // CRC of zeros

    } else {
        // Original input had at least a potential checksum.
        unsigned char *payload_in = buf + 4;
        size_t original_payload_size = buf_size - 4;

        // Copy original payload data
        // Ensure we don't copy more than exists or more than fits
        size_t copy_size = (original_payload_size < new_payload_size) ? original_payload_size : new_payload_size;
        memcpy(payload_out, payload_in, copy_size);

        // If new buffer is larger, fill the rest somehow (e.g., with random bytes)
        if (new_payload_size > original_payload_size) {
             for (size_t i = original_payload_size; i < new_payload_size; ++i) {
                payload_out[i] = rand() % 256;
             }
        }

        // Choose a random position to mutate within the *new* payload size
        size_t mutation_pos = (new_payload_size > 0) ? (rand() % new_payload_size) : 0;

        // Apply mutation (overwrite random bytes at mutation_pos)
        // Limit mutation application size to avoid going out of bounds
        for (size_t i = 0; i < mutation_size && (mutation_pos + i) < new_payload_size; i++) {
            payload_out[mutation_pos + i] = rand() % 256; // Random byte
        }

        // Compute new CRC32 on the mutated payload data
        new_crc32 = compute_crc32(payload_out, new_payload_size);
    }

    // Store CRC32 in little-endian format at the start
    (*out_buf)[0] = (new_crc32 & 0xFF);
    (*out_buf)[1] = (new_crc32 >> 8) & 0xFF;
    (*out_buf)[2] = (new_crc32 >> 16) & 0xFF;
    (*out_buf)[3] = (new_crc32 >> 24) & 0xFF;

    return new_size; // Return new buffer size
}

// Make sure init and deinit are present
void *afl_custom_init(afl_state_t *afl, unsigned int seed) {
    srand(seed);
    // Return non-NULL pointer on success
    // Using afl->fsrv.dev_urandom_fd as a simple non-NULL value
    // or just return (void*)1 like before.
    return (void*)1;
}

void afl_custom_deinit(void *data) {
    // Cleanup if needed
}