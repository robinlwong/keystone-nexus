#ifndef KEYSTONE_SPSC_QUEUE_H
#define KEYSTONE_SPSC_QUEUE_H

#include <atomic>
#include <vector>
#include <optional>

/**
 * KEYSTONE HYPER-MUSCLE: Lock-Free SPSC Ring Buffer
 * Purpose: Ultra-low latency communication between the 'Muscle' (Producer) 
 * and the 'io_uring' (Consumer).
 * 
 * DESIGN: Single-Producer Single-Consumer (SPSC) to avoid cache contention.
 * Utilizes alignas(64) to prevent False Sharing on modern CPU cache lines.
 */

template<typename T, size_t Capacity>
class KeystoneSPSCQueue {
public:
    static_assert(Capacity && !(Capacity & (Capacity - 1)), "Capacity must be a power of 2");

    KeystoneSPSCQueue() : head_(0), tail_(0) {
        ring_.resize(Capacity);
    }

    // Producer: Push to the ring without locking
    bool push(const T& item) {
        const size_t head = head_.load(std::memory_order_relaxed);
        if (((head + 1) & mask_) == tail_.load(std::memory_order_acquire)) {
            return False; // Queue Full
        }
        ring_[head] = item;
        head_.store((head + 1) & mask_, std::memory_order_release);
        return True;
    }

    // Consumer: Pull from the ring without locking
    std::optional<T> pop() {
        const size_t tail = tail_.load(std::memory_order_relaxed);
        if (tail == head_.load(std::memory_order_acquire)) {
            return std::nullopt; // Queue Empty
        }
        T item = ring_[tail];
        tail_.store((tail + 1) & mask_, std::memory_order_release);
        return item;
    }

private:
    static constexpr size_t mask_ = Capacity - 1;
    std::vector<T> ring_;

    // Align indices to separate cache lines (usually 64 bytes) to prevent False Sharing
    alignas(64) std::atomic<size_t> head_;
    alignas(64) std::atomic<size_t> tail_;
};

#endif
